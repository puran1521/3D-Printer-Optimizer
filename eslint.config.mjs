import { defineConfig } from "eslint/config";
import globals from "globals";
import js from "@eslint/js";
import pluginReact from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs,jsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node
      },
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      }
    },
    plugins: {
      react: pluginReact,
      "react-hooks": reactHooks
    },
    rules: {
      // React Rules
      "react/prop-types": "warn",
      "react/jsx-uses-react": "error",
      "react/jsx-uses-vars": "error",
      
      // React Hooks Rules
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",
      
      // General Rules
      "no-unused-vars": "warn",
      "no-console": process.env.NODE_ENV === "production" ? "error" : "warn"
    },
    settings: {
      react: {
        version: "detect"
      }
    }
  }
]);