import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const packageRoot = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const pkg = JSON.parse(fs.readFileSync(path.join(packageRoot, "package.json"), "utf8"));
const initPy = fs.readFileSync(
  path.join(packageRoot, "src/slack_agent_cli/__init__.py"),
  "utf8",
);
const match = initPy.match(/__version__\s*=\s*["']([^"']+)["']/);

if (!match) {
  console.error("Could not read __version__ from src/slack_agent_cli/__init__.py");
  process.exit(1);
}

if (match[1] !== pkg.version) {
  console.error(
    `Version mismatch: package.json is ${pkg.version}, Python __init__.py is ${match[1]}`,
  );
  process.exit(1);
}
