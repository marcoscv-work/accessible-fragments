# Marketplace storefront: working doc

Everything the Liferay Marketplace publishing wizard asks for, ready to copy and paste. The wizard freezes the listing on submit and keeps no draft, so review this file first. Constraints checked against the wizard (October 2026).

## Profile

| Field | Value |
|---|---|
| App name (≤50) | `Accessible Components for Liferay` (33 characters) |
| Category | Fragments |
| Areas | Content Management & Operations, Experience Management |
| Tags (closed vocabulary) | Low Code |
| Icon | `marketplace/icon-1024.png` (1024×1024 PNG): the Fragments icon (coral rounded square, card, two text lines) with the image placeholder replaced by the universal access pictogram, traced over the official symbol (`brand/universal-access.svg`) |

### Description (≤2000 characters, plain text, the storefront drops line breaks)

Accessible Components is a small set of Liferay's own page fragments, republished where the stock version has an accessibility gap the product does not cover yet. Import the ZIP in Site Builder, Fragments, and the collection appears next to the default ones with the same names and thumbnails. Banner Slider gains a pause and play control, stops while hovered or focused, does not start under reduced motion, hides inactive slides from assistive technology, and gives every indicator a visible focus ring, a 24 px target and a localized label. Accordion keeps its collapsed content out of the tab order and exposes the panel as a labelled region. Dropdown opens by keyboard even in display-on-hover mode, closes with Escape, and no longer announces a menu that is not there. Button gets an Accessible Description read after the visible label, which adds context to a Read More without breaking Label in Name. Card gets a heading level selector. Video gets a title and a captions track in the visitor language, and its Autoplay and Hide Controls options explain their accessibility cost. External Video gets a title on the embedded player, Cookie Banner becomes a labelled landmark, and Social drops its empty title attributes. Every added field sits in an Accessibility section of the fragment configuration, is optional and localizable, and leaves the fragment behaving like the original until an author fills it in. Image alternative text is intentionally not duplicated: the page editor already provides an Image Description for every image. The set shrinks as Liferay absorbs each fix; the Accordion aria-controls fix, for example, already landed in master. It is the companion of Accessibility Scanner for Liferay, which detects the issues these fragments fix. Requirements: Liferay DXP 2026.Q2 or 2026.Q3, a 2023 or later browser for the inert attribute. Source, issues and documentation: https://github.com/marcoscv-work/accessible-fragments

(1948 characters)

## Build

| Field | Value |
|---|---|
| App type | Low-Code Configuration, "Via Liferay Plugin Packages" (its description names fragments explicitly) |
| Package | `dist/accessible-components.zip` from `./build.sh`: the fragment collection in Liferay import format (collection.json, nine fragment folders with fragment.json, index.html, index.css, index.js, configuration.json, thumbnail.png) |
| Install | Site Builder, Fragments, Import. Not a deployable module: nothing goes into the deploy folder |
| Compatible versions | Only the rows marked green in the compatibility matrix below |

## Storefront images (1920×1080 PNG, upload one at a time, in this order)

| # | File | Caption (image description) |
|---|---|---|
| 1 | `storefront/01-fragments-admin.png` | The collection in the Fragments admin, with the same names and thumbnails as the originals |
| 2 | `storefront/02-editor-banner-slider.png` | Banner Slider in the page editor: an Accessibility section with the carousel label, next to the usual options |
| 3 | `storefront/03-editor-button.png` | Button: an Accessible Description that screen readers announce after the visible label |
| 4 | `storefront/04-editor-video.png` | Video: a title, a captions file, and options that explain their accessibility cost |
| 5 | `storefront/05-editor-card.png` | Card: pick the heading level so the card follows the page outline |
| 6 | `storefront/06-slider-controls.png` | The published slider: pause and play control, indicators with a visible focus ring and localized labels |

Regenerate with `scripts/demo-images.mjs` (artwork), `scripts/demo-page.py` (demo page on the local bundle) and `scripts/storefront-shots.mjs`. Video: none for the first version.

## Version

| Field | Value |
|---|---|
| Version | 3.0.0 |
| Release notes | First Marketplace release. Nine fragments that fix gaps the stock versions have: a pausable and keyboard-friendly Banner Slider, inert collapsed content in Accordion, keyboard and Escape handling in Dropdown, an accessible description for Button, a heading level for Card, a title and captions for Video, a title for External Video, a labelled Cookie Banner landmark, and no empty title attributes in Social. Import the ZIP from Site Builder, Fragments. |

## Pricing and licensing

Free, perpetual, no trial (wizard defaults). Source license LGPL 2.1 or later (derived from Liferay's fragments).

## Support

| Field | Value |
|---|---|
| Support URL | https://github.com/marcoscv-work/accessible-fragments/issues |
| Publisher website | https://github.com/marcoscv-work/accessible-fragments |
| Support email (public) | marcos.castro@liferay.com (same as the Scanner) |
| Phone | optional, leave empty |
| EULA URL | leave empty, the Marketplace standard EULA applies |
| Documentation URL | https://github.com/marcoscv-work/accessible-fragments#readme |
| Install and uninstall guide URL | https://github.com/marcoscv-work/accessible-fragments#install |

## Compatibility matrix

Declare only green rows. Each row is a run of `scripts/compat-test.sh` on the official `liferay/dxp` Docker image: sign in, import of the collection, a content page with every fragment, and 17 markup checks on the published page. The page comes from the site-pages API (`scripts/compat-smoke.py`) or, where that API cannot create it, from the real page editor driven with Playwright (`scripts/compat-editor.mjs`). Browser behaviour (slider pause and inert, accordion inert, dropdown keyboard and Escape, captions track) was checked by hand on 2026.Q3 and master. Raw results: `marketplace/compat-<tag>.txt` and `marketplace/compat-editor-<tag>.txt`, one line per run in `marketplace/compatibility.log`.

| Version | Image | Date | Result | Notes |
|---|---|---|---|---|
| 2026.Q3 | `liferay/dxp:2026.q3.6` | 2026-10-14 | **green, 17 of 17** | Browser behaviour verified by hand |
| 2026.Q2 | `liferay/dxp:2026.q2.12` | 2026-10-14 | **green, 17 of 17** | Rendered through the real page editor (`scripts/compat-editor.mjs`): the site-pages API of this release cannot create a page with fragments. `go-to-slide-x` does not exist here, so the indicators use the fragment's English fallback |
| 2026.Q1 LTS and older | | | not tested | The images need a development license key to boot |
| Master | local source build (October 2026) | 2026-10-14 | green | Development reference; page editor path 17 of 17, browser behaviour verified by hand |

## Open items before submitting

- Push the commit and tag `v3.0.0` with the ZIP as release asset, so the documentation and install links resolve to the current README.
- Consent before accepting the Publisher License Agreement and before Submit.
