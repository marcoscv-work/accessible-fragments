# Accessible Fragments

A curated collection of Liferay's out-of-the-box page fragments, re-published with **accessibility value added**. It is intentionally **not** a full copy of the default fragments. It contains only the ones where a concrete, effective accessibility improvement was possible over what Liferay already ships.

Every fragment here does one of three things the stock fragment does not:

- exposes a configurable **accessible name** (alternative text for images, an ARIA label for controls, a title for embedded media),
- adds **semantic structure** (a labelled landmark region, carousel and slide semantics), or
- **fixes a latent ARIA bug** in the original markup.

Fragments that Liferay already ships fully accessible are deliberately excluded: the form inputs (combobox and listbox patterns, label association, `role="alert"` errors, `autocomplete`), the main Slider and Tabs, and the Heading level selector. So are fragments with no accessible content to configure, such as Paragraph, HTML, Spacer, and Separator. Keeping the set small is the point. Every fragment in it earns its place.

## What is inside (14 fragments)

| Fragment | Accessibility value over the out-of-the-box version |
|---|---|
| Image, Card | An **Image Description** field drives the image `alt` (WCAG 1.1.1) |
| Social | An **Image Description** per icon, and removal of empty `title` attributes |
| Header Dark / Light, Footer Nav Dark / Light | The hard-coded logo `alt` becomes an editable **Image Description** |
| Button | An **ARIA Label** for icon-only or ambiguous buttons and links (WCAG 4.1.2) |
| Video | A **Video Title** sets an accessible name on the `<video>` element and the YouTube player iframe (WCAG 4.1.2) |
| External Video | A **Video Title** sets a `title` on the embedded provider iframe (WCAG 4.1.2, 2.4.1) |
| Cookie Banner | A labelled `role="region"` makes the consent banner a discoverable landmark |
| Dropdown | Fixes an `aria-labelledby` that pointed at a non-existent element |
| Accordion | Fixes `aria-controls` (it targeted the title, not the collapsible panel) and gives the panel `role="region"` with a label |
| Banner Slider | Adds carousel and slide `aria-roledescription` semantics |

All added fields sit under an **Accessibility** section in the fragment's configuration. They are optional, localizable, and empty or off by default, so a fragment behaves exactly like the original until an author supplies the value only they know. Free-text values are HTML-escaped before they reach an attribute.

## Install

1. Download `dist/accessible-components.zip` from this repository (or from the latest [Release](https://github.com/marcoscv-work/accessible-fragments/releases)).
2. In Liferay, open **Site Builder and then Fragments** (or **Fragments** at a global scope).
3. Click **Import**, choose the ZIP, and confirm.

The collection **Accessible Components** appears in the fragment list and in the page editor sidebar.

## Use

Select a fragment on the page, open the **Configuration** tab, and fill in the **Accessibility** section. For example, set an **Image Description** on an Image, an **ARIA Label** on an icon Button, or a **Video Title** on a Video. Leave an image description empty for purely decorative images, where an empty `alt` is the correct, screen-reader-silent default.

## Rebuild the ZIP

The source of truth is `src/accessible-components/`. To regenerate the importable ZIP after editing a fragment:

```bash
./build.sh
```

This writes `dist/accessible-components.zip` and needs only a shell and `zip`.

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
