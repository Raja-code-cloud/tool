export type FactoryOverrides<T extends object> = Partial<T> | ((sequence: number) => Partial<T>);

export type Factory<T extends object> = {
  build: (overrides?: FactoryOverrides<T>) => T;
  buildList: (count: number, overrides?: FactoryOverrides<T>) => T[];
  reset: () => void;
};

export function createFactory<T extends object>(defaults: (sequence: number) => T): Factory<T> {
  let sequence = 0;

  const build = (overrides: FactoryOverrides<T> = {}): T => {
    sequence += 1;
    const resolvedOverrides = typeof overrides === "function" ? overrides(sequence) : overrides;

    return { ...defaults(sequence), ...resolvedOverrides };
  };

  return {
    build,
    buildList: (count, overrides = {}) => Array.from({ length: count }, () => build(overrides)),
    reset: () => {
      sequence = 0;
    },
  };
}
