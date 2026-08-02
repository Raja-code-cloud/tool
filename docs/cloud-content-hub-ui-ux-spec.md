# Cloud Content Hub AI

## UI/UX Specification

**Product promise:** Create Once. Publish Everywhere.  
**Design direction:** Dark-first, premium enterprise SaaS  
**Document status:** Developer-ready foundation, version 1.0

---

## 1. Experience Principles

### Rationale

Cloud Content Hub AI serves beginners and professional teams. The interface must reduce the apparent complexity of multi-platform publishing without concealing control from expert users.

1. **One clear next action.** Every view has one visually dominant action; secondary actions remain available but quieter.
2. **Progressive disclosure.** Show essential choices first and reveal advanced controls on demand.
3. **Create once, adapt visibly.** Keep the master content and platform variants connected so users always understand what AI changed.
4. **Fast scanning.** Use concise labels, strong alignment, restrained color, and predictable page anatomy.
5. **Trust through transparency.** Show generation status, publishing status, account health, errors, and irreversible consequences explicitly.
6. **Power without clutter.** Batch actions, keyboard shortcuts, saved views, and dense layouts are available without burdening first-time users.
7. **Accessible by default.** Keyboard access, visible focus, semantic structure, readable contrast, and reduced motion are requirements.
8. **Calm confidence.** Motion and color communicate state; neither is decorative.

### UX writing

- Use sentence case: “Create content,” not “Create Content.”
- Use verbs for actions and nouns for destinations.
- Keep button labels specific: “Schedule 6 posts,” not “Continue.”
- Explain the result before destructive or external actions.
- Avoid AI mystique. Say what will be generated, from which source, and where it will publish.
- Pair errors with a cause, impact, and recovery action.

---

## 2. Information Architecture

### Rationale

Navigation follows the content lifecycle: understand, create, adapt, schedule, measure, and administer. Stable destinations reduce learning cost while global creation remains one click away.

Primary sidebar order:

1. Dashboard
2. Content Library
3. Upload Wizard
4. AI Studio
5. Scheduler
6. Calendar
7. Analytics
8. Social Accounts
9. Settings

Rules:

- Keep destination order stable across roles; hide only destinations the user cannot access.
- Use section separators before Analytics and Settings when space permits.
- Show badges only for actionable exceptions, such as failed posts or disconnected accounts.
- Preserve the last selected workspace and sidebar state.
- Global search and “Create” remain available from every primary page.
- Deep pages use breadcrumbs; top-level pages omit redundant “Home.”

---

## 3. Color System

### Rationale

Neutral surfaces carry hierarchy while a single cool accent signals interaction. Semantic colors are reserved for meaning, preserving an enterprise tone and improving status recognition.

### Dark theme tokens

| Token            |     Value | Use                         |
| ---------------- | --------: | --------------------------- |
| `bg-canvas`      | `#090B0F` | Application background      |
| `bg-sidebar`     | `#0C0F14` | Persistent navigation       |
| `bg-surface-1`   | `#11151C` | Cards, panels               |
| `bg-surface-2`   | `#171C24` | Raised/interactive surfaces |
| `bg-surface-3`   | `#202733` | Selected and pressed states |
| `border-subtle`  | `#252C37` | Structural separators       |
| `border-strong`  | `#364152` | Active boundaries           |
| `text-primary`   | `#F4F7FB` | Main content                |
| `text-secondary` | `#AAB4C3` | Supporting content          |
| `text-tertiary`  | `#758195` | Metadata and placeholders   |
| `accent`         | `#6EA8FE` | Primary action and focus    |
| `accent-hover`   | `#8BBAFF` | Hover                       |
| `accent-pressed` | `#4C8FEF` | Pressed                     |
| `accent-muted`   | `#172A46` | Selected backgrounds        |
| `success`        | `#49C884` | Completed, healthy          |
| `warning`        | `#E6B450` | Attention required          |
| `danger`         | `#F07178` | Failure, destructive        |
| `info`           | `#69B7E8` | Neutral information         |

### Light theme mapping

Use `#F7F8FA` canvas, `#FFFFFF` surfaces, `#E2E6EC` subtle borders, `#111827` primary text, and `#2563EB` accent. Semantic meanings must remain identical.

### Usage rules

