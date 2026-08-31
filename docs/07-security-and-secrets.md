# Security and Secrets Specification

<details open>
<summary><b>Contents</b></summary>

- [Purpose](#purpose)
- [Security Objectives](#security-objectives)
- [Threat Model](#threat-model)
- [Assets and Trust Boundaries](#assets-and-trust-boundaries)
- [Credential Management](#credential-management)
- [Environment and Endpoint Separation](#environment-and-endpoint-separation)
- [Authorization and Least Privilege](#authorization-and-least-privilege)
- [Configuration Integrity](#configuration-integrity)
- [Logging and Redaction](#logging-and-redaction)
- [Dependency and Supply Chain Security](#dependency-and-supply-chain-security)
- [Local Storage and Backups](#local-storage-and-backups)
- [Development and Test Safety](#development-and-test-safety)
- [Security Incident Response](#security-incident-response)
- [Verification Checklist](#verification-checklist)
- [Open Decisions](#open-decisions)

</details>

---

**Version:** 1.0  
**Date:** 30 August 2026  
**Status:** Proposed baseline  
**Related:** [Architecture](02-architecture.md) | [Execution Specification](06-execution-and-reconciliation.md) | [Risk Specification](03-risk-and-safety.md)

## Purpose

This specification protects broker credentials, account identity, trading controls, research evidence, and operational records. It focuses on practical threats to a single-owner system while defining stronger controls as prerequisites for a separately approved future stage.

## Security Objectives

1. No secret appears in source control, logs, exceptions, reports, fixtures, process arguments, or support bundles.
2. Paper credentials cannot authorize live trading.
3. A configuration or endpoint error cannot silently redirect a paper process to a live account.
4. Only the expected owner-controlled process can submit orders for the configured strategy and account namespace.
5. Published data, configuration, approvals, and evidence can be checked for unauthorized or accidental change.
6. Loss of confidentiality, integrity, or availability causes no new market exposure.
7. Credential rotation and incident recovery are documented and tested before unattended operation.

## Threat Model

| Threat | Example | Primary controls |
|---|---|---|
| Secret disclosure | API key committed, printed, included in traceback, or copied into a report | Secret provider, ignore rules, allowlisted logging, secret scanning, rotation |
| Environment confusion | Paper code points at a live endpoint or uses live credentials | Exact endpoint allowlist, credential namespaces, account-mode verification, live capability denial |
| Duplicate or unauthorized process | Two schedulers run the same strategy against one account | Single-writer lock, account namespace, deterministic client IDs, alerts |
| Local compromise | Malware or another local user reads credentials or changes configuration | OS access controls, encryption, dedicated account, patching, integrity checks |
| Dependency compromise | Malicious or hijacked package executes during install or runtime | Lockfile, hashes where supported, minimal dependencies, review, vulnerability scanning |
| Data or configuration tampering | Snapshot, risk limit, or approval changed after review | Content hashes, immutable artefacts, signed or owner-approved release manifest |
| Broker API impersonation | DNS, proxy, or certificate attack | TLS verification, official hosts, no certificate bypass, egress allowlist where practical |
| Log or backup disclosure | Account data copied to cloud or shared folder unencrypted | Data minimization, encryption, restricted destinations, retention policy |
| Alert-channel compromise | Malicious command encoded in an inbound message | Alerts are outbound-only; no trading command from chat or email in initial scope |
| Denial of service | Provider, network, disk, or alert system unavailable | Fail closed, independent watchdog, bounded retries, disk monitoring, recovery runbooks |

The initial system does not expose a public web server, accept remote trading commands, process third-party funds, or support multiple users. Adding any of those requires a new threat model.

## Assets and Trust Boundaries

| Asset | Sensitivity | Integrity need | Storage rule |
|---|---|---|---|
| Broker API secret | Critical | Critical | Runtime secret provider only; never project files |
| Broker account identity | Sensitive | Critical | Approved local registry; redact in reports |
| Risk profiles and approvals | Sensitive | Critical | Source-controlled template plus immutable approved release artefact |
| Intent order and fill journal | Sensitive | Critical | Restricted SQLite store and encrypted backup |
| Market data snapshots | Licensed | Critical for evidence | Content-addressed storage under provider terms |
| Strategy source and parameters | Confidential | Critical | Repository and release hash |
| Tax and recordkeeping exports | Highly sensitive | Critical | Separate encrypted restricted location |
| Logs and reports | Sensitive | Critical | Allowlisted schema, redaction, retention and access controls |
| Test fixtures | Non-sensitive | High | Synthetic or irreversibly redacted; safe for repository |

Trust boundaries exist at every provider API, local secret provider, filesystem, scheduler, backup destination, and alert service. Data is validated and normalized when crossing a boundary.

## Credential Management

- Separate credentials by environment. The paper process accepts only a credential reference from the `paper` namespace.
- Do not store credential values in YAML, Markdown, notebook output, command history, task definitions, screenshots, or `.env.example`.
- A local `.env` file may be used only for short-lived development if it is ignored before creation, access-restricted, never backed up or synced, and covered by secret scanning. It is not the preferred unattended store.
- Prefer Windows Credential Manager or another owner-approved encrypted secret store for scheduled paper operation. A cloud secret manager is considered only with a later cloud deployment.
- Inject secrets through the secret provider after process start. Do not pass them as command-line arguments.
- Domain code receives an authenticated adapter, never raw credential strings.
- Cache secrets only in process memory for the minimum lifetime supported by the SDK.
- Never log request headers, signed URLs, authorization objects, environment dumps, or raw SDK exceptions before redaction.
- Rotation must be possible without editing source or historical configuration.

Credential lifecycle:

1. Create the least-privileged paper credential through the broker.
2. Store it directly in the approved provider without passing it through repository files.
3. Record only its non-secret fingerprint, environment, owner, creation date, and review date.
4. Verify paper account identity in a read-only startup check.
5. Rotate on suspected exposure, owner change, broker instruction, or the approved periodic schedule.
6. Revoke the old credential and prove it no longer works.

## Environment and Endpoint Separation

The initial release is built and configured for paper operation only.

| Control | Requirement |
|---|---|
| Mode guard | `PAPER` must be explicit; unknown mode halts |
| Endpoint | Exact scheme and host allowlist; redirects to unapproved hosts fail |
| Credential namespace | Paper provider path only |
| Account check | Returned account fingerprint must match approved paper account |
| Capability | Live-order capability absent or denied in the paper release |
| UI and reports | Every session and order artefact displays `PAPER` prominently |
| Tests | Wrong endpoint, credential, account, redirect, and mode all fail before submission |

Future live operation uses separate credentials, configuration roots, approval records, state storage, report paths, and preferably a separate executable capability or deployment account. It must not share a mutable `.env` switch with paper.

## Authorization and Least Privilege

- The current owner is the only human operator.
- Use a dedicated OS account for scheduled unattended operation where practical.
- The trading process gets read access to approved data and config, write access only to its state, log, report, heartbeat, and lock locations, and no broad administrative rights.
- The watchdog gets only the minimum broker capability needed to inspect and cancel approved working orders. If the broker cannot scope this separately, record that limitation and protect the shared credential accordingly.
- Research processes never receive broker credentials.
- CI and offline tests use fakes and synthetic credentials only.
- Backup jobs can read protected state but cannot submit broker orders.
- Alert providers are outbound notification channels and cannot invoke trading actions.

No process is run with elevated Windows privileges merely to avoid fixing file or scheduler permissions.

## Configuration Integrity

- Configuration models reject unknown keys, missing values, invalid units, and unknown schema versions.
- Each effective configuration is rendered without secret values, canonicalized, and hashed.
- Approved risk and strategy hashes are recorded in the stage or release manifest.
- The process prints only non-sensitive configuration identity and selected mode, not a full environment dump.
- A dirty source tree is allowed for local research only and is visibly labeled; paper promotion evidence requires a known source revision and release manifest.
- A change to mode, endpoint, account, strategy, risk, calendar, data source, or alert routing opens a fresh review.
- Time-of-check and time-of-use changes are controlled by reading approved configuration once into an immutable runtime object.
- File permissions deny modification by unrelated local users where supported.

## Logging and Redaction

Use allowlisted structured fields. Never serialize arbitrary SDK objects, HTTP sessions, environment mappings, exception `repr` output, or configuration objects.

Always redact or omit:

- API keys, secrets, tokens, authorization headers, cookies, signed query values, and credential paths that reveal secret names unnecessarily.
- Full broker account numbers; use an approved short fingerprint.
- Personal contact details and tax identifiers.
- Raw request or response bodies unless a schema-specific sanitizer has run.
- Local user paths in externally shareable reports where they reveal identity.

Redaction must cover common secret formats and canary values in nested mappings, arrays, URLs, headers, exceptions, and multiline strings. A value discovered to be secret is rotated even if the log was believed private.

Security events use stable codes and include UTC time, session, component, severity, non-secret subject fingerprint, action, and correlation ID. Redaction failure is itself a high-severity halt condition for paper operation.

## Dependency and Supply Chain Security

- Keep runtime dependencies minimal and justify each direct package.
- Pin exact resolved versions in a lockfile and preserve the package source index.
- Use hashes for downloaded distributions where the selected toolchain supports a maintainable workflow.
- Install from official TLS package indexes; do not use unreviewed archives or copy-pasted install scripts.
- Run automated dependency vulnerability and secret scans in CI.
- Review direct dependency ownership, maintenance, license, release history, and transitive footprint before adoption.
- Separate optional research dependencies from the paper runtime environment.
- Treat broker SDK updates as behavioral changes requiring adapter contract tests.
- Apply OS and Python security updates on a reviewed schedule, with faster response for exploitable credential or remote-code issues.
- Generate a dependency inventory for each paper release.

A scanner finding is triaged by exploitability and exposure, but critical issues in network-facing or credential-handling dependencies block release until resolved or explicitly isolated.

## Local Storage and Backups

- Runtime state and secrets must not reside in a repository or broadly synchronized consumer folder.
- Use OS access control lists to restrict state, logs, reports, and backups to the operating account and owner.
- Encrypt backups containing broker, fill, account, or tax records.
- Store backup encryption keys separately from backup files.
- Use atomic writes for manifests, heartbeat, and release pointers.
- Monitor disk space; inability to persist intent or audit evidence blocks order submission.
- Retain hashes and restore instructions with backups.
- Test restoration into an isolated path without broker credentials.
- Securely remove expired sensitive records according to the retention policy and provider terms, while preserving legally required records.

OneDrive or another sync service is not assumed to provide sufficient secrecy, immutability, or transactional behavior for live state. Source documentation may remain in the workspace; runtime paths are selected separately before implementation.

## Development and Test Safety

- Unit and integration tests default to no network.
- Paper sandbox tests require an explicit marker and a verified paper account guard.
- Production or live hostnames are denied in all test environments.
- Fixtures use synthetic symbols, account IDs, keys, fills, and personal data unless a redaction review approves a minimal captured case.
- Notebooks cannot import unattended broker credentials or submit orders.
- Debuggers and crash dumps are treated as potential secret stores and disabled or protected for credential-handling processes.
- Screen recordings and screenshots of broker interfaces are reviewed for account and credential information before sharing.
- Pre-commit and CI scans reject likely secrets, private keys, tokens, and credential files.
- Security tests use recognizable canary secrets and confirm that none reaches captured output.

## Security Incident Response

For suspected credential or account compromise:

1. Activate the operator kill control and stop schedulers.
2. Use the broker interface through a trusted device to inspect and, if necessary, cancel working orders under owner judgment.
3. Revoke affected credentials immediately; do not wait to prove exposure.
4. Preserve relevant logs and state read-only without spreading secret values.
5. Verify account activity, positions, fills, withdrawals, profile changes, and authorized devices.
6. Rotate broker, alert, backup, and other linked credentials as the incident scope requires.
7. Identify entry point, exposed assets, duration, and market or data impact.
8. Correct the cause and add a regression or detection control.
9. Restore from verified sources and re-run full startup reconciliation in `PAPER` mode.
10. Document owner approval before unattended operation resumes.

For a live-account incident in a future stage, use broker emergency support and applicable legal or regulatory reporting guidance. This document does not replace provider-specific response procedures.

## Verification Checklist

- [ ] Repository and history secret scan returns no verified secret.
- [ ] Ignore rules cover local secret and runtime-state paths before those paths are created.
- [ ] Canary API keys are absent from logs, reports, exceptions, test output, and support bundles.
- [ ] Paper release rejects live endpoint, wrong account, wrong credential namespace, redirect, and unknown mode.
- [ ] Research and CI environments can run without broker credentials.
- [ ] Configuration and release hashes change on protected-field modification.
- [ ] Scheduler and runtime operate without administrator privileges.
- [ ] Dependency lock, inventory, license review, and vulnerability scan exist for the paper release.
- [ ] Encrypted backup and isolated restore tests pass.
- [ ] Credential rotation is rehearsed with paper credentials.
- [ ] Security incident tabletop exercise is completed before unattended paper operation.
- [ ] No inbound alert message can trigger a trading command.

## Open Decisions

| Decision | Needed by | Blocking effect |
|---|---|---|
| Select unattended local secret provider | Broker adapter integration | Blocks scheduled paper authentication |
| Select runtime directory outside synchronized source workspace | Stateful implementation | Blocks storage hardening |
| Define paper credential rotation interval | Unattended paper start | Blocks credential lifecycle sign-off |
| Choose encrypted backup technology and key location | State acceptance | Blocks restore sign-off |
| Choose primary and secondary alert providers | Watchdog implementation | Blocks dead-man acceptance |
| Confirm broker support for scoped cancel-only credentials | Watchdog implementation | Determines privilege limitation |
