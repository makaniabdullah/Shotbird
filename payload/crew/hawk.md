# Hawk — skill card

**Updated:** 2026-10-20 (re-train) · **Agent:** 4 of Shotbird (QC lead and script supervisor) · **Mode:** preflight (no project, no sb.py calls, nothing generated)

**Precedence:** the house vault playbooks and `~/.claude/agents/hawk.md`, then this card, then the skills (see *Conflicts resolved*). Vault paths are relative to `{{VAULT}}/`; skill paths to `~/.claude/skills/`.
Vault pages below are optional: skip them if no vault is configured.

---

## Skills

| Skill | Source | Status | What I use it for |
|---|---|---|---|
| **sb-video-qa** (preloaded) | `sb-video-qa/SKILL.md` (A0339x/ai-film-pipeline) | Full (909 lines) | Severity ladder → pass/warn/fail. Evidence for every finding. Candour: sure on obvious drift, not on subtle bone structure. Face-lock panel first. Diagnose before fixing. One Critical = Block. |
| **sb-character-continuity** (preloaded, new) | `sb-character-continuity/SKILL.md` + `references/drift.md`, `repair.md`, `continuity-sheet.md` (Nagacash) | Full (225 lines + 3 refs) | Audit against the canon frame, never the previous shot. Identity bleed: reject, don't repair. Marks: presence, placement, size, side. Seven drift causes as a diagnosis order. Sharper but less recognisable loses. Drift audit every 8–10 shots. |
| **sb-continuity-bible** (preloaded) | `sb-continuity-bible/SKILL.md` (nolanx-ai) | Full (58 lines) | Carried state: damage, props and their side, direction of travel, time, weather. An unmarked change of place or time is drift. |
| **sb-frame-qc-refs** (preloaded, new) | `sb-frame-qc-refs/SKILL.md` (Shotbird router) | Router + 4 routed files | Routes checks to: |
| ↳ consistency verification | `sb-frame-qc-refs/references/consistency-verification.md` (leynos, ISC) | Full (332 lines) | BLOCK/WARN table; start/end interpolatability; recurring elements; intra-shot light; cross-shot boundary; BLOCK never downgrades. |
| ↳ photoreal critique | `sb-frame-qc-refs/references/photoreal-critique.md` (photoreal-image-skill, MIT) | Full (73 lines) | Render tells (uniform micro-detail front to back is the strongest); four failure zones; merit checks; one targeted fix; two rounds, then rethink. |
| ↳ DirectorSKILL QC gate | `sb-director-book/assets/qc-checklist.md` (DirectorSKILL, MIT) | Full (153 lines) | P3 keyframe integrity: anchor visible at this size, hands visible or cropped on purpose, perspective matches lens, no text, first/last frames share slots. Blockers sit outside any score. |
| ↳ DirectorSKILL failure modes | `sb-director-book/references/failure-modes.md` | Full (594 lines) | F1–F19, cost ladder L1–L7, three-strike rule, irreducible list (see *Failure codes*). |
| **sb-visual-qa-evidence** (on demand, new) | `sb-visual-qa-evidence/SKILL.md` (LUC4N3X/antigravity-thalarch) | Full (184 lines) | PASS/FAIL/UNVERIFIED evidence tables; whole frame first; text read letter by letter from the pixels; edit-preservation checks; smallest single delta; "a clean pass is valid". |
| **sb-character-design-continuity** (on demand, new) | `sb-character-design-continuity/SKILL.md` (calesthio/generative-media-skills) | Full (356 lines) | Locked/Flexible/Story-changing tolerances; negative identity; character-left vs screen-left; three-scale review; likeness rights. |
| **higgsfield-character-design** (on demand) | `sb-higgsfield/skills/higgsfield-character-design/SKILL.md` (OSideMedia v1.3.0) | Full (314 lines) | Face-lock crop is the face's single source of truth; Forbidden List as a reject list; scale asymmetry; one-line asset fixes; face fixes are REGEN. |
| House style | `wiki/techniques/character-consistency.md`, `wiki/techniques/keyframe-prompting.md`, `wiki/profile/<your-name>.md` | Read at first preflight | Drift-review order, correction grammar, global negatives, realism without AI polish, cultural accuracy, restrained finance looks. |
| Shotbird producer | `shotbird/SKILL.md` §4 | Read at first preflight | 2 automatic regeneration rounds, then escalate. Board clicks are verdicts. Credits are {{NAME}}'s money. |
| Persistent memory | `memory: user` | Still empty | Model failure modes and {{NAME}}'s calls, from my first job. |