- Target WCAG 2.2 AA: 4.5:1 for normal text and 3:1 for large text and UI boundaries.
- Never encode state by color alone; pair color with text and, where useful, an icon.
- Use accent on the primary action, focus ring, active navigation, and selected data only.
- Charts use a maximum of six accessible series colors; direct-label series where possible.
- Avoid pure black, pure white, gradients, and decorative neon effects.

---

## 4. Typography

### Rationale

A neutral sans-serif keeps dense operational screens readable. A compact type scale limits visual noise and makes hierarchy depend on size, weight, and spacing together.

**UI family:** Inter, with `Segoe UI`, system-ui, sans-serif fallbacks.  
**Code/data family:** JetBrains Mono, with `Cascadia Code`, monospace fallbacks.

| Style       | Size / line height | Weight | Use                               |
| ----------- | ------------------ | -----: | --------------------------------- |
| Display     | 32 / 40 px         |    650 | Welcome or major empty state only |
| H1          | 24 / 32 px         |    650 | Page title                        |
| H2          | 20 / 28 px         |    600 | Major section                     |
| H3          | 16 / 24 px         |    600 | Card/panel title                  |
| Body        | 14 / 22 px         |    400 | Default UI copy                   |
| Body strong | 14 / 22 px         |    600 | Emphasis                          |
| Small       | 12 / 18 px         |    400 | Metadata                          |
| Label       | 12 / 16 px         |    600 | Form labels, compact headers      |
| Data        | 13 / 20 px         |    500 | Tabular values, counters          |

Rules:

- Use no more than three weights per screen.
- Keep prose lines between 55 and 75 characters.
- Use tabular numerals for metrics, calendars, counters, and tables.
- Never use all caps for navigation or headings.
- Truncate only when the full value is available by tooltip, expansion, or detail view.

---

## 5. Spacing, Grid, and Shape

### Rationale

A four-pixel base supports compact enterprise layouts while preserving consistent rhythm. Larger page gutters create calm; denser spacing stays inside data-heavy components.

### Spacing scale

`0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80 px`

- Inline icon gap: 8 px.
- Related field gap: 12–16 px.
- Card padding: 16 px compact, 20 px default, 24 px spacious.
- Section gap: 32 px desktop, 24 px tablet, 20 px mobile.
- Page padding: 32 px desktop, 24 px tablet, 16 px mobile.
- Maximum primary content width: 1440 px; reading/editor columns: 760–880 px.

### Grid

- Desktop ≥1280 px: 12 columns, 24 px gutters.
- Tablet 768–1279 px: 8 columns, 20 px gutters.
- Mobile <768 px: 4 columns, 16 px gutters.
- Optional right utility panel: 320–380 px; main content must remain at least 640 px before the panel collapses.

### Radius

- 4 px: badges, compact controls.
- 6 px: inputs, buttons, menu items.
- 8 px: cards, popovers.
- 12 px: dialogs and prominent panels.
- Pill radius only for status chips, segmented controls, and avatars.

### Borders and elevation

- Prefer 1 px borders and surface contrast to shadows.
- Popovers: `0 8px 24px rgba(0,0,0,.32)`.
- Dialogs: `0 16px 48px rgba(0,0,0,.42)`.
- Focus ring: 2 px accent with 2 px canvas offset.
- Never stack more than three perceived elevation levels.

---

## 6. Iconography

### Rationale

Consistent line icons improve recognition without competing with content.

- Use one library only: Lucide or an equivalent 1.75–2 px rounded-stroke set.
- Standard sizes: 16 px in controls, 18 px in navigation, 20–24 px for standalone actions.
- Pair unfamiliar icons with labels. Icon-only buttons require accessible names and tooltips.
- Use filled icons only for selected states or urgent status.
- Never use emojis as interface icons.

---

## 7. Application Shell and Navigation

### Sidebar

- Expanded width: 240 px; collapsed width: 64 px.
- Fixed desktop sidebar; overlay drawer below 1024 px.
- Workspace switcher sits at top; account and help controls sit at bottom.
- Active item uses `accent-muted`, primary text, and a 2 px accent indicator.
- Collapsed items show tooltips and retain badges.
- Keyboard order follows visual order; arrow keys may move within the navigation group.

### Header

- Height: 56 px; sticky with a subtle bottom border.
- Contains sidebar trigger, global search/command entry, create action, notifications, help, and profile.
- Search opens a command palette with recent items, navigation, content, and actions.
- Mobile header prioritizes menu, page title, create, and overflow.

### Breadcrumbs

