# Accessible Fragments

A curated collection of Liferay's out-of-the-box page fragments, re-published with **accessibility value added**. It is intentionally **not** a full copy of the default fragments. It contains only the ones where a concrete accessibility improvement was possible over what Liferay already ships, and it drops a fragment as soon as the product covers the gap.

Every fragment here does one of three things the stock fragment does not:

- fixes a **keyboard or screen reader behaviour** (pausable rotation, collapsed content kept out of the tab order, keyboard access to hover menus, Escape to close),
- exposes a **configurable accessible name, description, or captions** for things only the author knows (a video title, a captions file, a landmark label, extra context for a button), or
- adds **semantic structure** (a heading level, a labelled region, carousel and slide semantics).

Fragments that Liferay already ships fully accessible are deliberately excluded: the form inputs, the main Slider and Tabs, and the Heading fragment. So are fragments with no accessible content to configure, such as Paragraph, HTML, Spacer, and Separator.

Image alternative text is also excluded on purpose. The page editor already offers an **Image Description** field for every image editable, in the selection panel of the image, localized, and rendered as the `alt` attribute. That covers Image, Card images, Social icons, and the Header and Footer logos. Use that field; this set does not duplicate it.

## What is inside (9 fragments)

| Fragment | Accessibility value over the out-of-the-box version |
|---|---|
| Banner Slider | A **pause and play control** so the rotation can be stopped (WCAG 2.2.2), rotation paused while hovered or focused, and not started at all under `prefers-reduced-motion`. Inactive slides are hidden from assistive technology and removed from the tab order with `inert`. Indicators get a visible focus ring, a 24 px target (2.5.8), a localized **Go to slide** label and `aria-current`. Slides are named by their title, the container has `aria-roledescription="carousel"` plus an optional **ARIA Label**, and `aria-live` switches to polite while stopped. |
| Accordion | The collapsed panel is `inert`, so its links no longer sit in the tab order while hidden (2.4.3). The panel is a labelled `role="region"` and the toggle points at it with `aria-controls` (Liferay fixed the latter in master in August 2026). |
| Dropdown | Fixes an `aria-labelledby` that pointed at a non-existent element. With **Display on Hover** the menu can also be opened by click or keyboard, and it closes when focus leaves it. **Escape** closes the menu in every mode and returns focus to the toggle. The misleading `aria-haspopup` (there is no menu role inside) is removed. |
| Button | An **Accessible Description** rendered as visually hidden text linked with `aria-describedby`. Screen readers announce it after the visible label, so "Read more" can say what it opens without breaking Label in Name (2.5.3), which a replacement `aria-label` would. |
| Card | A **Heading Level** selector for the card title, which was a fixed `h2` (1.3.1, 2.4.6). |
| Video | A **Video Title** sets an accessible name on the `<video>` element and the YouTube player iframe (4.1.2), a **Captions URL** adds a WebVTT captions track in the current language (1.2.2), and the Autoplay and Hide Controls options explain their accessibility cost. |
| External Video | A **Video Title** sets a `title` on the embedded provider iframe (4.1.2, 2.4.1). |
| Cookie Banner | A labelled `role="region"` makes the consent banner a discoverable landmark. |
| Social | Removes the empty `title=""` attributes that produced empty tooltips and announcements. |

All added fields sit under an **Accessibility** section in the fragment's configuration. They are optional, localizable, and empty by default, so a fragment behaves like the original until an author supplies the value only they know. Free-text values are HTML-escaped before they reach an attribute. Labels reuse Liferay's own language keys where one exists.

## Install

1. Download `dist/accessible-fragments.zip` from this repository (or from the latest [Release](https://github.com/marcoscv-work/accessible-fragments/releases)).
2. In Liferay, open **Site Builder and then Fragments** (or **Fragments** at a global scope).
3. Click **Import**, choose the ZIP, and confirm.

The collection **Accessible Fragments** appears in the fragment list and in the page editor sidebar, with the same thumbnails as the originals. The fragments keep their original names, so you will see two "Button" entries in the sidebar: the one under **Accessible Fragments** is this one.

## Use

Select a fragment on the page, open the **Configuration** tab, and fill in the **Accessibility** section. For example, set a **Video Title** and a **Captions URL** on a Video, pick the **Heading Level** on a Card, or add an **Accessible Description** to a Button. For image alternative text, select the image itself and use the editor's **Image Description** field.

## Rebuild the ZIP

The source of truth is `src/accessible-components/`. To regenerate the importable ZIP after editing a fragment:

```bash
./build.sh
```

This writes `dist/accessible-fragments.zip` and needs only a shell and `zip`.

You can also manage the collection with the [Liferay Fragments Toolkit](https://github.com/liferay/liferay-js-toolkit). From the repository root, push straight into a running Liferay instance without a manual import:

```bash
npx -p generator-liferay-fragments liferay-fragments import
```

## Layout

The folder `src/accessible-components/` keeps its original name on purpose: Liferay uses it as the collection key, so importing a new version overwrites the collection instead of creating a second one.

```
src/
  accessible-components/
    collection.json            Collection name and description
    <fragment>/
      fragment.json            Import metadata (name, type, icon, cacheable, asset paths)
      index.html               FreeMarker template
      index.css                Styles
      index.js                 Behavior
      configuration.json       Configuration fields (incl. the Accessibility options)
      thumbnail.png            Sidebar preview (same as the original fragment)
```

## Compatibility

Built from the fragments shipped with Liferay DXP / Portal 7.4 and later. The fragments rely only on standard fragment features (editable elements, configuration fields, FreeMarker, and the `htmlUtil` and `languageUtil` helpers). The `inert` attribute needs a browser from 2023 or later; older browsers simply ignore it.

Tested on the official Docker images of **2026.Q2** and **2026.Q3** (import, a page with every fragment, and 17 checks on the published markup) and on a master build. The scripts live in `scripts/`: `compat-test.sh <tag>` boots the image and runs `compat-smoke.py`, or `compat-editor.mjs` on releases whose page API cannot create pages with fragments. Results are kept in `marketplace/`.

## License

The fragments derive from Liferay's own, which are published under the LGPL 2.1 or later. This collection keeps that license. See `LICENSE`.