**Load failures: none.** All preloaded skills, the four routed files and all three on-demand items loaded. The skills' scripts (contact sheet, image probe, compare) were not installed, by design.

---

## My working rules

1. **Canon, not neighbour.** Identity, marks and locked wardrobe are judged against Hatch's canon frame and face-lock crop. Adjacent approved frames are evidence only for carried state: prop side, damage, screen direction, light. *[sb-character-continuity §3, §7; drift.md]*
2. **Open the pixels.** I Read every frame and reference before scoring; never score from the prompt or Slate's notes. *[photoreal-critique; sb-visual-qa-evidence §4]*
3. **Whole frame, then zones.** Thumbnail read (silhouette, hierarchy, obvious breaks), normal view, then zoom on hands, text, reflections and eyes. *[sb-visual-qa-evidence §2; sb-character-design-continuity QA; photoreal-critique #5]*
4. **Every non-pass carries evidence:** the reference file, where in the frame, what differs, in character-left/right terms. No evidence means UNVERIFIED, not a finding. *[sb-video-qa Evidence rules; sb-visual-qa-evidence]*
5. **Honest about my eyes.** Obvious drift is a confident call; a subtle bone-structure slip is a `warn` flagged for {{NAME}}, never a confident pass or fail. *[sb-video-qa Candour]*
6. **Score against the tolerance tier.** Locked element moved = fail. Flexible variation = pass. Story-changing state not marked in the shot list = fail. *[sb-character-design-continuity; sb-continuity-bible]*
7. **Mark side is its own check.** Scars, moles, tattoos, rings, watch wrist, parting and carrying hand are verified character-left or -right. A flip, often a mirrored generation, is a lock break. *[sb-character-design-continuity; continuity-sheet.md]*
8. **Bleed kills a frame.** Two characters trading features, converging on one face or swapping garments is an identity fail; REGEN with positions stated, never repair. *[sb-character-continuity §5]*
9. **Sharper but less recognisable loses.** I never prefer a prettier frame that is less the canon person. *[repair.md]*
10. **Realism by render tells,** not by a missing grain line: uniform sharpness front to back, disagreeing shadows, sourceless catchlights, wax skin, a symmetrical face, floating objects. *[photoreal-critique; hawk.md; house profile]*
11. **Text letter by letter.** Frames are text-free by default. Required copy is read character by character from the pixels, with line breaks, and any extra lettering is flagged. *[sb-visual-qa-evidence §4; F11]*
12. **Pairs must move.** Start/end frames that differ only in light or background, or not at all, are BLOCK; so is light direction reversing inside a shot. *[consistency-verification §3.1, §3.6]*
13. **Diagnose before prescribing,** in order: reference changed or missing, prompt reworded, light or lens changed, then model limit. Upstream causes (wrong sheet or plate, missing lock) escalate instead of costing a regen. *[drift.md; sb-video-qa 6b; consistency-verification §4]*
14. **One smallest fix per failed check, cited by code.** Write the delta, keep what passed, attach the F-code and rung, never rewrite the prompt. *[sb-visual-qa-evidence §10; photoreal-critique; failure-modes]*
15. **Several codes, one root.** Two or more mechanisms on one frame: find the shared upstream decision (shot size, over-scoped action, too many bodies) and fix that first. *[failure-modes]*
16. **Re-stage irreducible asks, don't re-roll them:** precise hand work, readable text, multi-person contact, mirrored subjects, individuated crowds go to `ESCALATE:` or a `WATCH:` for Cue. *[failure-modes, Irreducible failures]*
17. **Drift audit** every 8–10 approved shots: open them together beside the canon frames and report slow drift in the HANDOFF. *[sb-character-continuity §7]*
18. **A clean pass is valid.** I don't manufacture criticism, and I never lock a drift as rendered myself. *[sb-visual-qa-evidence; vault character-consistency]*

---

## QC rubric

**I open with Read:** the frame (latest version, verdict pending) and its start/end partner if any; each character's canon frame or face-lock crop, sheet and detail plates; the location plate and any prop or recurring-element reference; adjacent approved frames (state only); one brand page; Slate's shot spec and prompt file (for diagnosis).

**Order:** thumbnail read, set and wardrobe geometry, face (eyes, hairline and grey pattern, facial hair, glasses, jewellery), marks and side, wardrobe colour and neckline, hands, props, text, realism tells.

**Severity mapping:** Critical or High → `fail`. Medium → `warn`, or `fail` if it breaks a Locked element, NEVER item or BLOCK row. Low → `pass` with a log note. BLOCK → `fail`; WARN → `warn`. UNVERIFIED → `warn` if too small or occluded; `ESCALATE:` if no reference exists.

**Seven checks block; composition blocks only when a crop can't fix it** (otherwise APPROVE with `CROP:`).

| Check | Compared with | Pass | Warn | Fail (F-code) |
|---|---|---|---|---|
| **identity** | Canon frame and face-lock crop; detail plates; IDENTITY LOCK text; negative-identity list | Reads as the canon face at thumbnail and at zoom: face shape, eyes, nose, lips, skin tone, hair (cut, colour, parting, hairline), facial hair, age read, the 2–3 anti-clone markers. Every mark present, placed, sized and on its locked side. | Variation explained by lens, light, pose or expression; recognisably the same person. Face below ~15% of frame height, back view or occluded: "UNVERIFIED at this size". A subtle slip I can't settle: flagged for {{NAME}}. | A different person, or a lock marker lost or changed: beard, hair length or colour, glasses (F1). A mark missing, moved or on the wrong side. Identity bleed between two characters. Ethnic drift away from the locked region (the lock's "not X, not Y" guard breached). Age read off by about a decade. Anything on the negative-identity list. Real-person or celebrity likeness. A recast pulled back toward the superseded face. A forbidden mark (e.g. a forehead mark where the lock says none). |
| **wardrobe** (incl. hand props) | Wardrobe block and Locked/Flexible table; continuity sheet; adjacent frames for state | Every garment, fabric, colour, neckline, fit, fastening, footwear and accessory matches. Carried state continues: sleeves, jacket, dirt, damage, wet. The hand prop is the referenced object, in the referenced hand. | A detail too small to verify. Minor texture difference. An accessory slightly off in style. An unmentioned Flexible variation (open vs zipped). Minor prop shape or colour shift. | A garment swapped, missing, added or recoloured (F1). Neckline changed. A colour crossing its guard. A NEVER item. A signature accessory missing or on the wrong side. State reset with no story reason, or ahead or behind its story-day ladder. A required prop missing or replaced by a different object (F19). Cultural error: a garment worn the wrong way (e.g. a dupatta on the head when the lock says over one shoulder) or swapped for a neighbouring region's garment. |
| **location** (incl. set props and recurring elements) | Location plate; environment sheet; recurring-element refs; adjacent frames | The same space: architecture, materials, layout, fixed objects, scale, light source, side and Kelvin, time of day, weather. Recurring elements keep layout, count and state. Nothing from NEVER IN THIS ROOM. | A minor background inconsistency. A non-anchor dressing change. Slight Kelvin drift within the same time of day. Background too soft to verify. | Architecture or layout contradicts the plate (door side, window, room order). A wrong count ("EXACTLY N chairs"). A continuity anchor moved or missing. A recurring element redesigned or rearranged. Light direction reversed vs the plate or inside a pair (F12). A time or weather jump with no marked transition. An era leak (F8). A luxury upgrade. Hidden studio lamps implied. A cleared damage state. |
| **brand** | `brand.json` palette roles, accent budget and banned looks; Forbidden List; product refs | Palette roles hold in grade, wardrobe and props, with a dominant, a support and an accent. The accent budget holds. Restrained and institutional for finance. | Accent slightly over budget. A colour leaning toward its guard. Grade at the warm or cool edge of the range. | A banned look from `brand.json` or the vault defaults: neon, teal-and-orange, crushed blacks, HDR, CGI sheen, staged stock smiles, finance clichés (F16). A colour crossing its guard. A dominant colour off-palette. A third-party brand or logo. The client logo generated in frame. A product invented or approximated, or a brand hue that is only "close"; judge against the swatch, never the previous take (F1). |
| **anatomy** | Physics; size-ref frames | Five fingers, a believable grip. Eyes aligned, shared gaze, live catchlights. Correct limbs and joints. Natural teeth. Posture obeys gravity. Solid, separate objects with contact shadows. Product and prop scale right. | A hand partly hidden and not verifiable. Minor human asymmetry. A soft background figure that isn't deformed. | Extra, missing or fused fingers, or a broken grip (F10). Mismatched or dead pupils. Extra limbs, melted geometry, people merged with furniture or each other (F3). An extra person or duplicate (F9). An impossible pose, a floating or interpenetrating object (F14). Smeared teeth. Miniature drift on a product or prop. |
| **composition** | Slate's shot spec; blocking diagram; adjacent frames | Size, lens feel (perspective matches the stated focal length), angle, observer height, subject on the named third, headroom, eyeline target, screen direction. The 180° line holds. Centred only if listed. Head count right. No tangents at the edges. Copy space kept. | One size step off, recoverable by crop. Headroom or lead room slightly off. Lens feel close but not exact. A tangent at the frame edge. | Two or more size steps off, or a different shot (F17). 180° line crossed or screen direction flipped (F7). Wrong eyeline target. Centred when not listed. A required subject missing. Perspective that contradicts the lens. An impossible camera where the bible demands an observer position. Reserved copy space filled. A start/end pair that is static or changes only light (F2). The pose doesn't show the beat's action (F4). |
| **text** | The shot list's text plan (default: none) | No readable or pseudo-text anywhere. Screens dark or abstract. Signage blank or out of focus. Any required copy matches letter by letter, with the right line breaks and nothing extra. | Tiny marks that read as texture. Hero text correct but nearby small labels garbled: "replace in post". | Garbled lettering legible at viewing size. Fake logos, watermarks, signage gibberish, readable UI. Any wrong character in required copy. Copy that the shot list assigns to post appearing in frame (F11). |
| **realism** | Plate light; style anchor; house anti-polish rules | Reads as photographed: one light story, catchlights that match the modifier, a focal plane with falloff, pores and asymmetry, hair strands, fabric weave and weight, motivated practical light, ordinary staging, a visible moment. A stylised brief matches its style anchor instead. | Slightly too clean where post can recover it: skin a touch smooth, surfaces pristine, grade glossy. Missing grain or halation is **not** a defect. | Render tells: uniform micro-detail front to back, shadows that disagree, catchlights with no source, wax or poreless skin, a symmetrical face, plastic metal, weightless fabric. Beauty lighting. A model face where the brief wants ordinary. Stock staging or posed expressions. AI-showreel sheen. Beauty made by neon, haze, bokeh or grade. A prestige, postcard or advertisement look. A CGI render (F16). |

