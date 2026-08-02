# Theming guide

Tailwind CSS v4 theme tokens are declared in `styles/globals.css`. Semantic colors (`background`, `foreground`, `card`, `primary`, status colors, border/input/ring, and six chart colors), radii, shadows, spacing, typography, timing, and breakpoints map to CSS custom properties.

The root HTML is server-rendered with class `dark`; `ThemeProvider` also defaults to dark and suppresses the expected hydration-class warning. The provider reads/writes `localStorage` key `app-theme` and supports system preference. Theme switching is therefore client behavior after the dark SSR baseline.

Use semantic classes such as `bg-background`, `text-foreground`, and `border-border`. Do not hard-code route-specific light/dark colors. New tokens require readable values in both `:root` and `.dark`; verify text, focus rings, statuses, and charts in both modes.

Inter is loaded through `next/font` with swap behavior. The monospace stack is reserved for data-like output. Shared typography utilities (`text-display`, heading/body/small/label/data/eyebrow) keep hierarchy consistent.
