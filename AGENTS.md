# Project Agent Instructions

## Project

This repository distributes Sealos Cloud agent skills. It is not a deployable
application. `plugins/sealos/skills/` is the only skill implementation source:

- `use-sealos` handles interactive deploy, database, object storage, and operations.
- `sealos-deploy` handles Brain managed deployment when `SEALAI_DEPLOY_MODE=managed`.
- `k8s-kaniko-job` builds source images in the Brain sandbox.

The three `skills/` entries are symlinks to those canonical directories. Keep
the names and sibling paths intact: Brain's installer requires
`sealos-deploy/SKILL.md` and `k8s-kaniko-job/SKILL.md`, while `use-sealos`
routes between managed and interactive modes. See `BRAIN-ADAPTATION.md` for
the control-plane contract.

## Host Distribution

- Codex: `.agents/plugins/marketplace.json` selects `plugins/sealos`, whose
  `.codex-plugin/plugin.json` exposes `$sealos`. Root `plugin.json` and
  `.codex-plugin/plugin.json` support direct repository imports.
- Claude Code: `.claude-plugin/marketplace.json` selects `plugins/sealos`;
  `plugins/sealos/commands/sealos.md` provides `/sealos`.
- Cursor, Qoder, and CodeBuddy: their manifests select `plugins/sealos`.
- OpenClaw: install `plugins/sealos`, not the repository root. The root
  `package.json` is a DeepSeek Harness bundle.
- Gemini CLI and Qwen Code: context-only extensions that load `CLAUDE.md`.
- DeepSeek Harness: `index.js` registers `use-sealos` via `cordis.patch.yml`.
- `skills.sh` and generic importers: discover the three `SKILL.md` files via
  the root symlinks or canonical plugin tree.

Do not claim slash-command support for context-only hosts. Keep host versions,
repository URLs, skill inventories, and command routes in sync. The previous
eight-skill implementation is preserved on `codex/backup-before-next-20260928`;
do not reintroduce its code as a second skill source.

## Commands and Validation

There is no top-level application build. Run the narrowest relevant checks,
then the full gate for changed surfaces:

- `npm ci` and `npm test` for the DeepSeek bundle and host coverage.
- `python3 -m unittest discover -s plugins/sealos/skills/use-sealos/scripts -p 'test_*.py' -v` for the Sealos API.
- `python3 -m py_compile` for changed Python files.
- `node --check index.js` and `shellcheck` for changed shell scripts.
- `python3 scripts/validate-host-distribution.py` when host manifests,
  commands, skill inventory, or distribution metadata change.
- Test both local-directory and GitHub-source `skills.sh` discovery before
  releasing a change to the three-skill pack.

## Editing Discipline

- Inspect `git status --short` and relevant diffs before editing. Preserve
  unrelated user changes and untracked files.
- Keep behavior in the owning skill and host details in adapters or manifests.
- Use English for code, comments, commit messages, and pull requests.
- Node helpers use ESM and two-space indentation; Python uses four-space
  indentation and standard-library tools where the existing code does.
- Keep secrets and complete connection strings out of committed files,
  diagnostics, and user-facing output.

## Runtime Safety

- Require explicit user confirmation before deleting Kubernetes resources,
  databases, or buckets; changing public access; rotating credentials; or
  installing system tools. In managed mode, use a control-plane input or
  explicit task authorization; if it is unavailable, stop without deletion.
- Scope Kubernetes operations to the selected namespace and named app.
  Inspect the live footprint before mutation.
- For interactive Sealos access use the selected namespace-scoped kubeconfig.
  In Brain managed mode use the injected `KUBECONFIG` as-is and never log in.
- Accept a deployment only after the actual URL, relevant logs, workload
  readiness, and resource footprint are verified. Never print kubeconfig,
  OAuth tokens, database passwords, bucket secrets, or `.env` values.

The `brain-deploy-preview` branch is a separate prepare-only workflow. This
replacement changes `main` only; do not merge it into preview mechanically.