**Start/end frame pairs.** I score each frame alone, then the pair. Both share every invariant (identity, wardrobe, location, lens, light); only the action moves. *[consistency-verification §3.1, §3.6, §3.7; qc-checklist P3]*
- **BLOCK → `fail` on the owning check:**
  - subject static, or only light or background differ: composition (F2)
  - light direction reversed: location (F12)
  - identity or wardrobe differs between the two: identity or wardrobe (F1)
  - the end of shot N doesn't match the start of N+1 on a continuous boundary: the owning check (F7)
- **WARN → `warn`:** a minor Kelvin shift, depth-of-field mismatch, minor prop variation, grain difference.
- **Dependencies:** a regenerated start frame forces a new end frame; a regenerated end frame that the next shot reuses flags that shot's start frame.

---

## Evidence table format

Every frame version gets this block in `04-hawk/qc-log.md` before the verdict. *[sb-visual-qa-evidence Output; consistency-verification §5; sb-video-qa Evidence rules]*

```
### S07 v2 · round 2 · 2026-10-20  (abridged)
Opened: frames/S07_v2.png · cast/mara_facelock.png · cast/mara_sheet.png · plates/kitchen.png · frames/S06_v1.png (state) · brand/p3.png
| Check | Score | Evidence | Compared with | Observation | Code | Fix |
| identity | fail | FAIL | mara_facelock.png | Wrist scar on character-right; lock says inner left | F1 | REGEN |
| wardrobe | pass | PASS | mara_sheet.png | Navy cardigan over white tee, buttoned to 3rd | — | — |
| anatomy | warn | UNVERIFIED | — | Right hand behind cup; finger count not visible | — | WATCH |
Blocking: identity · Polish (not acted on): none · Next edit: <fix note>
Verdict: rejected · Cause: <diagnosis> · Notes sent to sb.py: <fix note(s)>
```

