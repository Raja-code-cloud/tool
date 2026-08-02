import { describe, expect, it } from "vitest";

import { createFactory } from "../factories";

describe("test factory foundation", () => {
  it("builds deterministic objects and resets its sequence", () => {
    const factory = createFactory((sequence) => ({
      id: `record-${sequence}`,
    }));

    expect(factory.buildList(2)).toEqual([{ id: "record-1" }, { id: "record-2" }]);

    factory.reset();

    expect(factory.build()).toEqual({ id: "record-1" });
  });
});
