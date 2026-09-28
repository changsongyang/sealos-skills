---
name: sealos
description: Deploy and operate apps, databases, and object storage on Sealos Cloud.
argument-hint: "[task or project path]"
---

# Sealos

Use `../skills/use-sealos/SKILL.md` as the entry for interactive Sealos work.
Read only the references needed for the request. When
`SEALAI_DEPLOY_MODE=managed`, follow `../skills/sealos-deploy/SKILL.md`
instead and honor its Brain control-plane contract.

Route deployment, database, object storage, status, logs, and troubleshooting
requests through `use-sealos`. Follow its credential, namespace, confirmation,
and verification rules. Do not execute the Brain-only `k8s-kaniko-job` path in
an interactive session.
