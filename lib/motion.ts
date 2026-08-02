export const MOTION_DURATION = {
  hover: 0.15,
  menu: 0.16,
  dialog: 0.2,
  drawer: 0.22,
  page: 0.18,
} as const;

export const MOTION_EASING = {
  enter: [0.16, 1, 0.3, 1],
  exit: [0.4, 0, 1, 1],
} as const;

export const MOTION_VARIANTS = {
  fade: { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } },
  scale: {
    initial: { opacity: 0, scale: 0.98 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.98 },
  },
} as const;
