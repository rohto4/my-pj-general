# Cozy UI System

## Information before atmosphere

Create a checklist of all metrics, summaries, rows, statuses, links, filters, actions, and editable fields. Every theme must render the checklist from the same source.

Decorative layers use `pointer-events: none`, low contrast, and reserved space. They never cover data.

## Structural vocabulary

Prefer shelf rules, book-spine stripes, window mullions, archive labels, woven patterns, editorial folios, marginal notes, large color fields, thin dividers, and asymmetrical whitespace around a strict data grid.

Avoid a rounded rectangle around every group, identical shadows on every surface, blurred glass as the default hierarchy, emoji as primary product icons, and decorative photos behind text.

## Radius budget

| Element | Radius |
| --- | --- |
| page region, panel, table, drawer | 0 |
| list row, summary item, input, select | 0-2px |
| primary button | 0-2px |
| compact status badge | 0-2px |
| plant leaf, lamp glow, status dot | organic or circular |

If more than 15 percent of visible rectangular controls use a radius over 2px, fail the review.

## Narrow viewport composition

At approximately 1180-1366 CSS px:

1. Reduce the fixed navigation width before reducing text size.
2. Keep paired summaries in two equal columns with `align-items: stretch`.
3. Give repeated list groups equal row counts or a shared minimum block height so their lower edges align.
4. Move the attention and decision column below the paired summaries when three columns become cramped.
5. Convert wide task tables to a horizontally scrollable local surface, never document-level overflow.
6. Keep the theme switcher out of content and action hit areas.

## Four room archetypes

### Private library

Use dark timber, bottle green, parchment, brass rules, shelf numbering, and warm reading-light accents. Keep data surfaces flat and rectangular.

### Sunroom archive

Use limewash, sage, terracotta, pale wood, window-grid patterns, and botanical silhouettes. Maintain strong ink contrast.

### Listening lounge

Use ink, indigo, copper, wool gray, acoustic-grid patterns, and low horizontal bands suggesting a sofa. Use one vivid accent for actions.

### Nordic reading loft

Use ash, fog gray, off-white, cobalt, rust, oversized folio numbers, and editorial asymmetry. Let thin rules do most grouping.

## Screenshot audit

- Navigation remains legible and does not consume the room.
- The first viewport has a clear reading order.
- Paired sections share top and bottom alignment.
- Headings and metadata never collide.
- Actions remain distinguishable from decoration.
- Decorative patterns do not create false controls.
- No fixed element covers content.
- The design reads as a distinct environment even with color removed.
