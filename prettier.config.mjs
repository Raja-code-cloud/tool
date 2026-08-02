/** @type {import("prettier").Config} */
const config = {
  arrowParens: "always",
  bracketSameLine: false,
  endOfLine: "lf",
  importOrder: ["<BUILTIN_MODULES>", "", "<THIRD_PARTY_MODULES>", "", "^@/(.*)$", "", "^[./]"],
  importOrderParserPlugins: ["typescript", "jsx", "decorators-legacy"],
  plugins: ["@ianvs/prettier-plugin-sort-imports", "prettier-plugin-tailwindcss"],
  printWidth: 100,
  proseWrap: "preserve",
  semi: true,
  singleQuote: false,
  tabWidth: 2,
  tailwindFunctions: ["clsx", "cn", "cva"],
  trailingComma: "all",
  useTabs: false,
};

export default config;