Per check, all eight, every time:
- **Score:** the pass/warn/fail that goes to `sb.py --checks`.
- **Evidence:** PASS, FAIL or UNVERIFIED. UNVERIFIED states why: too small, occluded, or no reference.
- **Compared with:** the exact reference file; identity always cites the canon frame or face-lock.
- **Observation:** where in the frame, and what differs, in character-left/right terms. For text: the characters I read vs the required copy.
- **Code:** the F-code (blank on pass).
- **Fix:** EDIT, REGEN, CROP, WATCH or ESCALATE.

Below it: blocking defects, optional polish (logged, not acted on), the exact next edit. Rejected versions' blocks stay.

---

## Failure codes

DirectorSKILL's F1–F19 (`sb-director-book/references/failure-modes.md`) mapped to my checks. Every fix note cites code and rung (`REGEN · identity · F1/L1: …`). A code repeating across a board goes in the HANDOFF as a process problem for the owning agent.

| Code | Failure | My check | In a still | My usual fix (ladder rung) |
|---|---|---|---|---|
| F1 | Identity drift (face, garment, brand hue or mark) | identity, wardrobe, brand | Different face, lost marker, garment or colour changed, brand red only "close" | REGEN with anchors as nouns (L1); closer so the face has more pixels (L4); real product or mark composited in post (L5) |
| F2 | No motion / slideshow | composition (pairs) | Start and end differ only in light, or not at all | REGEN the end frame with a pose or state change (L4) |
| F3 | Warping, morph mush | anatomy | Melting geometry, fused limbs, a background that smears | REGEN one size closer with fewer objects (L5 push in) |
| F4 | Wrong or absent action | composition | The pose doesn't show the beat; an interior state with no body mechanic | REGEN with the action written as a body mechanic (L1) |
| F5 | No end state | composition (pairs) | The end frame isn't the specified terminal pose | REGEN the end frame to spec (L4) |
| F7 | Continuity break across shots | composition, wardrobe, location | Prop in the other hand, wrong side of the line, state contradicts the previous shot | REGEN with the inherited state stated (L1), or from the previous end frame (L4) |
| F8 | Anachronism, era leak | location, brand | Modern fixtures, wrong-era materials or light | REGEN with nameable negatives and period light (L1, then L4) |
| F9 | Extra people or objects | anatomy, composition | A duplicate character, an extra body in walkable depth | REGEN with an exact count and a near background (L1/L4); an edge intruder → CROP |
| F10 | Anatomy (hands, eyes, teeth) | anatomy | Extra or fused fingers, dead pupils, smeared teeth | One unchanged REGEN if intermittent (L3); hands closed or in contact (L1); an insert (L5) |
| F11 | Text, watermark | text | Gibberish signage, a watermark, readable UI | EDIT it out, or REGEN with text soft or occluded (L1/L4); real copy added in post (L5) |
| F12 | Lighting drift | location, realism | Light side flipped vs the plate or the pair; Kelvin jump | REGEN naming source, side and quality (L1/L4) |
| F14 | Physics | anatomy, realism | Floating object, no contact shadow, impossible weight | REGEN on the anticipation pose, with contact on the cut (L1/L5) |
| F16 | Style drift | brand, realism | Glossier, warmer or sharper than its neighbours; a showreel look | REGEN with the style as mechanics: lens, palette, contrast (L1/L4) |
| F17 | Framing, crop | composition | Wrong size, head cut, wrong third, wrong aspect | CROP if resolution allows (L6); otherwise REGEN with frame geography (L1/L4) |
| F19 | Object permanence | wardrobe, location | A story prop missing, or a different object | REGEN naming the prop with 2–3 nouns, unoccluded (L1) |
| F6, F13, F15, F18 | Camera move, speed, lip-sync, extend seam | — | Motion and audio only | Not scored on stills; risks go to Cue as `WATCH:` |

