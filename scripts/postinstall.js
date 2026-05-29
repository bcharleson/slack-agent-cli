import { spawnSync } from "node:child_process";
import fs from "node:fs";

import { findPython } from "../npm/find-python.js";
import { packageRoot, pythonModulesDir } from "../npm/paths.js";

if (process.env.SLACK_AGENT_CLI_SKIP_POSTINSTALL === "1") {
  process.exit(0);
}

const python = findPython();
if (!python) {
  console.warn(
    "[slack-agent-cli] Python 3.10+ not found. Install Python, then run:\n" +
      "  npm rebuild slack-agent-cli",
  );
  process.exit(0);
}

fs.mkdirSync(pythonModulesDir, { recursive: true });

const install = spawnSync(
  python,
  [
    "-m",
    "pip",
    "install",
    packageRoot,
    "--target",
    pythonModulesDir,
    "--upgrade",
    "--disable-pip-version-check",
    "--no-warn-script-location",
  ],
  { stdio: "inherit" },
);

if (install.status !== 0) {
  console.warn(
    "[slack-agent-cli] Could not install Python dependencies automatically.\n" +
      "Try: python3 -m pip install " +
      packageRoot,
  );
  process.exit(0);
}
