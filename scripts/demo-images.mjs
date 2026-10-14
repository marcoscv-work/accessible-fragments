/**
 * Generates the placeholder artwork used by the demo page (no text, no faces):
 * three 1920x720 slides and one 960x540 card image.
 *
 *   NODE_PATH=~/projects/liferay-portal/modules/node_modules node scripts/demo-images.mjs
 */
import {createRequire} from 'node:module';
import path from 'node:path';

const require = createRequire(path.join(process.env.NODE_PATH || process.cwd(), 'noop.js'));
const {chromium} = require('playwright');

const out = 'marketplace/demo-assets';
const art = {
	'slide-1': {bg: 'linear-gradient(120deg, #1e3a8a 0%, #2563eb 55%, #60a5fa 100%)', shapes: '<circle cx="1500" cy="200" r="260" fill="#ffffff" fill-opacity="0.12"/><circle cx="1650" cy="520" r="140" fill="#ffffff" fill-opacity="0.18"/><rect x="120" y="500" width="520" height="24" rx="12" fill="#ffffff" fill-opacity="0.35"/>'},
	'slide-2': {bg: 'linear-gradient(120deg, #065f46 0%, #10b981 60%, #a7f3d0 100%)', shapes: '<rect x="1250" y="120" width="420" height="420" rx="80" fill="#ffffff" fill-opacity="0.14" transform="rotate(12 1460 330)"/><circle cx="300" cy="560" r="90" fill="#ffffff" fill-opacity="0.25"/>'},
	'slide-3': {bg: 'linear-gradient(120deg, #7c2d12 0%, #ea580c 55%, #fdba74 100%)', shapes: '<polygon points="1400,80 1800,420 1200,560" fill="#ffffff" fill-opacity="0.14"/><circle cx="1700" cy="160" r="70" fill="#ffffff" fill-opacity="0.3"/>'},
	'card': {bg: 'linear-gradient(135deg, #312e81 0%, #6366f1 60%, #c7d2fe 100%)', shapes: '<circle cx="700" cy="140" r="160" fill="#ffffff" fill-opacity="0.16"/><rect x="80" y="360" width="300" height="20" rx="10" fill="#ffffff" fill-opacity="0.4"/>', h: 540, w: 960},
};
const browser = await chromium.launch();
for (const [name, a] of Object.entries(art)) {
	const w = a.w || 1920, h = a.h || 720;
	const page = await browser.newPage({deviceScaleFactor: 1, viewport: {height: h, width: w}});
	await page.setContent(`<!doctype html><html><body style="margin:0;width:${w}px;height:${h}px;background:${a.bg}"><svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" xmlns="http://www.w3.org/2000/svg">${a.shapes}</svg></body></html>`);
	await page.screenshot({path: `${out}/${name}.jpg`, quality: 85, type: 'jpeg'});
	await page.close();
	console.log('wrote', name);
}
await browser.close();