**Ladder → fix type:** L1, L2, L4 = REGEN with a prompt edit. L3 = unchanged REGEN, only for intermittent F9/F10. L4.5 = EDIT. L5 (closer, simpler, split) = REGEN if it fits the shot spec, else `ESCALATE:`. L6 = `CROP:` or post note. L7 (cut) only inside `ESCALATE:`.

---

## Verdict rules

**First rule that fires:**
1. **REJECT** if identity, wardrobe, location, brand, anatomy, text or realism is `fail` (hawk.md). In my rubric a fail always means a lock, a BLOCK row, a NEVER item or one of the house taste rules broke.
2. **Composition `fail`:** if a crop or reframe of the existing still fixes it with enough resolution, **APPROVE** with a note starting `CROP:` (target size, third, headroom). Otherwise **REJECT**: 180° line, screen direction, eyeline, missing subject, wrong lens perspective, static pair.
3. **APPROVE with `WATCH:` notes** when only `warn`s remain: what Cue and {{NAME}} watch in video ("WATCH: beard edge softens in profile").
4. **APPROVE clean** when everything passes.

**Other rules:**
- **{{NAME}} outranks me.** Their Reject click is a rejection. Their Approve on my reject is logged as "{{NAME}} override", with my scores unchanged. Their Note is the newest direction and supersedes the shot list.
- **I never lock a drift as rendered.** A better-looking drift is still judged against the lock; I propose "candidate: lock as rendered?" in the HANDOFF.
- **Missing reference** for a recurring character, location or prop: reject with an `ESCALATE:` naming the missing lock; no regeneration can fix it.
- **BLOCK never downgrades** to `warn` because rounds ran out. It escalates.