- Use for detail and nested settings pages.
- Collapse middle items on small screens.
- Last item is current location and not a link.

---

## 8. Page Layout Standard

### Rationale

Predictable page anatomy lets users scan new areas without relearning controls.

Each page uses:

1. Breadcrumb, when nested.
2. Header row with H1 and concise description.
3. One primary action and up to two visible secondary actions; overflow the rest.
4. Optional status, tabs, or view controls directly below.
5. Main content area.
6. Optional right utility panel for contextual—not navigational—content.

Behavior:

- Keep primary action top-right on desktop and visible near the title on mobile.
- Sticky action bars are allowed only for long edit, review, or bulk-selection flows.
- Filters and results share a clear visual relationship.
- Preserve filter, sorting, density, and view preferences by user.
- Empty, loading, and failure states occupy the same geometry as eventual content to reduce layout shift.

---

## 9. Component System

### Buttons

- Heights: 32 px compact, 36 px default, 40 px prominent.
- Variants: primary, secondary, ghost, destructive, icon.
- Primary: accent fill, dark high-contrast label.
- Secondary: surface fill and strong border.
- Ghost: transparent until hover; use for low-priority actions.
- Destructive confirmation uses a red primary button only in the confirmation dialog.
- States: default, hover, pressed, focus-visible, disabled, loading.
- Loading preserves width and replaces leading icon with a spinner; label remains when space permits.
- Limit one primary button per action region.

### Form elements

- Default height: 36 px; touch contexts: 44 px minimum target.
- Label above control; required indicator appears in text, not color only.
- Helper or error text sits below and does not replace the label.
- Validate on blur for field errors and on submit for cross-field errors.
- Inputs support default, hover, focus, filled, disabled, read-only, warning, and error.
- Textareas display character count near limits.
- Selects support search after seven options.
- Checkboxes are for independent choices; radios for one required choice; switches for immediate binary settings.

### Search, filters, and sorting

- Search uses descriptive placeholder text such as “Search content by title or tag.”
- Debounce remote results and show progress without clearing existing results.
- Active filters appear as removable chips with “Clear all.”
- Filter menus show selected counts.
- Sorting states are explicit in both label and icon.

### Cards

- Use cards to group related content, not every section.
- Default border, surface-1 background, 8 px radius, and 20 px padding.
- Interactive cards have one primary click target and visible focus.
- Metrics cards include label, value, trend, comparison period, and optional compact visualization.
- Never rely on hover to expose the only route to essential actions.

### Tables

- Header height: 40 px; rows: 44 px compact or 52 px default.
- Left-align text; right-align numeric data; keep actions rightmost.
- Sticky header for long tables; freeze the primary identifier when horizontal scrolling is required.
- Row selection reveals a persistent bulk-action bar.
- Sort controls announce direction; selection state is screen-reader accessible.
- Mobile tables become prioritized lists/cards, not compressed desktop tables.

### Badges and status

- Variants: neutral, info, success, warning, danger.
- Use short nouns or past-tense states: Draft, Scheduled, Published, Failed.
- Include status icon when color distinction may be insufficient.
- Do not use badges as buttons unless styled and announced as interactive controls.

### Dialogs and drawers

- Use dialogs for focused decisions; drawers for contextual inspection or editing.
- Widths: 400 px confirmation, 560–720 px forms; drawers 360–480 px.
- Trap focus, close with Escape when safe, restore focus to invoker.
- Destructive dialogs name the affected object and impact.
- Do not nest dialogs.

### Dropdowns

- Minimum width 180 px; maximum height 360 px before scrolling.
- Group related commands and separate destructive commands.
- Support arrows, Home/End, Enter/Space, and Escape.

### Pagination

- Prefer cursor/infinite loading only for discovery feeds.
- Use page-based pagination for tables and predictable bulk work.
- Show range, total, page size, and next/previous; avoid excessive page numbers on mobile.

### Charts

- Every chart includes title, period, units, accessible summary, and tooltip.
- Use lines for trends, bars for comparisons, stacked bars for composition, and donut charts only for 2–5 parts.
- Avoid 3D, dual axes by default, and decorative chart chrome.
- Provide table or textual equivalents for critical data.

### Upload zones

- Dashed structural border, upload icon, supported types, maximum size, and browse action.
- Support drag/drop, click, paste where applicable, progress, pause/retry, replace, and remove.
- Validate before upload when possible; identify the failed file and recovery action.

### Avatars

