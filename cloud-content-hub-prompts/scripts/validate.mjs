#!/usr/bin/env node
/**
 * Validates prompt packages against JSON Schemas and structural requirements.
 * Layer 1 of the evaluation framework.
 */
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import addFormats from "ajv-formats";
import Ajv2020 from "ajv/dist/2020.js";
import { globSync } from "glob";
import YAML from "yaml";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "..");
const SCHEMAS = join(ROOT, "schemas");

const ajv = new Ajv2020({ allErrors: true, strict: false });
addFormats(ajv);

function loadSchema(name) {
  const path = join(SCHEMAS, name);
  return JSON.parse(readFileSync(path, "utf8"));
}

const evalCaseSchema = loadSchema("evaluation-case.schema.json");
ajv.addSchema(evalCaseSchema);

const validateMetadata = ajv.compile(loadSchema("prompt-metadata.schema.json"));
const validateInputWrapper = ajv.compile(loadSchema("prompt-input.schema.json"));
const validateEvalSuite = ajv.compile(loadSchema("evaluation-suite.schema.json"));

let errors = 0;

function fail(message) {
  console.error(`  ✗ ${message}`);
  errors += 1;
}

function pass(message) {
  console.log(`  ✓ ${message}`);
}

function findPromptPackages() {
  return globSync("prompts/**/metadata.yaml", {
    cwd: ROOT,
    ignore: ["**/node_modules/**"],
  }).map((relative) => dirname(relative));
}

function validatePackage(packageDir) {
  const absDir = join(ROOT, packageDir);
  const label = packageDir.replace(/\\/g, "/");
  console.log(`\nPackage: ${label}`);

  const metadataPath = join(absDir, "metadata.yaml");
  const metadata = YAML.parse(readFileSync(metadataPath, "utf8"));

  if (!validateMetadata(metadata)) {
    for (const err of validateMetadata.errors ?? []) {
      fail(`metadata.yaml — ${err.instancePath || "/"} ${err.message}`);
    }
    return;
  }
  pass("metadata.yaml valid");

  const templatePath = join(absDir, metadata.template.file);
  if (!existsSync(templatePath)) {
    fail(`missing template file: ${metadata.template.file}`);
  } else {
    pass(`template file exists: ${metadata.template.file}`);
  }

  const inputSchemaPath = join(absDir, metadata.input_schema.file);
  if (!existsSync(inputSchemaPath)) {
    fail(`missing input schema: ${metadata.input_schema.file}`);
    return;
  }

  const inputSchema = JSON.parse(readFileSync(inputSchemaPath, "utf8"));
  if (!validateInputWrapper(inputSchema)) {
    for (const err of validateInputWrapper.errors ?? []) {
      fail(`input.schema.json — ${err.instancePath || "/"} ${err.message}`);
    }
  } else {
    pass("input.schema.json valid");
  }

  const readmePath = join(absDir, "README.md");
  if (!existsSync(readmePath)) {
    fail("missing README.md");
  } else {
    pass("README.md exists");
  }

  if (metadata.id !== packageDir.split(/[/\\]/).pop()) {
    fail(`metadata id "${metadata.id}" does not match directory name`);
  }

  const evalFiles = globSync("evaluations/*.yaml", { cwd: absDir });
  if (evalFiles.length === 0) {
    fail("no evaluation files in evaluations/");
  } else {
    for (const evalFile of evalFiles) {
      const evalPath = join(absDir, evalFile);
      const suite = YAML.parse(readFileSync(evalPath, "utf8"));
      if (!validateEvalSuite(suite)) {
        for (const err of validateEvalSuite.errors ?? []) {
          fail(`${evalFile} — ${err.instancePath || "/"} ${err.message}`);
        }
      } else {
        pass(`${evalFile} valid`);
      }
    }
  }
}

console.log("Cloud Content Hub — Prompt Validation");
console.log("=====================================");

const packages = findPromptPackages();
if (packages.length === 0) {
  fail("no prompt packages found");
} else {
  console.log(`Found ${packages.length} prompt package(s)`);
  for (const pkg of packages) {
    validatePackage(pkg);
  }
}

console.log("\n=====================================");
if (errors > 0) {
  console.error(`FAILED — ${errors} error(s)`);
  process.exit(1);
}
console.log("PASSED — all checks OK");
process.exit(0);