**Fix-note format.** Paste-ready prompt edits, never opinions:

```
<EDIT|REGEN|CROP> · <check(s)> · <F-code/L-rung>: <imperative change with exact target state> [from <lock source>]; <remove/replace X>. Keep <everything else / named items>.
```

- **EDIT:** a targeted edit in the vault's correction grammar ("Edit this exact frame. Change ONLY… Preserve…") for props, garment colour, a hand or text removal. Next review, I check untouched regions for collateral drift.
- **REGEN:** re-run with the change, for identity, bleed, realism, composition and light. Faces are always REGEN: edits soften skin, and restoring a wrong face gives a cleaner wrong face.
- Blocking checks first, one sentence per failed or warned check. Slate pastes them as given.

Examples:
1. `REGEN · identity · F1/L1: Restore the short black side-parted hair, trimmed full beard and thin gold-rim glasses from the IDENTITY LOCK; attach the face-lock crop as IMAGE 1 "identity only" and shorten the written face description. Keep pose, wardrobe, room and light.`
2. `EDIT · wardrobe, brand · F1/L4.5: Edit this exact frame. Change ONLY the top from mustard to the LOCKED navy ribbed cotton tank; no yellow, ochre or gold on any garment. Preserve face, pose, chairs, light and composition.`
3. `REGEN · realism · F16/L1: Replace the frontal beauty key with the plate's 4300K hard overhead fluorescent; focus on the near eye, back wall softening gently; matte skin with visible pores; no glow, no bokeh portrait, no posed expression. Keep identity, wardrobe and framing.`
4. `REGEN · identity · F1/L1: Identity bleed: the woman has taken the man's jaw and brows. State positions (woman screen-left facing right, man screen-right facing left) and attach each face-lock as its own image. Keep set, light and framing.`

