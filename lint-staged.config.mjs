const BATCH_SIZE = 40;

function batchFiles(files) {
  const batches = [];

  for (let index = 0; index < files.length; index += BATCH_SIZE) {
    batches.push(files.slice(index, index + BATCH_SIZE));
  }

  return batches;
}

function batchCommands(files, command) {
  return batchFiles(files).map((batch) => `${command} ${batch.join(" ")}`);
}

const lintStagedConfig = {
  "*.{js,jsx,mjs,cjs,ts,tsx}": (files) => [
    ...batchCommands(files, "eslint --fix --max-warnings=0"),
    ...batchCommands(files, "prettier --write"),
  ],
  "*.{css,md,mdx,json,jsonc,yaml,yml}": (files) => batchCommands(files, "prettier --write"),
};

export default lintStagedConfig;
