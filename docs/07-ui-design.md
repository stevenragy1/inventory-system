# 07 · UI design

## Goal

Make the user interface match the design made in Figma, and keep it responsive at phone, tablet, and desktop widths.

## Design source

The design is the Figma file "web-design". It contains:

| Frame | Width | Status |
|---|---|---|
| Dashboard (Neumorphic Edition) | 1280 px | Applied |
| Items (Neumorphic Edition) | 1280 px | Applied |
| Stock updates (Neumorphic Edition) | 1280 px | Applied |
| Search (Neumorphic Edition) | 1280 px | Applied |
| Reports (Cyan & Parchment Neumorphic) | 1280 px | Applied, with the theme's brighter teal |
| Dashboard (Mobile Neumorphic) | 390 px | Used for reference; full layout not yet matched |
| Items (Mobile Neumorphic) | 390 px | Used for reference; full layout not yet matched |
| Stock updates (phone) | — | Not in the file yet |
| Search (phone) | — | Not in the file yet |
| Reports (phone) | — | Not in the file yet |

## Visual system

The design uses a soft, "neumorphic" style: raised and pressed-in surfaces on a warm beige background.

| Token | Value | Used for |
|---|---|---|
| Background | `#ede4e0` | Page and raised surfaces |
| Surface | `#f4edea` | Inset fields and table wells |
| Text | `#12263a` | Headings and body text |
| Muted text | `#6c7a87` | Labels, table headers, hints |
| Teal | `#26cbd1` | In-stock status, focus ring, accents |
| Orange | `#d97b28` | Low-stock status |
| Red | `#d9383a` | Negative levels, destructive actions |
| Font | Plus Jakarta Sans | All text |

Raised surfaces (cards, buttons, dialogs) use a light shadow from the top left and a darker one from the bottom right. Inputs and tables are pressed in using an inset shadow.

## Implementation

- Tokens are defined once, as CSS variables, in `frontend/src/theme.css`.
- The theme loads after Bootstrap, so it overrides Bootstrap's defaults without changing any page's markup.
- The font loads from Google Fonts in `frontend/index.html`.
- Status badges use the palette: teal for in stock, orange for low, grey for out, red for negative. Each badge also has a text label, so status does not depend on colour alone.

## Accuracy against the design

- **Colours, font, shadows, and corner radii:** taken from the Figma frames' values.
- **Layout and spacing:** the pages keep their existing structure and use Bootstrap's grid. They do not yet match the exact Figma positions.
- **Icons:** the Figma icons are image files that could not be downloaded during the build, so no icons are shown.
- **Reports accent:** the Reports frame uses a deeper teal (`#00696d`). The app uses the brighter teal across all screens, so the whole app stays consistent. This was a deliberate choice.

## Responsive behaviour

- Bootstrap's grid stacks cards and charts on phones and places them side by side on desktop.
- Tables scroll sideways inside their own box, so the page itself never scrolls sideways.
- Dialogs fill most of a phone screen, and their buttons stay within reach.

The mobile frames show the intended phone layouts. Matching them exactly needs the mobile frames for Stock updates, Search, and Reports to be added to the Figma file, and then a layout pass over each phone frame.

## Originality

- The theme values come from the team's own Figma file. The palette, font, and shadows were read from the design and written as CSS variables.
- The React components, tests, and documentation were written for this project.
- No Figma-generated code was copied into the project. The project was scanned for Figma asset links and generated class names, and none were found.
- The only third-party code is the open-source libraries listed in `frontend/package.json` and `backend/requirements.txt`, used under their own licences.
- An external plagiarism database was not run. Submit the project through your institution's checker if one is required.
