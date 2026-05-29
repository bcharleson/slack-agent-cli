#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

import { findPython } from "../npm/find-python.js";
import { packageRoot, pythonModulesDir } from "../npm/paths.js";

const args = process.argv.slice(2);

function buildEnv() {
  const env = { ...process.env };

  if (fs.existsSync(pythonModulesDir)) {
    const existing = env.PYTHONPATH ? `${env.PYTHONPATH}${path.delimiter}` : "";
    env.PYTHONPATH = `${pythonModulesDir}${path.delimiter}${existing}${packageRoot}`;
  } else {
    const existing = env.PYTHONPATH ? `${env.PYTHONPATH}${path.delimiter}` : "";
    env.PYTHONPATH = `${packageRoot}${path.delimiter}${existing}`;
  }

  return env;
}

function run() {
  const python = findPython();
  if (!python) {
    console.error(
      "slack-agent-cli requires Python 3.10 or newer.\n" +
        "Install Python from https://www.python.org/downloads/ and re-run npm install -g slack-agent-cli",
    );
    process.exit(1);
  }

  const result = spawnSync(python, ["-m", "slack_agent_cli.cli.main", ...args], {
    stdio: "inherit",
    env: buildEnv(),
    cwd: packageRoot,
  });

  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }

  process.exit(result.status ?? 1);
}

run();
