import { spawnSync } from "node:child_process";

const CANDIDATES = ["python3.12", "python3.11", "python3.10", "python3", "python"];

export function findPython() {
  for (const command of CANDIDATES) {
    const result = spawnSync(command, ["--version"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    });

    if (result.status !== 0) {
      continue;
    }

    const versionText = `${result.stdout}${result.stderr}`;
    const match = versionText.match(/Python (\d+)\.(\d+)/);
    if (!match) {
      continue;
    }

    const major = Number(match[1]);
    const minor = Number(match[2]);
    if (major > 3 || (major === 3 && minor >= 10)) {
      return command;
    }
  }

  return null;
}
