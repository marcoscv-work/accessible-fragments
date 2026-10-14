/**
 * Storefront screenshots (1920x1080) from a local portal with the collection
 * imported and the test page created by scripts/compat-smoke.py.
 *
 *   NODE_PATH=~/projects/liferay-portal/modules/node_modules \
 *   LIFERAY_URL=http://localhost:8080 LIFERAY_AUTH=test@liferay.com:test \
 *   SHOT_PAGE=/web/guest/accessible-fragments-test node scripts/storefront-shots.mjs [outDir]
 */
import {createRequire} from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(path.join(process.env.NODE_PATH || process.cwd(), 'noop.js'));
const {chromium} = require('playwright');

const base = process.env.LIFERAY_URL || 'http://localhost:8080';
const [login, password] = (process.env.LIFERAY_AUTH || 'test@liferay.com:test').split(':');
const testPage = process.env.SHOT_PAGE || '/web/guest/accessible-fragments-test';
const out = process.argv[2] || 'marketplace/storefront';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
fs.mkdirSync(out, {recursive: true});

const browser = await chromium.launch();
const context = await browser.newContext({deviceScaleFactor: 1, locale: 'en-US', viewport: {height: 1080, width: 1920}});
const page = await context.newPage();

await page.goto(`${base}/c/portal/login`);
await page.fill('input[name$="_login"]', login);
await page.fill('input[name$="_password"]', password);
await Promise.all([page.waitForNavigation(), page.keyboard.press('Enter')]);

async function closeProductMenu() {
	const open = await page.evaluate(() => document.body.classList.contains('open') || !!document.querySelector('.lfr-product-menu-panel.open'));
	if (open && (await page.$('[data-qa-id="productMenu"]'))) {
		await page.locator('[data-qa-id="productMenu"]').first().click();
		await sleep(1200);
	}
}

async function shot(name) {
	await page.mouse.move(5, 5);
	await sleep(500);
	await page.screenshot({path: `${out}/${name}.png`});
	console.log('shot', name);
}

// 1. The collection in the Fragments admin.
await page.goto(`${base}/group/guest/~/control_panel/manage?p_p_id=com_liferay_fragment_web_portlet_FragmentPortlet`);
await page.waitForLoadState('networkidle');
await sleep(2000);
const collectionLink = page.locator('a:text-is("Accessible Fragments")').first();
if (await collectionLink.count()) {
	await collectionLink.click();
	await page.waitForLoadState('networkidle');
	await sleep(1500);
}
await closeProductMenu();
await shot('01-fragments-admin');

// 2. The page editor with each fragment selected and its Accessibility section open.
await page.goto(`${base}${testPage}?p_l_mode=edit`);
await page.waitForSelector('.page-editor__toolbar', {timeout: 90000});
await sleep(6000);
await closeProductMenu();

let browserPanelOpen = false;

async function selectFragment(itemClass, treeName, name) {
	// The Browser panel (page structure tree) selects a fragment without
	// touching its editables, and shows its configuration on the right.
	if (!browserPanelOpen) {
		await page.locator('button[aria-label="Browser"]').first().click();
		await sleep(1200);
		browserPanelOpen = true;
	}
	const node = page.locator('.page-editor__page-structure__tree-node').filter({hasText: new RegExp(`^${treeName}$`)}).first();
	await node.click({force: true});
	await sleep(1500);
	const el = page.locator(`.page-editor__fragment-content.${itemClass}`).first();
	await el.evaluate((e) => e.scrollIntoView({block: 'start'}));
	await sleep(800);
	// Expand the Accessibility section when it is collapsed.
	const section = page.locator('.page-editor__sidebar__content button:has-text("Accessibility"), .page-editor__sidebar__content .panel-header:has-text("Accessibility")').first();
	if (await section.count() && (await section.getAttribute('aria-expanded')) === 'false') {
		await section.click();
		await sleep(600);
	}
	await shot(name);
}

await selectFragment('lfr-layout-structure-item-banner-slider', 'Banner Slider', '02-editor-banner-slider');
await selectFragment('lfr-layout-structure-item-button', 'Button', '03-editor-button');
await selectFragment('lfr-layout-structure-item-video', 'Video', '04-editor-video');
await selectFragment('lfr-layout-structure-item-card', 'Card', '05-editor-card');

// 3. Visitor view: the slider controls with keyboard focus on the pause button.
await page.goto(`${base}${testPage}`);
await page.waitForSelector('.carousel-toggle-button', {timeout: 60000});
await sleep(1500);
await page.evaluate(() => document.querySelector('.section-slider').scrollIntoView({block: 'start'}));
await sleep(500);
await page.focus('.carousel-toggle-button');
await sleep(300);
await shot('06-slider-controls');

await browser.close();
