#!/usr/bin/env node
/**
 * Runs Layer 2–3 evaluations: template rendering and offline acceptance criteria.
 */
import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { globSync } from "glob";
import YAML from "yaml";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");

let failures = 0;

function fail(message) {
  console.error(`  ✗ ${message}`);
  failures += 1;
}

function pass(message) {
  console.log(`  ✓ ${message}`);
}

function renderTemplate(template, variables) {
  const fields = new Set();
  const regex = /\{([a-z][a-z0-9_]*)\}/g;
  let match;
  while ((match = regex.exec(template)) !== null) {
    fields.add(match[1]);
  }

  const missing = [...fields].filter((f) => !(f in variables));
  const unknown = Object.keys(variables).filter((k) => !fields.has(k));
  if (missing.length > 0) {
    throw new Error(`Missing variables: ${missing.join(", ")}`);
  }
  if (unknown.length > 0) {
    throw new Error(`Unknown variables: ${unknown.join(", ")}`);
  }

  return template.replace(/\{([a-z][a-z0-9_]*)\}/g, (_, name) => String(variables[name]));
}

function checkCriterion(type, value, rendered, output) {
  switch (type) {
    case "rendered_equals":
      return rendered === value;
    case "rendered_contains":
      return rendered.includes(value);
    case "rendered_matches_regex":
      return new RegExp(value).test(rendered);
    case "output_contains":
      return output.includes(value);
    case "output_not_contains":
      return !output.includes(value);
    case "output_matches_regex":
      return new RegExp(value).test(output);
    case "output_length_min":
      return output.length >= value;
    case "output_length_max":
      return output.length <= value;
    case "output_json_valid":
      try {
        JSON.parse(output);
        return true;
      } catch {
        return false;
      }
    default:
      throw new Error(`Unsupported criterion type: ${type}`);
  }
}

function runCase(caseDef, template) {
  const { id, inputs, expected_rendered, acceptance } = caseDef;
  let rendered;
  try {
    rendered = renderTemplate(template, inputs);
  } catch (err) {
    fail(`case "${id}" — render failed: ${err.message}`);
    return;
  }

  if (expected_rendered !== undefined && rendered !== expected_rendered) {
    fail(`case "${id}" — rendered output mismatch`);
    return;
  }

  const output = acceptance.fixture_output ?? "";
  for (const criterion of acceptance.criteria) {
    const ok = checkCriterion(criterion.type, criterion.value, rendered, output);
    if (!ok) {
      fail(`case "${id}" — criterion failed: ${criterion.type}`);
      return;
    }
  }
  pass(`case "${id}" passed`);
}

console.log("Cloud Content Hub — Prompt Evaluation");
console.log("======================================");

const packages = globSync("prompts/**/metadata.yaml", {
  cwd: ROOT,
  ignore: ["**/node_modules/**"],
}).map((f) => dirname(f));

for (const packageDir of packages) {
  const absDir = join(ROOT, packageDir);
  const label = packageDir.replace(/\\/g, "/");
  console.log(`\nPackage: ${label}`);

  const metadata = YAML.parse(readFileSync(join(absDir, "metadata.yaml"), "utf8"));
  const template = readFileSync(join(absDir, metadata.template.file), "utf8");

  const evalFiles = globSync("evaluations/*.yaml", { cwd: absDir });
  for (const evalFile of evalFiles) {
    const suite = YAML.parse(readFileSync(join(absDir, evalFile), "utf8"));
    console.log(`  Suite: ${evalFile}`);
    for (const caseDef of suite.cases) {
      runCase(caseDef, template);
    }
  }
}

console.log("\n======================================");
if (failures > 0) {
  console.error(`FAILED — ${failures} failure(s)`);
  process.exit(1);
}
console.log("PASSED — all evaluations OK");
process.exit(0);
