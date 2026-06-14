#!/usr/bin/env node
/**
 * AiNa App Factory — skill installer.
 *
 * Copies the bundled, self-contained skill into Claude Code's skills directory
 * so it works in ANY environment (no marketplace step needed):
 *
 *   npx aina-skill@latest            → installs to ~/.claude/skills/aina-skill (personal)
 *   npx aina-skill@latest --project  → installs to ./.claude/skills/aina-skill (this repo)
 *   npx aina-skill@latest --force    → overwrite an existing install
 *
 * Zero dependencies — Node built-ins only.
 */
import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "..", "skills", "build"); // the self-contained skill
const args = new Set(process.argv.slice(2));
const SKILL_NAME = "aina-skill";

const baseDir = args.has("--project") ? join(process.cwd(), ".claude") : join(homedir(), ".claude");
const target = join(baseDir, "skills", SKILL_NAME);

const SKIP = new Set(["__pycache__", "aina-out", ".DS_Store"]);

function log(msg) { process.stdout.write(msg + "\n"); }

if (!existsSync(SRC)) {
  console.error(`✗ bundled skill not found at ${SRC} — corrupt package?`);
  process.exit(1);
}

if (existsSync(target)) {
  if (!args.has("--force")) {
    console.error(`✗ ${target} already exists. Re-run with --force to overwrite.`);
    process.exit(1);
  }
  rmSync(target, { recursive: true, force: true });
}

mkdirSync(dirname(target), { recursive: true });
cpSync(SRC, target, {
  recursive: true,
  filter: (s) => !s.split(/[\\/]/).some((p) => SKIP.has(p) || p.endsWith(".pyc")),
});

log("");
log(`  ✓ AiNa App Factory skill installed → ${target}`);
log("");
log("  Next:");
log("    1. (Re)start Claude Code so it picks up the skill.");
log("    2. Run:  /aina-skill        then describe what to build.");
log("");
log("  Optional config (aina-build.yaml in your project, or env vars):");
log("    AINA_ENGINE=local|openrouter   OPENROUTER_API_KEY=...   AINA_OUTPUT_MODE=zip");
log("");
log("  Needs: python3 (always) · git+gh (for git-repo output) · docker/ssh (for vps deploy).");
log("");
