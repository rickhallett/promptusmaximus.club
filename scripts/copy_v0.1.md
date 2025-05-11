---

## Landing-Page Content / Build Map

*(wire tasks directly to Tailwind or React-+Tailwind components; variable tokens in **{braces}**)*

### 1 `<header>`

* **Logo** → “Promptus Maximus” glyph (SVG or text).
* **Nav (optional)** → “Codex”, “Arena Cohort”, “Login”.

### 2 `<section id="hero">`

| Element      | Copy / Token                                                                                                                  | Dev notes                                                    |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| **H1**       | Join the **Legion of Promptus Maximus**                                                                                       | `class="text-4xl md:text-6xl font-extrabold tracking-tight"` |
| **H2**       | Forge unbreakable prompts, wield Stoic strategy, and spar with the world’s most advanced LLMs—no prior code or toga required. | `max-w-prose opacity-80`                                     |
| **Tag-line** | Your Campus, Our Colosseum, One Giant Language Model.                                                                         | place after H2, `italic`                                     |

#### CTA block (inline form)

| Element         | Copy / Token                                                                                                              | Dev notes                           |
| --------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| **Email input** | placeholder: `your@uni.edu`                                                                                               | `class="w-full md:w-64 rounded-lg"` |
| **Button**      | **Unlock the Codex**                                                                                                      | `:hover:bg-rose-600`                |
| **Micro-copy**  | Join **{member\_count}** fellow prompt gladiators. <br>*(init `{member_count}=297`; fetch realtime from `members` table)* | small, muted                        |

---

### 3 `<section id="features">` (grid of cards or list bullets)

1. **Gladiator-grade Prompt Craft** — tone, structure, few-shot wizardry.
2. **Context Alchemy** — fuse your background with the model’s bias for sharper output.
3. **Stoic Mindset Drills** — resilience, clarity, and ethical guard-rails from the *Meditations*.
4. **Hands-on AI Sparring Matches** — real-time critique sessions with ≥ GPT-3o-class models.
5. **Think Like a Programmer** — critical, Socratic, inductive & deductive reasoning patterns.
6. **Hyper-Intelligence Protocol** — become noticeably smarter in less screen-time.
7. **10× Input Clarity → 10× Output Impact** — compound leverage through prompt design.
8. **Lifetime Access to the Promptus Maximus Codex** — version-controlled prompt library.

*(Use `flex flex-col gap-4` on mobile → `md:grid grid-cols-2`)*

---

### 4 `<section id="cohort-banner">`

* **Banner text**: **Promptus Maximus Pro: Arena Cohort ∙ Summer 2025**
* Sub-text: “Limited seats · first come, first served.”
* Style: full-width dark stripe, gold accent border (`border-y-2 border-amber-500`).

---

### 5 `<section id="social-proof">`

| Quote                                                                       | Attribution                          |
| --------------------------------------------------------------------------- | ------------------------------------ |
| “I swear my essays read like Cicero now—yet took half the time.”            | — Gladiator #42, History undergrad   |
| “Went from vague to laser-precise prompts in two days. Professors noticed.” | — Gladiator #77, Cognitive-Sci major |

(Load testimonials array from CMS; render in `swiper` or `scroll-snap` carousel.)

---

### 6 `<footer>`

* Mini-logo + copyright.
* Links: Terms, Privacy, Contact.
* “Built with stoic calm and silicon fire.”

---

## Dev Task Checklist

| # | Task                                                                            | Priority |
| - | ------------------------------------------------------------------------------- | -------- |
| 1 | Build responsive layout with Tailwind; dark-mode default.                       | P0       |
| 2 | Create `GET /api/members/count` to return live member count; fallback to 297.   | P0       |
| 3 | Wire email form to mailing-list provider (`/api/subscribe`) with optimistic UI. | P0       |
| 4 | Animate hero headline (Framer Motion fade-up).                                  | P1       |
| 5 | Add Accessibility: `aria-labels`, high-contrast focus rings.                    | P1       |
| 7 | SEO: meta-tags, OG image (Arena + circuit board motif).                         | P2       |
| 8 | Analytics event: `cta_click`, `subscribe_success`.                              | P2       |

*(P0 = must-have before launch)*

---