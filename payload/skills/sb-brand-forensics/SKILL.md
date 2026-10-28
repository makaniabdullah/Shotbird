---
name: sb-brand-forensics
description: "Shotbird crew skill (Scout): extract a brand's exact look and feel from a brand guide PDF, a website or assets (palette hex and roles, typefaces and weights, logo rules, imagery direction) with evidence labels, and translate it into film-language rules for image models. Use inside Shotbird runs."
---

# Brand forensics (Shotbird · Scout)

Goal: a `brand.json` that Hatch, Slate and Hawk can enforce. Every value has to be traceable to evidence. Higgsfield's official method lives in `references/asset-analysis.md` (MIT). Read it first and follow its evidence rules: keep **exact** values separate from **inferred** ones, and never call an inferred font, colour role or grid exact.

## Source precedence
1. **The official brand guide**, usually a PDF attached to the brief (00-inbox/) or in a client folder the user names.
2. **Text extracted into the Obsidian vault**: `raw/<client>/*brand*` under `{{VAULT}}`.
3. **Approved past deliverables** in the client folder, which show the brand as it was actually used.
4. **The live website**, via WebFetch: CSS colours and webfont names.
5. **Inference from imagery.** Mark it `inferred`.

## Steps
1. **Find the pages.** Grep the extracted text for `Color|Colour|Typography|Typeface|Font|Logo|Imagery|Photography|Do not|Don't`. Note the page numbers from the section order.
2. **Render the pages** you need, macOS-native, no poppler:
   `osascript -l JavaScript ~/.claude/skills/shotbird/pdfpage.js "<guide.pdf>" ~/Shotbird/<slug>/01-scout/brand-refs "1,<colour pages>,<type pages>,<imagery pages>" 1400`
   Open each PNG with Read and confirm visually what the text says.
3. **Palette.**
   - Record the exact hex values as printed, with the guide's own names and roles (primary background, surface, accent, text).
   - Record any approved combinations or contrast pairs and accent limits.
   - If only RGB or CMYK is given, convert and mark it `converted`.
4. **Type.**
   - Record each family's name, weights, role (display, body, numerals) and case or tracking rules.
   - Note the fallback if the font isn't on Google Fonts.
5. **Logo.** Clear space, minimum size, approved colourways, and the misuse list.
6. **Imagery and art direction.** Photography style, lighting, texture, graphic devices and motion cues. Quote short phrases.
7. **Film language.** Translate it all into rules an image model and a DP can obey:
   - **Grade:** where each palette role lives on screen (sets, wardrobe, light).
   - **Accent budget:** e.g. the accent colour ≤ 5% of frame, only on hero props or UI.
   - **Mood:** contrast and texture.
   - **Text:** no readable text in generated frames; type appears only in post supers or end cards.
   - **Banned looks.**

## Output (`01-scout/brand.json`)
```json
{"name":"","source":"<file + pages>","palette":[{"hex":"#","name":"","role":"","evidence":"exact|converted|inferred"}],
 "fonts":[{"name":"","role":"","weights":"","fallback":"","evidence":"exact|inferred"}],
 "logo_rules":[""],"look":["<film-language rule>"],"rules":["<hard must>"],"banned":[""],
 "refs":["01-scout/brand-refs/page-001.png"]}
```