- Sizes: 24, 32, 40 px; use initials fallback with deterministic neutral color.
- Groups show up to three avatars plus count.
- Always provide a text name in menus and detailed contexts.

---

## 10. Feedback and System States

### Empty states

- Explain what belongs here, why it is useful, and one next action.
- First-use empty states may include a restrained illustration; filtered empties should show “No matches” with filter-reset action.
- Permission empties explain who can grant access.

### Loading states

- Use skeletons for content expected within 1–3 seconds.
- Use inline spinners for actions and determinate progress for upload/generation/publishing.
- After 10 seconds, show an explanatory message and safe cancel/background option.
- Never replace an entire page with a spinner when stable navigation can remain.

### Errors

- Field: inline beside the source.
- Section: banner within the affected region.
- Page: full-state message with retry and support reference.
- Toast: only for non-blocking outcomes; never as the sole place for critical errors.
- Preserve user input after failure.

### Success

- Use inline state changes for local actions and brief toasts for background completion.
- Confirm external publishing with platform, account, time, and content title.
- Provide “View post” or “Undo” when technically safe.

---

## 11. Dashboard

### Rationale

The dashboard should answer three questions quickly: What needs attention, what should I do next, and how is publishing performing?

Desktop layout:

- Welcome header with contextual greeting, workspace health summary, and “Create content.”
- Quick actions: Upload, Generate with AI, Schedule, Connect account.
- Four statistics cards: Published, Scheduled, Engagement, Failed/Needs attention.
- Main two-column region: AI Suggestions (8 columns) and Publishing Calendar (4 columns).
- Recent Content table with thumbnail, title, variants, status, owner, updated, actions.
- Bottom modules: Recent Activity, Platform Health, Storage Usage.

Rules:

- Personalize AI suggestions from drafts, performance, missing variants, and calendar gaps; explain “Why this suggestion.”
- Failed publishing and disconnected accounts outrank promotional suggestions.
- Let users dismiss suggestions and preserve the choice.
- Collapse to one column below 1024 px; show key stats in a horizontal scroll only when cards retain 160 px minimum width.

---

## 12. Content Library

### Rationale

The library supports visual browsing and high-volume operations without creating separate mental models.

- Header: create/upload primary action, search, saved view, filter, sort, grid/list toggle.
- Filters: type, status, platform, owner, date, campaign, tag.
- Grid cards: preview, title, type, status, platform indicators, updated time, owner, overflow.
- List columns: selection, title, type, variants, platforms, status, owner, modified, actions.
- Bulk bar: selected count, tag, move, schedule, export, archive; delete remains in overflow.
- Preview panel opens from a row/card without leaving the current view and shows content, variants, metadata, publishing history, and edit action.
- Preserve scroll and selection after preview closes.
- Search highlights matching title/tag text.
- Support saved views for repeated filter/sort combinations.

Mobile:

- Default to list cards.
- Open filters in a full-height drawer.
- Keep search and filter count visible.
- Move preview to a full-screen detail route.

---

## 13. Upload Wizard

### Rationale

The wizard converts a complex content pipeline into a guided sequence while allowing experienced users to skip irrelevant media steps.

Sequence: **Poster → Article → Video → Thumbnail → AI Generation → Review → Schedule**

Layout:

- Desktop stepper left, active form center, contextual guidance/preview right.
- Mobile stepper becomes “Step 3 of 7” with a compact progress bar.
- Sticky footer contains Back, Save and exit, and a specific next action.

Rules:

- Save draft automatically and show “Saved” with timestamp.
- Allow optional steps to be skipped and marked accordingly.
- Validate the current step before advancing; never erase completed work.
- Poster: upload/select source image, crop, alt text.
- Article: import, paste, upload, or compose; show title and readability checks.
- Video: upload/select, transcript detection, caption language.
- Thumbnail: choose frame, upload, or AI-generate; preview aspect ratios.
- AI Generation: choose platforms, tone, audience, goals, and generation depth; estimate output.
- Review: compare master and variants, flag policy/length issues, approve individually or in bulk.
- Schedule: account, date/time, timezone, queue position, final confirmation.
- Show processing as per-file/per-variant progress and allow safe backgrounding.

---

## 14. AI Studio

### Rationale

AI Studio is the flagship workspace. It must make adaptation fast while preserving authorship, control, and platform-specific confidence.

Desktop layout:

