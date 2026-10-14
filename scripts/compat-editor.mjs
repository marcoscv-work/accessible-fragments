/**
 * Render check through the real page editor, for portal versions where the
 * site-pages API cannot create a page with fragments (2026.Q2 and older).
 * Creates a content page, adds every fragment of the imported collection
 * from the Components panel, publishes, and checks the published markup.
 *
 *   NODE_PATH=~/projects/liferay-portal/modules/node_modules \
 *   LIFERAY_URL=http://localhost:8082 LIFERAY_AUTH=test@liferay.com:password \
 *   node scripts/compat-editor.mjs
 */
import {createRequire} from 'node:module';
import path from 'node:path';

const require = createRequire(path.join(process.env.NODE_PATH || process.cwd(), 'noop.js'));
const {chromium} = require('playwright');

const base = process.env.LIFERAY_URL || 'http://localhost:8080';
const [login, password] = (process.env.LIFERAY_AUTH || 'test@liferay.com:test').split(':');
const FRAGMENTS = ['Banner Slider', 'Accordion', 'Dropdown', 'Button', 'Card', 'Cookie Banner', 'Social', 'Video', 'External Video'];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const results = [];
const report = (ok, name, detail = '') => {
	results.push(ok);
	console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail ? ': ' + detail : ''));
};

const browser = await chromium.launch();
const context = await browser.newContext({locale: 'en-US', viewport: {height: 1080, width: 1920}});
const page = await context.newPage();

await page.goto(`${base}/c/portal/login`);
await page.fill('input[name$="_login"]', login);
await page.fill('input[name$="_password"]', password);
await Promise.all([page.waitForNavigation(), page.keyboard.press('Enter')]);
if (/update_password/.test(page.url())) {
	await page.fill('input[name$="password1"]', 'Compat-test-2026!');
	await page.fill('input[name$="password2"]', 'Compat-test-2026!');
	await page.locator('input[name$="password2"]').press('Enter');
	await page.waitForURL((url) => !/update_password/.test(url.href), {timeout: 60000});
}
await page.goto(`${base}/web/guest`);
const signedIn = await page.evaluate(() => Liferay.ThemeDisplay.isSignedIn());
report(signedIn, 'session login');
if (!signedIn) {
	process.exit(1);
}

// A fresh content page through the Pages admin "Add Page" form, which also
// creates the draft the editor needs (the headless page API cannot do this on
// 2026.Q2). The form is fetched first so its action URL and tokens are exact.
const url = `ac-editor-${Date.now()}`;
const created = await page.evaluate(async (url) => {
	const ns = '_com_liferay_layout_admin_web_portlet_GroupPagesPortlet_';
	const groupId = Liferay.ThemeDisplay.getScopeGroupId();
	const render = `/group/guest/~/control_panel/manage?p_p_id=com_liferay_layout_admin_web_portlet_GroupPagesPortlet&p_p_lifecycle=0&p_p_state=pop_up&${ns}mvcRenderCommandName=%2Flayout_admin%2Fadd_layout&${ns}type=content&${ns}groupId=${groupId}&${ns}privateLayout=false&${ns}parentLayoutId=0&${ns}layoutPageTemplateEntryId=0`;
	const html = await (await fetch(render)).text();
	const doc = new DOMParser().parseFromString(html, 'text/html');
	const form = doc.querySelector('form.add-layout-form');
	if (!form) {
		return {error: 'add page form not found'};
	}
	const body = new URLSearchParams();
	for (const input of form.querySelectorAll('input[name]')) {
		body.set(input.name, input.value);
	}
	body.set(ns + 'name', url);
	const action = new URL(form.getAttribute('action'), location.origin);
	action.searchParams.set('p_auth', Liferay.authToken);
	const r = await fetch(action.toString(), {body, headers: {'x-csrf-token': Liferay.authToken}, method: 'POST'});
	const text = await r.text();
	try {
		return JSON.parse(text);
	}
	catch (error) {
		return {raw: text.slice(0, 300), status: r.status};
	}
}, url);
report(!!created.redirectURL, 'create content page', created.redirectURL ? 'draft opened in the editor' : JSON.stringify(created).slice(0, 200));
if (!created.redirectURL) {
	process.exit(1);
}

await page.goto(created.redirectURL);
await page.waitForSelector('.page-editor__toolbar', {timeout: 120000});
await sleep(5000);
// Some releases greet a new page with a modal (tips, onboarding); close it.
for (let i = 0; i < 3 && (await page.locator('.modal.show').count()); i++) {
	const text = (await page.locator('.modal.show').first().innerText()).trim().slice(0, 80).replace(/\s+/g, ' ');
	console.log('  closing modal:', text);
	const close = page.locator('.modal.show button[aria-label="Close"], .modal.show .close').first();
	if (await close.count()) {
		await close.click({force: true});
	}
	else {
		await page.keyboard.press('Escape');
	}
	await sleep(1000);
}

