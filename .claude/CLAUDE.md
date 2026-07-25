# CLAUDE.md

Project-specific guidance for AI coding agents.

<!-- ASTRYX:START -->
Astryx v0.1.6 · 149 components
CLI: run every command as `npx astryx <cmd>` (shown below as `astryx ...`).

SETUP (once, in your app entry e.g. main.tsx) — without these, components render unstyled:
  import "@astryxdesign/core/reset.css";
  import "@astryxdesign/core/astryx.css";

WORKFLOW — discover, don't guess. Before writing UI:
1. `astryx build "<idea>"` — START HERE: returns a kit (closest [page] + [block]s + [component]s). No args = full playbook.
2. `astryx template <name> [--skeleton]` — scaffold the [page]/[block]s it named, or study their layout. Templates are reference code.
3. `astryx component <Name>` — props + examples for every component you use.

RULES:
- No <div> — components do all layout/spacing. Full page → AppShell; sidebar nav → SideNav.
- Frame first: pick the shell (AppShell / Layout+LayoutPanel) and budget regions in px BEFORE writing content (`astryx docs layout`).
- Dense data = rows (Table, List/Item) edge-to-edge — never Card-wrapped list items. Card = dashboard widgets, galleries, settings groups only.
- Status → StatusDot/Token; Badge only for counts and enumerated states, never decoration.
- Custom styling: component props first; else style/className with tokens — var(--color-*|--spacing-*|--radius-*). No raw hex/px. (No StyleX/Tailwind compiler here — don't use xstyle/utility classes.)
- Tokens for every value (`astryx docs tokens`). Brand/accent via `astryx theme` — never override --color-* in :root.

MORE CLI:
  search "<query>"   find any component / hook / doc / template / block
  component --list   149 components by category
  template --list    page + block recipes
  docs <topic>       color, elevation, icons, illustrations, layout, migration, motion, principles, shape, spacing, styling, theme, tokens, typography
  swizzle <Name>     eject component source for deep customization
  upgrade --apply    run after any @astryxdesign/core bump
<!-- ASTRYX:END -->

<!-- ASTRYX:MIGRATION:START -->
## Migrating an existing Tailwind/shadcn/Radix app to Astryx

Treat this as a shell-and-workflow migration, not a global class swap. Wrap the app in `Theme`/`AppShell` first, then move one route/surface at a time — keep routing and business logic intact.

Before touching any migration work, run:
```
npx astryx docs migration --dense
npx astryx docs theme --dense
npx astryx docs styling --dense
npx astryx template AppShellTopNavWithSideNav --skeleton
```

Order: install+init → wrap root in `Theme` → make CSS `@layer` order explicit (design-system layers before Tailwind utilities) → render a foundation smoke test page (Button/TextInput/Card/Table — fails if `getComputedStyle(button).paddingInline === '0px'`) → migrate persistent frame (AppShell/TopNav/SideNav) → replace shared primitives (Button, TextInput, Dialog, etc. — see mapping table in `npx astryx docs migration`) → replace global workflows (CommandPalette, settings, theme toggle) → strip legacy Tailwind classes per finished surface → verify light+dark mode, keyboard nav, responsive, empty/error/loading states.

Cascade-layer gotcha: an unlayered `@import` (no `layer()`) always overrides every named layer regardless of specificity — this is the most common silent breakage. Always import legacy resets as `@import "./legacy-reset.css" layer(reset);` and declare the canonical `@layer` order once, before any import.

Full guide, code snippets, and the shadcn/Radix→Astryx component mapping table: `npx astryx docs migration`.
<!-- ASTRYX:MIGRATION:END -->