- Top toolbar: content title/status, save state, version history, share, primary “Approve all.”
- Left pane (38–44%): Master Article editor with outline and source controls.
- Center pane (36–42%): platform tabs and generated variant editor.
- Right utility pane (280–340 px): live preview, suggestions, SEO, hashtags, publishing tips.
- Panes are resizable within minimum widths; below 1180 px the utility pane becomes a drawer.

Core behavior:

- Platform tabs show icon, account, character status, and approval state.
- Generated content is editable; AI-generated and user-edited states are distinguishable in version history, not through noisy inline decoration.
- Character counter shows current/limit and warning thresholds at 85% and 100%.
- SEO score includes actionable factors, not only a number.
- Suggestions show proposed change, reason, and affected platform; users accept or dismiss each.
- “Regenerate” opens scope controls: whole variant, selection, headline, CTA, hashtags, or tone.
- Preserve the previous version after regeneration and support undo.
- Copy confirms copied scope.
- Approve locks the reviewed version for scheduling; editing it returns it to “Changes to review.”
- Reject asks for an optional reason that can guide regeneration.
- Live preview uses authentic aspect ratio and truncation behavior but is labeled as an approximation.
- Hashtag suggestions show relevance and platform suitability; users can reorder and remove.
- Publishing tips identify platform constraints, best-time guidance, missing media/alt text, and account issues.

Keyboard:

- `Ctrl/Cmd+S`: save.
- `Ctrl/Cmd+Enter`: generate or approve only when clearly labeled in context.
- `Alt+1…9`: switch platform tabs.
- Slash menu for editor commands.
- All AI actions announce start and completion to assistive technology.

Mobile:

- Use one pane at a time: Master, Variant, Preview, Insights.
- Keep platform switcher and save state sticky.
- Put approval actions in a bottom action bar.

---

## 15. Scheduler and Calendar

### Rationale

Scheduling should expose timing conflicts and publishing risk while keeping rearrangement direct.

Views:

- Calendar: month/week/day with platform filters and timezone.
- Timeline: chronological cross-platform plan.
- Queue: ordered posts per account with cadence controls.

Behavior:

- Dragging shows valid targets, proposed time, conflicts, and a keyboard-accessible move alternative.
- Dropping requires confirmation only when changing timezone/day, overriding a conflict, or moving a published item.
- Cards show platform, time, status, content type, and account.
- Statuses: Draft, Needs approval, Scheduled, Publishing, Published, Failed, Paused.
- Upcoming panel shows next posts and urgent blockers.
- Dense days use a count overflow, never unreadably compressed cards.
- Failed items remain in context with retry and diagnostic actions.
- Mobile defaults to agenda view with day picker; drag/drop becomes “Move to.”

---

## 16. Analytics

### Rationale

Analytics must connect publishing activity to outcomes and make cross-platform differences understandable without misleading comparisons.

Page controls:

- Date range, comparison period, platforms, accounts, campaigns, and export.
- Persistent disclosure of timezone and data freshness.

Sections:

- KPI cards: Reach, Engagement, Followers, Publishing Frequency.
- Growth Trends: time-series with comparison period.
- Platform Comparison: normalized bars plus raw-value toggle.
- Publishing Frequency versus Engagement: aligned charts, not a misleading dual axis.
- Top Posts table: content, platform, published time, reach, engagement rate, clicks, conversions when available.
- Insight callouts explain meaningful changes and methodology.

Rules:

- Define metrics in tooltips and document platform-specific differences.
- Mark estimated or unavailable data.
- Avoid red/green for positive/negative trend alone; use arrows and labels.
- On mobile, stack charts, simplify axes, and make Top Posts a ranked list.

---

## 17. Social Accounts and Settings

### Social Accounts

- Group connections by platform and workspace.
- Each account shows identity, permissions, connection health, last sync, and actions.
- Connection flows explain requested permissions before redirect.
- Expired/revoked states provide reconnect and impact details.
- Bulk health summary appears above account list.

### Settings

- Secondary navigation: Workspace, Members, Roles, Brand, AI defaults, Publishing, Notifications, Billing, Integrations, Security.
- Save locally scoped settings within each section; avoid one page-wide save button.
- Show inherited versus overridden values.
- Role and permission changes include clear impact summaries.
- Destructive workspace actions occupy a separated danger zone.

---

## 18. Responsive Rules

### Rationale

Responsive design prioritizes tasks rather than shrinking desktop geometry.

