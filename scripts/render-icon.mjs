/**
 * Renders brand/logo-mark.svg to marketplace/icon-1024.png.
 *
 *   NODE_PATH=~/projects/liferay-portal/modules/node_modules node scripts/render-icon.mjs
 */
import {createRequire} from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(path.join(process.env.NODE_PATH || process.cwd(), 'noop.js'));
const {chromium} = require('playwright');

const browser = await chromium.launch();
const page = await browser.newPage({deviceScaleFactor: 1, viewport: {height: 1024, width: 1024}});
const svg = fs.readFileSync(path.resolve('brand/logo-mark.svg'), 'utf8').replace('<svg ', '<svg width="1024" height="1024" ');
await page.setContent(`<!doctype html><html><body style="margin:0;background:transparent">${svg}</body></html>`);
await page.screenshot({omitBackground: true, path: path.resolve('marketplace/icon-1024.png')});
await browser.close();
console.log('wrote marketplace/icon-1024.png');
