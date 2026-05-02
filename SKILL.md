---
name: chip-design
description: Public /design router skill that routes product and design requests to focused deliverable skills, integrates the design-taste-frontend and gpt-taste upstreams, and checks those upstream submodules once per day on days the skill is used.
---

# Chip Design

Use this skill when the user invokes `/design`, asks for `chip-design`, or wants a routed design/product/frontend deliverable.

## Start Hook

At the start of each `/design` task, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-upstreams.ps1
```

The script checks `upstreams/design-taste-frontend` and `upstreams/gpt-taste` at most once per local day. If the skill is not used, no check is required.

If the script reports updates, inspect the changed upstream commits before changing this skill. Refresh the snapshots in `references/upstreams/` only when the upstream changes are meant to be integrated.

## Routing Workflow

1. Identify the deliverable: interface, critique, product doc, deck, business doc, static image, motion/media, or code implementation.
2. Select the primary skill from the routing table.
3. Add at most one style/helper skill when it clearly improves the result.
4. For coding implementation, include `shaw` as the execution workflow unless the user explicitly asks for a different workflow.
5. State a compact route before work: `Route: chip-design -> <primary> -> <helper> -> shaw`.
6. Execute through the selected skills, following stricter repository or task instructions when present.

## Integrated Upstreams

- `design-taste-frontend`: high-agency frontend/UI engineering direction. Submodule: `upstreams/design-taste-frontend`. Snapshot: `references/upstreams/design-taste-frontend.SKILL.md`.
- `gpt-taste`: advanced UX/UI and GSAP motion direction. Submodule: `upstreams/gpt-taste`. Snapshot: `references/upstreams/gpt-taste.SKILL.md`.

Load an upstream snapshot only when the route calls for that design style or when the user explicitly asks for its behavior.

## Primary Routes

| User intent | Primary skill |
| --- | --- |
| dashboard, analytics UI, admin console, cockpit, metrics workspace | `dashboard` |
| mobile app, iOS/Android screens, app flow | `mobile-app` |
| SaaS landing page, marketing homepage | `saas-landing` |
| pricing, plans, subscription comparison | `pricing-page` |
| interactive prototype, clickable web demo | `web-prototype` |
| wireframe, rough structure, low-fidelity layout | `wireframe-sketch` |
| critique, audit, teardown, review a design or product decision | `critique` |
| design brief, creative brief, visual direction brief | `design-brief` |
| PM spec, PRD, feature spec, product requirements | `pm-spec` |
| kanban board, workflow board, task board UI | `kanban-board` |
| social carousel, LinkedIn/Instagram slide series | `social-carousel` |
| poster, campaign image, key visual | `image-poster` |
| magazine/editorial poster | `magazine-poster` |
| simple presentation deck | `simple-deck` |
| Replit-style deck | `replit-deck` |
| Guizang-style PPT | `guizang-ppt` |
| invoice | `invoice` |
| finance report | `finance-report` |
| weekly update | `weekly-update` |
| meeting notes | `meeting-notes` |
| team OKRs | `team-okrs` |
| short-form video concept, script, shot plan | `video-shortform` |
| motion design frames, animation storyboard | `motion-frames` |
| sprite animation | `sprite-animation` |
| audio jingle, sound identity | `audio-jingle` |

## Taste Routes

Use these as primary skills only when the request names them or the task matches them exactly:

| User intent | Skill |
| --- | --- |
| premium frontend with no narrow style chosen | `design-taste-frontend` |
| stricter GPT/Codex frontend direction or GSAP-heavy Awwwards-style UI | `gpt-taste` |
| existing UI redesign or visual cleanup | `redesign-skill` |
| image reference -> analysis -> code implementation | `image-to-code-skill` |
| web design image comps only | `imagegen-frontend-web` |
| mobile design image comps only | `imagegen-frontend-mobile` |
| brand board, logo directions, palette, type system | `brandkit` |
| calm polished soft UI | `soft-skill` |
| restrained editorial/product minimal UI | `minimalist-skill` |
| hard experimental brutalist UI | `brutalist-skill` |
| Google Stitch-compatible output | `stitch-skill` |
| full output/no placeholders enforcement | `output-skill` |

## Helper Selection

- Add `design-taste-frontend` for frontend UI deliverables when the primary skill is structural (`dashboard`, `mobile-app`, `saas-landing`, `pricing-page`, `web-prototype`, `kanban-board`) and the user wants polished implementation.
- Add `gpt-taste` when the user asks for advanced motion, GSAP, cinematic landing pages, or stronger creative variance.
- Add `redesign-skill` instead of `design-taste-frontend` when improving an existing UI.
- Add `image-to-code-skill` when the user asks to generate or match a visual reference before implementation.
- Add `brandkit` when brand identity, naming, logo, typography, or palette must be defined before the deliverable.
- Add `output-skill` when the user explicitly demands complete output, no placeholders, or prior attempts were truncated.

## Disambiguation Rules

- Existing project + "make it better" -> `redesign-skill`.
- New coded frontend -> primary route + `design-taste-frontend` + `shaw`.
- Motion-heavy marketing frontend -> primary route + `gpt-taste` + `shaw`.
- Design image only -> image/poster/brand/imagegen skill, no `shaw` unless code is requested.
- Document/deck deliverable -> use the relevant document or deck skill; do not force frontend taste skills.
- Product planning/spec work -> `design-brief` or `pm-spec`; use `project-storm` only for broad architecture or high-tradeoff product planning.
- If multiple routes fit, choose the deliverable the user will actually receive. Mention the rejected route only when it would change the output.

## Route Examples

- `/design dashboard for a fintech risk team` -> `chip-design -> dashboard -> design-taste-frontend -> shaw`
- `/design critique this pricing page` -> `chip-design -> critique`
- `/design mobile onboarding flow, image comps only` -> `chip-design -> imagegen-frontend-mobile`
- `/design SaaS landing with GSAP and implement it` -> `chip-design -> saas-landing -> gpt-taste -> shaw`
- `/design make this existing app look premium` -> `chip-design -> redesign-skill -> shaw`
- `/design quarterly update deck` -> `chip-design -> simple-deck`

## Output Contract

Begin substantial work with:

```text
Route: chip-design -> <selected skills>
Deliverable: <what will be produced>
Verification: <how the result will be checked, when applicable>
```

Then continue through the selected skills. Keep routing visible but brief.
