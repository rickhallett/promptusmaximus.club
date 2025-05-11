# Product Requirements Document (PRD)

**Project Codename:** *Promptus Maximus – Signal‑Fire Landing*

**Prepared for:** autonomous Taskmaster agent & core repo maintainers
**Date:** {{NOW}}

---

## 1  Objective

Build and deploy a minimal, high‑impact landing site that:

1. Captures visitor emails for the upcoming *Promptus Maximus* content drop.
2. Projects the brand voice (Stoic‑gladiator × AI wizard).
3. Runs entirely on Vercel with zero‑friction DX; expandable later to forum & merch.

## 2  Success Criteria

| KPI              | Target                                    |
| ---------------- | ----------------------------------------- |
| **Time to Prod** | ≤ 2 developer‑hours hands‑on (one coffee) |
| **TTFB** (home)  | < 100 ms global (Vercel edge)             |
| **CLS / LCP**    | Lighthouse ≥ 90 mobile                    |
| **Signup‑%**     | stub—tracking added, no goal yet          |

## 3  In‑Scope

* Single hero landing (index) + “Thanks” page.
* Email capture → Resend list (REST).
* Tailwind styling, dark gladiator palette.
* Serverless API route for subscribe (Next App Router).
* Basic validation + honey‑pot field.
* Prod deploy on `<promptmaximus.club>` via Vercel.

## 4  Out of Scope (v1)

* Forum / auth
* Payments / merch
* CMS or DB
* i18n
* SEO extras (OG images) beyond default

## 5  Tech Stack

| Layer      | Choice                                               | Rationale                                        |
| ---------- | ---------------------------------------------------- | ------------------------------------------------ |
| Framework  | **Next.js 14 (App Router)**                          | First‑class Vercel support; future ISR/blog MDX. |
| Styling    | **Tailwind CDN**                                     | No build step; atomic classes.                   |
| Serverless | **/app/api/subscribe route**                         | Native in Next 14.                               |
| E‑mail     | **Resend SDK**                                       | Free tier, simple REST.                          |
| State      | None (edge function writes directly to Resend list). |                                                  |
| Infra      | **Vercel Hobby**                                     | 1‑click CI/CD; env‑var UI.                       |

## 6  High‑Level Flow

```mermaid
flowchart LR
  A[Visitor] --> B[Landing page  (GET /)]
  B --> C[Form POST /api/subscribe]
  C -->|validate| D{Valid?}
  D -- no --> E[Return 400]
  D -- yes --> F[Resend.contacts.create]
  F --> G[302 → /thanks]
  G --> H[Thank‑you page]
```

## 7  Task Breakdown (Taskmaster syntax)

```taskmaster
- id: init
  title: Repo bootstrap ‑ Next 14 + Tailwind CDN
  assignee: agent
  steps:
    - npx create-next-app promptus-maximus --ts --app --eslint
    - remove unused boilerplate; add Tailwind CDN link in layout.tsx

- id: landing
  title: Hero Landing UI
  dependsOn: [init]
  description: Implement main slogan, sign‑up form, dark stone bg.

- id: api_subscribe
  title: /api/subscribe route
  dependsOn: [init]
  description: Serverless handler; call Resend.contacts.create; redirect 302.

- id: env
  title: Configure Vercel env vars (RESEND_API_KEY, RESEND_CONTACT_LIST)
  dependsOn: [api_subscribe]

- id: honeypot
  title: Add hidden honeypot input + simple regex email check
  dependsOn: [landing]

- id: thankyou
  title: “Thanks” page with Stoic quote + back button
  dependsOn: [api_subscribe]

- id: deploy
  title: Production deploy & custom domain promptmaximus.club
  dependsOn: [env, thankyou]

- id: lighthouse
  title: Run Lighthouse CI, fix CLS/LCP regressions
  dependsOn: [deploy]

# Stretch
- id: analytics
  title: Add Vercel Analytics or Plausible
  dependsOn: [deploy]
```

## 8  Open Questions

1. Exact copy for hero ↓ final approval by Brandon.
2. Color palette—stick to stone‑900 + amber‑600?
3. Future blog → MDX or external CMS?

## 9  Risks & Mitigations

| Risk                            | Likelihood | Impact | Plan                                        |
| ------------------------------- | ---------- | ------ | ------------------------------------------- |
| Resend API quota hit            | low        | med    | Batch retries, swap to Mailerlite if needed |
| Brand voice drifts across pages | med        | med    | Single copywriter review pass               |
| Over‑engineering via frameworks | low        | low    | Keep components server‑only where possible  |

---

## 10  Glossary

* **Signal‑fire** – periodic e‑mail blast / YouTube short drop.
* **Arena** – future gated forum.
* **Gladius** – sword metaphor for concise prompt.

> *“The impediment to action advances action.”*  — Marcus Aurelius

*End of PRD v1.0*
