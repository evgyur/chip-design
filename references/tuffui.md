# TUFFUI: AI-product interface components

## Pinned source and selection

Source: https://github.com/yurigdesigner/tuffui, pinned revision `16389fad9d3ac87d94e061cd4a1ae287b1864123`, repository-relative submodule `upstreams/tuffui`. Read `README.md`, `LICENSE`, `package.json`, `lib/catalog.ts` and the chosen `registry/<slug>/docs.ts` plus component source before integration. Source code is MIT: retain copyright/license headers. No API subscription or hosted design account is required for local source inspection.

Select for React AI-product UI: chat/streaming messages, composer, tool-call blocks, approval queues, agent activity/plans, run traces, memory, context/usage meters and interactive answers. Choose only components that serve the actual brief; complete example screens are references, not permission to replace a working application. Ordinary landing pages, generic decorative animation, native desktop UI and real browser automation do not automatically select TUFFUI. Hallmark retains visual direction and the approved brand; Elaya contributes conversion reasoning only where applicable. Stageshow remains the separate option for a scripted product illustration. Preserve the existing implementation and renderer owners.

## Read before copying

The upstream site currently advertises 76 components; use the actual catalog and files at the pin instead of relying on that count for coverage. Components are source-copy/shadcn-registry material, not a registered Hermes tool or a globally installed package. Do not mutate the pinned checkout for project adaptations.

Inspect selected imports and registry dependencies before installation. The upstream demo site uses React 19, Next.js 16, Tailwind 4, Radix and Motion, but its whole site dependency tree is not automatically required by every copied component. Check the target framework, client/server boundaries, aliases, CSS variables, icon libraries and dependency versions. Copy only reviewed files into the assigned project and adapt their design tokens, font, density, color and motion to the approved brand. Do not impose TUFFUI's dark demonstration theme or globally replace app CSS. Do not run mutable `npx ...@latest` installation instructions blindly; prefer reviewed pinned local source or explicitly reviewed dependency versions.

## Real authority stays in the backend

TUFFUI is presentation, not authorization or a runtime policy engine. An approval control must not create `session` or `always` grants merely because the upstream example exposes those choices. Default to the existing backend's narrow supported scope; disable unsupported scopes. The backend must authorize the exact actor, tenant, request ID, payload/version and expiry, handle retries idempotently, and reject stale/cross-tenant/unauthorized requests. A local optimistic checkmark is not successful execution: show pending/error until authoritative acknowledgment and reconcile server readback. Never change runtime permissions as part of installing this source module.

`Undo` cannot reverse an already sent message, payment or shell side effect. Implement an actual supported cancellation before execution or label the operation as irreversible; do not promise rollback from the demo's local undo state. Risk labels, tool results, trace spans, tokens, cost and memory values must come from authenticated backend data. Redact credentials/private tool payloads from both rendered UI and captured debug logs.

Upstream `registry/use-mock-run/` drives previews. Keep mock data out of production telemetry; label DEMO/concept whenever a viewer could confuse it with a real run. Do not display fake successful tool calls or fabricated usage/prices. When backend wiring is not in scope, deliver an explicitly labelled UI mock, never claim a working agent, approval system or real product E2E.

## Focused acceptance for an actual project

Build/typecheck the selected integration in its target project, then inspect desktop and compact mobile output, keyboard/focus, readable wrapping, streaming completion and interruption, loading/error/empty states, reduced motion and cleanup/unmount behavior. For approval/control screens test pending, denial, authorized acknowledgment, failed/stale/duplicate request and unsupported grant scope; reconcile the committed effect with the backend. Real approval/money/auth integration needs its own appropriately scoped security review; source-catalog installation does not execute that boundary.

Report separately: source module installed, selected files integrated, backend connected, build executed, actual rendered output reviewed and deployed. None follows automatically from a clone or a static routing test.

## Routing checks

Positive: «интерфейс чата AI-агента» -> Hallmark + selected TUFFUI components. «Покажи trace и token usage» -> TUFFUI with authoritative data or visibly labelled mock. «Очередь подтверждений инструментов» -> TUFFUI UI only; existing backend permission owner, no new broad grants.
Negative: «проверь реальную оплату» -> actual product E2E, not a mock confirmation. «Сделай обычный лендинг» -> Hallmark + Elaya without mandatory TUFFUI. «Демо с нарисованным курсором» -> Stageshow. «Почини кнопку в native desktop app» -> existing desktop route, no React stack migration.
