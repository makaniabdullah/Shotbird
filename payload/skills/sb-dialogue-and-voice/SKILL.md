---
name: sb-dialogue-and-voice
description: "Shotbird crew skill (Cue): dialogue lines and voice in video prompts: punctuation rules, causes of lip-sync failure, and speaker tagging. Use inside Shotbird runs for any shot with speech."
---

> **Shotbird install note.** Installed for Abdullah's Shotbird crew from a pinned GitHub commit (see ATTRIBUTION.md). Only Markdown and data were installed: skip any step that runs a script, installs software, needs an API key, uploads media to third-party sites or writes to a local database. Abdullah's house rules (Obsidian vault playbooks and the agent's own instructions) take precedence over this skill.


# Dialogue, voice and audio

Audio is generated whether you direct it or not. Leaving it blank is the single most
common mistake: the model invents speech, usually in English, and burns the clip.

---

## 1. The audio hierarchy

Direct these four, in this order of priority:

1. **Dialogue** — foreground, most important
2. **SFX** — tied to a visible action
3. **Ambience** — the background bed
4. **Music** — **add in post-production only** (see §6)

---

## 2. Dialogue format

```
Dialogue in <LANGUAGE>: <Speaker> speaks in <tone/delivery>. He/She says: <exact words>
Voice: <gender>, <age> years old, <language + accent>, <delivery>, <energy>, <emotional quality>.
```

**Three rules that each cost a generation to learn:**

### Quotation marks — the contested one

> `[CONTESTED]` Google's Veo prompt guide shows attributed dialogue **with** quotation
> marks (*A woman says, "We have to leave now."*). Separate Google guidance says to use
> **a colon after the speaker's action and avoid quotation marks**, because quotes push
> the model toward rendering the text visually in the video.
>
> **Field testing sided with the no-quotes form**, and it composes with the known caption
> bug — anything that nudges the model toward rendering text makes burned-in subtitles
> more likely. **Default to the colon form.** If speech fails to trigger at all, try the
> quoted form as a fallback and note which one your footage came from.

```
Prefer:   Man says: Bom dia!
Fallback: A woman says, "We have to leave now."
```

### No ellipsis, no mid-sentence periods

An `...` or a full stop in the middle of a line **stops the voice and the lip-sync
dead.** Replace mid-sentence periods with commas; use a period or question mark only at
the very end. For genuinely separate thoughts, split into two attributed statements.

```
Wrong:  She says: I want to get so full that... what is it called?
Wrong:  She says: And the next day, I wake up wrecked. That is what I want.
Right:  She says: And the next day I wake up wrecked, cooked like an old puppet,
        that is what I want, and you?
Right:  He says in Brazilian Portuguese: Eu vou querer tangerina.
        He says in Brazilian Portuguese: Só não tá gelada, tá?
```

### Always name the language

Omitting the language causes audio-generation failures and random-language output.
Every spoken line — and every background murmur — states its language.

```
Wrong:  She says: Hm, abacaxi.
Right:  She speaks in Brazilian Portuguese with deadpan delivery. She says: Hm, abacaxi.
```

Non-English dialogue **keeps its accents** — `nao → não`, `e → é`. Accents drive
pronunciation; never ASCII-strip a dialogue line. Spell numbers out in words.

---

## 3. Line length and lip-sync

| Type | Max words | Notes |
|---|---|---|
| Short reaction | 2–4 | Best lip-sync |
| Normal line | 5–7 | Good lip-sync |
| Long line | 8–10 | Acceptable |
| Too long | 10+ | Split across clips |

One or two short attributed lines per clip. Crowding garbles the lip-sync and the mix.
**Do not write "precise lip sync"** and expect it — exact word-level sync is documented
as unreliable across model families. Ask for the line, accept the approximation, or dub
in post.

---

## 4. Voice profiles

Define one per speaking character, and reuse it verbatim:

| Attribute | Example |
|---|---|
| Gender | Male / Female |
| Age | 25–28 years old |
| Language | Brazilian Portuguese |
| Energy | Low / Medium / High |
| Style | Deadpan / Warm / Excited / Casual |
| Delivery | Monotone / Animated / Natural |
| Emotional quality | Sleepy / Friendly / Understated / Eager |

```
Voice: Male, 25-28 years old, deadpan monotone Brazilian Portuguese, casual understated
delivery, low energy, sounds like he just woke up, zero emotional reaction.

Voice: Male, 40-45 years old, warm friendly Brazilian Portuguese, relaxed casual
delivery, medium energy, slight smile in the voice, genuine helpfulness.
```

Naming the speaker in every line prevents voice drift between clips.

---

## 5. Ambience — concrete audible sounds only

Use **3–5 concrete sounds**. Specify the language of any voices. Be specific:
"keyboard clacking", not "office sounds".

```
Wrong: Ambience: city sounds, people talking, background noise
Right: Ambience: car engine hum, a single motorcycle passing, muffled conversation in
       Brazilian Portuguese, footsteps on concrete
```

**What is not an ambient sound** — this is where prompts quietly rot:

| Do not write | Why | Write instead |
|---|---|---|
| "earrings swaying" | motion is visual, not audible | "earrings jingling softly" |
| "dramatic pause" | silence is the absence of sound | "a clock ticking quietly" |
| "confident energy" | abstract, not audible | (delete — that is the dialogue's job) |
| "animated gesture sounds" | not specific | "fabric rustling from gestures" |
| "intimate atmosphere" | abstract | "soft room tone" |

Reliable concrete beds: soft room tone · clock ticking quietly · distant traffic hum ·
fabric rustling · silverware clinking · a glass setting down · a gentle exhale · air
circulation · a chair creaking.

**One bed per clip.** Layering muddies the mix.

---

## 6. SFX and music

**SFX: exactly one per clip**, tied to a visible action.

```
SFX: door handle click as the door opens
SFX: two hollow knocks on the wooden door
SFX: None.
```

Write sound events as **verbs**, not nouns — *"the mask tearing free with a sharp rip of
fabric"*, not *"fabric, ripping"*. Where a model exposes named layers, use all three:

```
Audio. Foreground: <the main event>. Bed: <ambience>. Background: <the distant layer>.
```

**Music: None. — always.** The model generates a *different* track for every clip, and
the assembly sounds disjointed. Lay one track across the whole timeline in post, ducked
−8 dB to −12 dB under dialogue.

---

## 7. Silence

Speech cues are the primary trigger for **both** unwanted audio and burned-in captions.
To get a genuinely silent clip:

- Remove every quoted line and every speech cue.
- **Never mention the mouth, lips or speaking** — "his mouth opens slightly as if about
  to speak" and "lips press together" both generate actual speech. Convey emotion through
  eyebrows, jaw and eyes only.
- State the silence positively and explicitly:
  `Dialogue: None. He does NOT speak. Mouth closed. Silent scene.`
  plus `No dialogue. No music. Ambient room tone only.`
- A thin ambient bed is safer than total dead air, which can read as a glitch.
- **Never add an `Audio language:` line to a silent clip** — it forces speech.
- In Google Flow there is also an explicit toggle: View Settings → *Return silent
  videos: On*.

---

## 8. Failure modes worth knowing

- **Depicting people under 18 has been observed to kill audio entirely** ("audio
  generation failed"). Age the character up, or accept a silent clip.
- **Upscaling 720p → 1080p strips the audio.** Plan the resolution before you commit.
- **Re-voicing a clip's spoken audio is restricted** on Omni Flash — you cannot reliably
  chat-edit speech after the fact.

More hard-won failures: [`docs/veo3-field-lessons.md`](../../docs/veo3-field-lessons.md).
