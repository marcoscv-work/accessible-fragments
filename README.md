# Accessible Fragments

Accessible versions of Liferay's out-of-the-box page fragments, packaged as a single, importable **fragment collection**.

Every fragment in Liferay's default sets (Basic Components, Form Components, Navigation Bars, Footers, and more) is reproduced here with **opt-in accessibility options** added to its configuration: alternative text for images, ARIA labels for icon and action controls, semantic roles for landmarks and disclosures, and fixes for a couple of latent ARIA bugs. Nothing is forced on the markup. Fields start empty or off, so a fragment behaves exactly like the original until an author fills in the accessible name that only they know the right value for.

This mirrors Liferay's supported, low-code approach to accessibility: rather than baking a fixed ARIA strategy into every out-of-the-box fragment (which is noise for one site and wrong for another), copy the fragment and expose the attributes so each site can meet WCAG in the way that fits its content.

## Install

1. Download `dist/accessible-components.zip` from this repository (or from the latest [Release](https://github.com/marcoscv-work/accessible-fragments/releases)).
2. In Liferay, open **Site Builder and then Fragments** (or **Fragments** under a global scope).
3. Click **Import**, choose the ZIP, and confirm.

The collection **Accessible Components** appears in the fragment list and in the page editor sidebar, ready to drop onto any Content Page.

## Use

Select a fragment on the page, open the **Configuration** tab, and look for the **Accessibility** section:

- **Image**, **Card**, **Social**, **Header**, **Footer**: an **Image Description** field sets the image `alt`. Leave it empty for purely decorative images (an empty `alt` is the correct, screen-reader-silent default).
- **Button**: an **ARIA Label** field sets an accessible name, which is essential for icon-only or otherwise ambiguous buttons and links.
- **Cookie Banner**: an **ARIA Label** field names the consent region so assistive technology announces it as a landmark.

All fields are localizable, so translations follow the page's language.

## What changed per fragment

| Fragment(s) | Accessibility improvement |
|---|---|
| Image, Card | Configurable `alt` via an **Image Description** field |
| Social | Per-icon **Image Description** fields; removed empty `title` attributes |
| Header Dark/Light, Footer Nav Dark/Light | The hard-coded logo `alt` is now an editable **Image Description** field |
| Button | **ARIA Label** applied to both the action button and the link variant |
| Spacer | Marked `aria-hidden` so the purely visual gap is skipped by screen readers |
| Dropdown | Fixed a broken `aria-labelledby` that pointed at a non-existent element |
| Accordion | Fixed `aria-controls` (it targeted the title, not the panel) and gave the panel `role="region"` with a label |
| Cookie Banner | Added `role="region"` with a configurable label |
| Banner Slider | Added carousel and slide `aria-roledescription` semantics |
| Slider, Tabs, and the form inputs | Already fully accessible in Liferay, included unchanged |

Free-text values are HTML-escaped before they reach an attribute, so authored text cannot break the markup.

## Rebuild the ZIP

The source of truth is `src/accessible-components/`. To regenerate the importable ZIP after editing a fragment:

```bash
./build.sh
```

This writes `dist/accessible-components.zip`. It needs only a shell and `zip`.

You can also manage the collection with the [Liferay Fragments Toolkit](https://github.com/liferay/liferay-js-toolkit). From the repository root, push straight into a running Liferay instance without a manual import:

```bash
npx -p generator-liferay-fragments liferay-fragments import
```

## Layout

```
src/
  accessible-components/
    collection.json            Collection name and description
    <fragment>/
      fragment.json            Import metadata (name, type, asset paths)
      index.html               FreeMarker template
      index.css                Styles
      index.js                 Behavior
      configuration.json       Configuration fields (incl. the Accessibility options)
```

## Compatibility

Built from the fragments shipped with Liferay DXP / Portal (7.4 and later). The fragments rely only on standard fragment features (editable elements, configuration fields, FreeMarker, and the `htmlUtil` and `languageUtil` helpers), so they import into any site on a compatible version.