- **≥1440 px:** full sidebar, 12-column layout, optional utility panel.
- **1024–1439 px:** collapsible sidebar, reduced gutters, utility panel may become drawer.
- **768–1023 px:** overlay navigation, 8-column layout, two-column content only where each column remains useful.
- **<768 px:** 4-column layout, single primary column, 16 px page padding.
- Maintain 44×44 px touch targets even if the visible control is smaller.
- Convert tables to prioritized cards/lists; retain sorting and filtering.
- Convert side panels to full-height drawers or routes.
- Keep primary action accessible without obscuring content.
- Never hide essential functionality solely because of viewport size.
- Support 200% text zoom without clipping or loss of operation.

---

## 19. Accessibility

### Rationale

Accessibility is a product-quality requirement and supports keyboard-heavy professional workflows.

- Meet WCAG 2.2 AA.
- Use semantic landmarks, heading order, lists, tables, labels, and buttons.
- Provide a skip-to-content link.
- Show focus-visible on every interactive element; never remove outlines without replacement.
- Keep keyboard order aligned with visual order.
- Announce async generation, upload, save, and publishing updates through appropriate live regions.
- Trap and restore focus for modal experiences.
- Provide alt text workflow for publishing media and mark decorative imagery accordingly.
- Do not auto-play media or motion.
- Support `prefers-reduced-motion`, high-contrast modes, browser zoom, and screen magnification.
- Ensure status is expressed with text/icon in addition to color.
- Use error summaries for long forms and move focus to the summary after failed submit.
- Avoid time limits; where unavoidable, warn users and allow extension.
- Test with keyboard only, NVDA on Windows, VoiceOver on Apple devices, and automated contrast/semantic tools.

---

## 20. Motion

### Rationale

Motion clarifies cause and effect. It must feel immediate and never delay work.

- Hover/color transitions: 100–150 ms.
- Menus/tooltips: 120–160 ms fade/scale from 98%.
- Drawers: 180–220 ms slide.
- Dialogs: 160–200 ms fade/scale.
- Page content: optional 120–180 ms fade; navigation shell remains stable.
- Use ease-out for entrances and ease-in for exits.
- Drag items follow pointer directly; nearby targets may shift subtly.
- Skeleton shimmer is optional and disabled under reduced motion.
- Avoid bounce, parallax, looping decorative animation, and staggered lists.
- Reduced motion replaces transforms with immediate state changes or brief opacity transitions.

---

## 21. Consistency and Governance

### Rationale

A premium system stays coherent by constraining exceptions and making decisions traceable.

- Components consume semantic tokens; feature teams do not introduce one-off colors, spacing, radii, or shadows.
- Reuse existing components before creating variants.
- New variants require a recurring use case across at least two product areas.
- All components define default, hover, pressed, focus, disabled, loading, empty, error, and success states where applicable.
- One concept has one name across navigation, buttons, documentation, and support.
- Primary actions use the same placement and visual priority within equivalent layouts.
- Icons, labels, and shortcuts remain consistent across menus and toolbars.
- Density modes may change spacing, not information hierarchy or control behavior.
- Maintain design tokens and component documentation as the source of truth.

---

## 22. Design QA and Developer Handoff

### Required design annotations

- Component name and variant.
- Token references rather than isolated values.
- Responsive behavior at all four breakpoint ranges.
- Keyboard interaction and focus order.
- Loading, empty, error, success, permission, and offline states.
- Truncation, overflow, localization, and long-content behavior.
- Accessibility name, role, state, and announcements for custom controls.

### Acceptance checklist

- [ ] One primary action is evident in each action region.
- [ ] Layout follows the page standard and spacing scale.
- [ ] All colors and dimensions map to documented tokens.
- [ ] Text and UI contrast meet WCAG 2.2 AA.
- [ ] Keyboard operation and visible focus are complete.
- [ ] Mobile behavior is task-appropriate, not merely compressed.
- [ ] Empty, loading, error, success, and permission states are designed.
- [ ] Destructive and external publishing actions communicate impact.
- [ ] AI output remains reviewable, reversible, and attributable.
- [ ] Tables and charts have accessible alternatives.
- [ ] Motion respects reduced-motion preferences.
- [ ] No essential action depends exclusively on hover, color, or gesture.

### Definition of ready

A screen is ready for development only when its content hierarchy, component variants, responsive transformations, interaction states, copy, accessibility behavior, and edge cases are documented. Any new visual pattern must first be reconciled with this system.
