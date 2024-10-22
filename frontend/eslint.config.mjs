import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "typescript-eslint";


export default [
  {
    rules: {
      'no-unused-vars': ["error", {"argsIgnorePattern": "^_"}],
      '@typescript-eslint/no-unused-vars': ["error", {"argsIgnorePattern": "^_"}]
    }
  },
  {files: ["**/*.{js,ts}"]},
  {languageOptions: {globals: globals.browser}},
  pluginJs.configs.recommended,
  ...tseslint.configs.recommended,
];
