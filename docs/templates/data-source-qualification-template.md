# Data Source Qualification Template

<details open>
<summary><b>Contents</b></summary>

- [Source Identity](#source-identity)
- [Intended Use](#intended-use)
- [Terms and Rights](#terms-and-rights)
- [Coverage](#coverage)
- [Instrument Identity](#instrument-identity)
- [Time and Availability Semantics](#time-and-availability-semantics)
- [Corporate Actions and Adjustments](#corporate-actions-and-adjustments)
- [Quality and Completeness](#quality-and-completeness)
- [Revision Behavior](#revision-behavior)
- [API Operations](#api-operations)
- [Security and Privacy](#security-and-privacy)
- [Cost and Sustainability](#cost-and-sustainability)
- [Verification Evidence](#verification-evidence)
- [Limitations](#limitations)
- [Qualification Decision](#qualification-decision)
- [Review](#review)

</details>

---

**Qualification ID:** `DATA-SOURCE-TBD`  
**Provider:** `TBD`  
**Product or endpoint:** `TBD`  
**Review date:** `TBD`  
**Status:** `NOT_APPROVED`

## Source Identity

| Field | Value |
|---|---|
| Provider legal or product name | `TBD` |
| Dataset or API product | `TBD` |
| Official documentation | `TBD` |
| Contract or terms version and date | `TBD` |
| Account or subscription class | `TBD` |
| Owner | `TBD` |

Do not include credentials, signed URLs, full subscription identifiers, or restricted contract content. Use protected references.

## Intended Use

| Use | Required | Source permits | Evidence |
|---|---|---|---|
| Local historical research | `TBD` | `TBD` | `TBD` |
| Immutable raw and curated storage | `TBD` | `TBD` | `TBD` |
| Backups and reproducible replay | `TBD` | `TBD` | `TBD` |
| Paper decision support | `TBD` | `TBD` | `TBD` |
| Separately approved Stage 5 use | `TBD` | `TBD` | `TBD` |
| Private reports and adviser export | `TBD` | `TBD` | `TBD` |

**Exact approved scope if qualified:** `TBD`

## Terms and Rights

- Automated retrieval allowed and rate terms: `TBD`
- Raw storage allowed: `TBD`
- Derived storage allowed: `TBD`
- Backup and retention allowed: `TBD`
- Private display allowed: `TBD`
- Redistribution or public repository restriction: `TBD`
- Use after subscription termination: `TBD`
- Attribution requirement: `TBD`
- Exchange or non-display agreement requirement: `TBD`
- Material term-change notification method: `TBD`

**Terms review result:** `NOT_APPROVED`

## Coverage

| Dimension | Claimed coverage | Measured coverage | Gap |
|---|---|---|---|
| Instruments and exchanges | `TBD` | `TBD` | `TBD` |
| Date history | `TBD` | `TBD` | `TBD` |
| Daily OHLCV fields | `TBD` | `TBD` | `TBD` |
| Raw and adjusted series | `TBD` | `TBD` | `TBD` |
| Corporate actions | `TBD` | `TBD` | `TBD` |
| Delistings and failed instruments | `TBD` | `TBD` | `TBD` |
| Point-in-time universe membership | `TBD` | `TBD` | `TBD` |
| Holidays and half-days | `TBD` | `TBD` | `TBD` |

## Instrument Identity

- Provider symbol uniqueness and reuse behavior: `TBD`
- Exchange or listing identity: `TBD`
- Stable provider instrument ID: `TBD`
- Currency field: `TBD`
- Symbol-change history: `TBD`
- ETF domicile and instrument metadata needed for review: `TBD`
- Mapping to internal instrument registry: `TBD`

## Time and Availability Semantics

| Field or event | Provider definition | Verified behavior | Canonical mapping |
|---|---|---|---|
| Daily bar timestamp | `TBD` | `TBD` | `TBD` |
| Session date and timezone | `TBD` | `TBD` | `TBD` |
| Publication or completion time | `TBD` | `TBD` | `available_at_utc = TBD` |
| Revision timestamp | `TBD` | `TBD` | `TBD` |
| Corporate-action announcement and effective time | `TBD` | `TBD` | `TBD` |

Test at least one normal session, half-day, holiday boundary, and both daylight-saving transition periods.

## Corporate Actions and Adjustments

- Split coverage and ratio semantics: `TBD`
- Cash dividend coverage, currency, ex-date, and pay date: `TBD`
- Symbol changes: `TBD`
- Mergers, spinoffs, and delistings: `TBD`
- Adjustment-factor formula: `TBD`
- Dividend-adjusted versus split-adjusted behavior: `TBD`
- Adjusted-volume behavior: `TBD`
- Historical restatement behavior: `TBD`
- Independent reconciliation sample: `TBD`

## Quality and Completeness

Record the result of every mandatory data validation:

| Validation | Sample result | Exceptions | Qualification effect |
|---|---|---|---|
| DV-001 duplicates | `NOT_RUN` | `TBD` | `TBD` |
| DV-002 expected sessions | `NOT_RUN` | `TBD` | `TBD` |
| DV-003 UTC and session mapping | `NOT_RUN` | `TBD` | `TBD` |
| DV-004 OHLC relationships | `NOT_RUN` | `TBD` | `TBD` |
| DV-005 positivity and finite values | `NOT_RUN` | `TBD` | `TBD` |
| DV-006 extreme return and action evidence | `NOT_RUN` | `TBD` | `TBD` |
| DV-007 adjustment reconciliation | `NOT_RUN` | `TBD` | `TBD` |
| DV-008 volume behavior | `NOT_RUN` | `TBD` | `TBD` |
| DV-009 null and fill behavior | `NOT_RUN` | `TBD` | `TBD` |
| DV-010 expected counts | `NOT_RUN` | `TBD` | `TBD` |
| DV-011 manifest and hash reload | `NOT_RUN` | `TBD` | `TBD` |
| DV-012 revision detection | `NOT_RUN` | `TBD` | `TBD` |

## Revision Behavior

| Question | Finding and evidence |
|---|---|
| Can historical bars change? | `TBD` |
| Can actions or adjustments change? | `TBD` |
| Is a correction feed or revision timestamp available? | `TBD` |
| Does an identical request return deterministic content? | `TBD` |
| How will overlapping pulls be compared? | `TBD` |
| How are users notified of corrections? | `TBD` |

Attach an unchanged re-pull and a simulated or observed changed-history exercise.

## API Operations

- Authentication method without recording the secret: `TBD`
- Official hosts and TLS behavior: `TBD`
- Request and response formats: `TBD`
- Pagination: `TBD`
- Rate limits and headers: `TBD`
- Retry-safe operations: `TBD`
- Timeout and outage behavior: `TBD`
- Provider status and support channel: `TBD`
- Historical and current endpoint consistency: `TBD`
- Cache or CDN staleness behavior: `TBD`

## Security and Privacy

- Least-privileged credential support: `TBD`
- Credential rotation and revocation: `TBD`
- Sensitive account or request fields: `TBD`
- Logging redaction requirements: `TBD`
- Raw-payload access controls: `TBD`
- Provider breach notification: `TBD`

## Cost and Sustainability

| Cost | Amount and currency | Frequency or unit | Change risk |
|---|---|---|---|
| Subscription | `TBD` | `TBD` | `TBD` |
| Exchange or non-display | `TBD` | `TBD` | `TBD` |
| Request or overage | `TBD` | `TBD` | `TBD` |
| Historical or action add-on | `TBD` | `TBD` | `TBD` |
| Exit or retention cost | `TBD` | `TBD` | `TBD` |

State whether the cost is sustainable under the project budget and what export exists if the source is discontinued: `TBD`.

## Verification Evidence

| Evidence | Reference or hash | Result |
|---|---|---|
| Terms review | `TBD` | `NOT_RUN` |
| Reference ETF ten-year pull | `TBD` | `NOT_RUN` |
| Twelve validation report | `TBD` | `NOT_RUN` |
| Independent price and action sample | `TBD` | `NOT_RUN` |
| Timestamp and availability sample | `TBD` | `NOT_RUN` |
| Revision comparison | `TBD` | `NOT_RUN` |
| Adapter timeout rate and pagination tests | `TBD` | `NOT_RUN` |

## Limitations

| Limitation | Affected use or claim | Bias or risk | Can it reverse a result | Required control |
|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `YES` or `NO` | `TBD` |

A limitation that can reverse a promotable conclusion makes that use `NOT_APPROVED` until resolved.

## Qualification Decision

Select one per exact use:

- `APPROVED`: terms and measured behavior support the defined use.
- `EXPLORATORY_ONLY`: technically usable but bias or rights block promotion and trading decisions.
- `NOT_APPROVED`: mandatory evidence, rights, or quality is absent.
- `REVOKED`: previously approved use is no longer permitted or reliable.

**Decision:** `NOT_APPROVED`  
**Approved use if any:** `NONE`  
**Blocking gaps:** `TBD`  
**Review trigger or expiry:** `TBD`

## Review

| Role | Name or protected reference | Decision | Date |
|---|---|---|---|
| Data implementation owner | `TBD` | `TBD` | `TBD` |
| Project owner | `TBD` | `APPROVE_SCOPE`, `REJECT`, or `REQUIRE_MORE_EVIDENCE` | `TBD` |
| Legal or contract reviewer if needed | `TBD` | `TBD` | `TBD` |

**Immutable qualification hash:** `TBD`