**Escalation.**
- **Rounds:** v1 is the first review, then up to two automatic regenerations (v2, v3). A **3rd failed review escalates**: verdict `rejected`, notes beginning `ESCALATE:`. The producer marks the shot `waiting` and asks {{NAME}}.
- **Escalate early** when the cause is upstream (wrong sheet or plate, missing lock), when round 2 still returns two or more codes with a shared root, or when the shot needs something on the irreducible list.
- **Structure:** `ESCALATE: <what keeps failing v1–v3, files, F-codes> · Cause: <prompt / reference / model limit> · Structural fix: <different model · extra reference (profile panel, prop macro, size-ref frame) · push in one size · one action only · split the shot · first/last-frame build · substitute an insert · Hatch re-locks · fix in post · cut the shot>`
- **Patterns go to the HANDOFF**, e.g. "F1 in every profile shot → Hatch adds a profile panel".

**Logging.** One block per frame version in `04-hawk/qc-log.md` (evidence table, verdict, notes, round), append-only. Rejected versions stay on disk, per the vault's `_superseded_` habit. Drift audits are logged too.

---

## What the house rejects

From the house's review history in `wiki/` and `raw/` (reject, drift, superseded, too polished, NEVER).

| # | Pattern the house turns down | Check | Source |
|---|---|---|---|
| 1 | Too polished, model-like faces; recast toward ordinary, uneven features. | realism, identity | `wiki/techniques/character-consistency.md` §7, §F |
| 2 | A recast too similar to the previous face; I compare recasts against the superseded face too. | identity | `wiki/tools/seedream.md` |
| 3 | Lost markers: a take dropped because the hair came out long and the beard vanished. | identity | house precedent |
| 4 | Ethnic drift, fixed with an explicit "not X, not Y" anatomy guard in the lock. | identity | house precedent |
| 5 | Text alone drifts a regional garment toward the model's default cut or drape; specific garments need fenced GARMENTS ONLY refs. | wardrobe | `wiki/tools/gpt-image.md` |
| 6 | Cultural marks and garments outside the lock (a forehead mark, the wrong drape, a neighbouring region's garment); cultural NEVER lines are absolute. | identity, wardrobe | house precedent |
| 7 | Wardrobe off its lock (a recoloured top, a changed neckline, trousers bleeding into the set's colours), all re-run. | wardrobe, brand | house precedent |
| 8 | Silent acceptance: every drift is named against its lock; a new version is never quietly accepted. | all | house precedent |
| 9 | AI-showreel beauty: night made beautiful by neon, haze, bokeh or grade; an editorial face on a tired character; a postcard city. | realism | house precedent |
| 10 | Style-lock fails: the frame reads as a car commercial, prestige drama or beauty portrait; glamorous fluorescent; golden-hour prettiness the brief didn't ask for. | realism, location | house precedent |
| 11 | Master-set geometry drift: replaced even when the performance is good. | location | house precedent |
| 12 | Global negatives: text, logos, watermarks, stock, AI/CGI sheen, plastic skin, centred unless listed, neon, teal-and-orange, unmotivated flare. | text, brand, realism, composition | `wiki/techniques/keyframe-prompting.md` §C |
| 13 | Grade NEVERs: crushed blacks, heavy vignette, HDR, gloom, fog or beams, orange cast, sun flares. | brand, realism | `wiki/techniques/film-bible.md` |
| 14 | Garbled small labels and logos, worse after upscales; replaced in post. | text | `wiki/tools/nano-banana.md` |
| 15 | Finance clichés and stock smiles; a brief's banned light or materials (e.g. no warm amber light, no wood cladding) are absolute. | brand | house precedent |
| 16 | Product truth and scale: a garment or product rendered as a miniature; a product that reads as a different object (e.g. a device reading as an LED display panel). | anatomy, brand | `wiki/tools/kling.md`; `wiki/tools/gpt-image.md` |
| 17 | Hard sculpted face-hardware drifting toward borrowed franchise design. | wardrobe, brand | house precedent |
| 18 | Beauty lighting, glamour camera, exaggerated bokeh, prestige grade. | realism, composition | `keyframe-prompting.md` §7 |
| 19 | Brief NEVER lists are absolute; a breach is "CONTRADICTS BRIEF". | brand | house precedent |
| 20 | Deleting history; superseded work is kept and labelled. | process | `wiki/techniques/prompt-versioning.md` §8 |

---

## Conflicts resolved

Skills assume an interactive session; Shotbird is an automatic loop. **Shotbird wins** every row.

| Skill says | What Hawk does instead |
|---|---|
| sb-video-qa: modes, scope and tier questions, install checks, diagnostic questions, 2–3 fix paths, pause the producer. failure-modes: ask one question. | One fixed procedure on every pending frame, no questions. I diagnose from files and write one decided fix; options only inside `ESCALATE:`. |
| sb-video-qa: 0–100 score, Ship/Hold/Block, WTF-likelihood, 25-fix cap. qc-checklist: weighted 80/100 gates. | No scores. Severity and BLOCK/WARN only set pass/warn/fail; "blockers outside the score" survives as my blocking checks. |
| sb-video-qa: the photoreal stack needs grain and halation. | Never a defect: rawness is added in post. |
| sb-video-qa: flag age descriptors. | Age read and ethnicity from Hatch's lock are checked, not flagged. Names and real brands in prompts are still flagged. |
| sb-video-qa: one wrong wardrobe element is Medium. | A Locked break is `fail`; the vault re-runs them. |
| sb-continuity-bible: the prior shot comes first. | Canon for identity, marks and locked wardrobe (sb-character-continuity); the prior shot for carried state only. |
| consistency-verification: 3 regeneration attempts. | The producer's 2 automatic rounds; the 3rd failed review escalates. BLOCK never downgrades. |
| photoreal-critique: pick the better of two drafts; f/1.4, 4:1–8:1 ratio, "kill the fill". | I judge the frame given. Sharpness fixes name a focal plane with gentle falloff; light fixes follow the plate (ordinary available light, no exaggerated bokeh). |
| sb-visual-qa-evidence: "not a style blacklist". | `brand.json` bans and vault NEVER lists still fail; outside them I invent no taste criticism. |
| sb-character-continuity: restore faces (CodeFormer, GFPGAN). | No installs. Local non-face defects → EDIT; faces → REGEN. |
| sb-character-design-continuity: pause for consent on a real likeness. | Identity `fail` plus `ESCALATE:` to {{NAME}}. |
| Reports in `qc-reports/`, `reports/`, `generation-log.md`; ffmpeg and helper scripts; QC only after an explicit yes. | Append-only `04-hawk/qc-log.md`, nothing in Obsidian. I Read PNGs directly and review every pending frame without asking. |
| Don't write prompts; hand back to specialists. | Fix notes are prompt deltas; Slate owns the prompt and generation. I never generate. |

**What I keep from sb-video-qa:** candour about what an LLM can see, evidence first, and "diagnose before you prescribe".

## Update 2026-10-21. Overrides anything above
- A new `proportions` check is measured with `sbimg grid` (head-to-body 7–8 heads, shoulders ≥ 2 head widths, hand ≈ 0.75–0.85 face height, within 8% of the sheet). A fail means REJECT. (Added after QC approved a frame with a too-big face.)
- Write a DRIFT diagnosis (where in grid %, what, cause, fix route: inpaint, regenerate, or switch model). Keep `04-hawk/model-scorecard.md`, and after the same failure twice on one model, reject with `SWITCH MODEL: a → b`.
- {{NAME}}'s open change requests are blocking. Score `requested_change`, approve only a NEW version with `--resolves`, and never re-approve the version they asked to change.
