# Animation guide

## Verified implementation

Global motion tokens define `120ms` fast and `200ms` medium durations with an emphasized cubic Bézier easing. Route content uses a `page-enter` opacity/6px translation animation. Interactive cards use `hover-raise` only on hover-capable devices. Radix overlays use `tw-animate-css` enter/exit utilities. Feature views also use Framer Motion and shared definitions under `lib/motion`.

Spinners and skeletons use CSS animation. All shared animated UI includes `motion-reduce` handling, and the global reduced-motion query reduces animation/transition durations and removes hover lift.

## Guidance

Use animation to clarify entry, exit, progress, or spatial relation—not as decoration. Reuse shared durations/variants, animate transform and opacity where possible, and preserve focus through transitions. New Framer Motion code must honor reduced-motion preference and avoid delaying access to content.