const components = page.locator('button[aria-label="Components"]').first();
if ((await components.count()) && (await page.locator('.page-editor__sidebar__content:has-text("Fragments")').count()) === 0) {
	await components.click();
	await sleep(1000);
}
const header = page.locator('.page-editor__sidebar__content button.panel-header').filter({hasText: /^Accessible Fragments$/}).first();
report(await header.count() > 0, 'collection listed in the Components panel');
if ((await header.getAttribute('aria-expanded')) === 'false') {
	await header.click();
	await sleep(1000);
}
const section = header.locator('xpath=following-sibling::*[1]');
let added = 0;
// Each card is dropped on the top edge of the first fragment (a sibling insert,
// never inside an Accordion or Dropdown drop zone), so the list runs backwards.
for (const name of [...FRAGMENTS].reverse()) {
	const card = section.locator(`button[aria-label="Add ${name}"]`).first();
	if (!(await card.count())) {
		console.log('  no card for', name);
		continue;
	}
	await card.scrollIntoViewIfNeeded().catch(() => {});
	const from = await card.boundingBox();
	// Drop after the last fragment on the canvas, or on the empty root drop zone.
	const toppers = page.locator('.page-editor__root .page-editor__topper');
	let target;
	if (await toppers.count()) {
		const first = await toppers.first().boundingBox();
		target = {x: first.x + first.width / 2, y: first.y + 3};
	}
	else {
		const root = await page.locator('.page-editor__root').first().boundingBox();
		target = {x: root.x + root.width / 2, y: root.y + Math.min(root.height / 2, 200)};
	}
	await page.mouse.move(from.x + from.width / 2, from.y + from.height / 2);
	await page.mouse.down();
	await page.mouse.move(from.x + from.width / 2 + 10, from.y + from.height / 2 + 10, {steps: 4});
	await page.mouse.move(target.x, target.y - 40, {steps: 12});
	await page.mouse.move(target.x, target.y, {steps: 8});
	await sleep(400);
	await page.mouse.up();
	await sleep(2500);
	const names = await page.evaluate(() => [...document.querySelectorAll('.page-editor__topper')].map((e) => e.dataset.name).filter(Boolean));
	if (names.includes(name)) {
		added++;
	}
	else {
		console.log('  drop did not add', name);
	}
}
report(added === FRAGMENTS.length, 'fragments added from the collection', `${added} of ${FRAGMENTS.length}`);
const onCanvas = await page.evaluate(() => [...document.querySelectorAll('.page-editor__topper')].map((e) => e.dataset.name).filter(Boolean));
console.log('  on canvas before publish:', JSON.stringify(onCanvas));

await page.locator('.page-editor__toolbar button:has-text("Publish")').first().click();
await sleep(2000);
const confirm = page.locator('.modal button:has-text("Publish")').first();
if (await confirm.count()) {
	await confirm.click();
}
await page.waitForURL((u) => !/p_l_mode=edit/.test(u.href), {timeout: 60000}).catch(() => {});
await sleep(3000);
console.log('  after publish:', page.url());

// The published page, located through JSON-WS so the friendly URL is not guessed.
await page.goto(`${base}/web/guest`);
const published = await page.evaluate(async (url) => {
	const body = new URLSearchParams({groupId: Liferay.ThemeDisplay.getScopeGroupId(), p_auth: Liferay.authToken, privateLayout: 'false'});
	const r = await fetch('/api/jsonws/layout/get-layouts', {body, headers: {'x-csrf-token': Liferay.authToken}, method: 'POST'});
	const layouts = await r.json();
	const layout = (Array.isArray(layouts) ? layouts : []).find((l) => (l.nameCurrentValue || l.name || '').includes(url));
	return layout ? {friendlyURL: layout.friendlyURL, plid: layout.plid} : {count: Array.isArray(layouts) ? layouts.length : -1};
}, url);
report(!!published.plid, 'page published', published.plid ? `plid ${published.plid} ${published.friendlyURL}` : JSON.stringify(published));
const response = await context.request.get(`${base}/web/guest${published.friendlyURL || '/' + url}`);
const html = await response.text();
console.log('  published page HTTP', response.status(), 'fragments', (html.match(/lfr-layout-structure-item-(?:banner-slider|accordion|dropdown|button|card|cookie-banner-simple|social|video|external-video)\b/g) || []).length);
const has = (name, pattern, count) => {
	const found = html.match(new RegExp(pattern, 'gs')) || [];
	report(count === undefined ? found.length > 0 : found.length === count, name, `${found.length} match(es)`);
};
has('carousel container', '<div[^>]*aria-roledescription="carousel"[^>]*role="group"');
has('inactive slides inert', '<div[^>]*aria-hidden="true" inert [^>]*aria-roledescription="slide"', 2);
has('slides named by title', 'aria-labelledby="[^"]*-slide-title-0[123]"', 3);
has('pause and play labels localized', 'data-label-pause="Pause" data-label-play="Play"');
has('indicator labels and aria-current', '<button[^>]*aria-current="(true|false)" aria-label="Go to Slide [123]"', 3);
has('accordion region', '<div[^>]*aria-labelledby="accordion-title-[^"]+"[^>]*id="accordion-panel-[^"]+" role="region"');
has('dropdown labelledby fixed', '<div aria-labelledby="dropdown-fragment-([^"]+)"[^>]*id="\\1-dropdown-fragment-menu"');
has('dropdown without aria-haspopup', 'dropdown-fragment-toggle[^>]*aria-haspopup', 0);
has('card default heading level', '<h2>\\s*<span[^>]*data-lfr-editable-id="02-title"');
has('cookie banner region', '<div aria-label="Cookie consent" class="cookie-banner[^"]*" role="region">');
has('social without empty titles', 'component-social[\\s\\S]*?title=""', 0);
has('no FreeMarker errors', 'FreeMarker template error|freemarker\\.core', 0);

console.log(`\n${results.filter(Boolean).length} of ${results.length} checks passed; page ${base}/web/guest/${url}`);
if (!process.env.KEEP_PAGE && published.plid) {
	const deleted = await page.evaluate(async (plid) => {
		const body = new URLSearchParams({p_auth: Liferay.authToken, plid});
		const r = await fetch('/api/jsonws/layout/delete-layout', {body, headers: {'x-csrf-token': Liferay.authToken}, method: 'POST'});
		return r.status;
	}, String(published.plid));
	console.log('test page deleted:', deleted);
}
await browser.close();
process.exit(results.every(Boolean) ? 0 : 1);
