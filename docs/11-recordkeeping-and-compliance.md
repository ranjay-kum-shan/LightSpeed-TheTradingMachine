# Recordkeeping and Compliance Plan

<details open>
<summary><b>Contents</b></summary>

- [Purpose and Disclaimer](#purpose-and-disclaimer)
- [Applicability](#applicability)
- [Record Classes](#record-classes)
- [Order and Fill Records](#order-and-fill-records)
- [Cash Fees FX and Corporate Actions](#cash-fees-fx-and-corporate-actions)
- [Tax Lot and Disposal Records](#tax-lot-and-disposal-records)
- [Statements and Reconciliation](#statements-and-reconciliation)
- [UK Tax Review](#uk-tax-review)
- [Broker and Product Review](#broker-and-product-review)
- [Market Data Licensing](#market-data-licensing)
- [Personal Use Boundary](#personal-use-boundary)
- [Retention Access and Export](#retention-access-and-export)
- [Periodic Review](#periodic-review)
- [Preactivation Checklist](#preactivation-checklist)
- [Open Decisions](#open-decisions)

</details>

---

**Version:** 1.0  
**Date:** 30 August 2026  
**Status:** Planning baseline; professional review pending  
**Related:** [Project Charter](../CHARTER.md) | [Security Specification](07-security-and-secrets.md) | [Rollout Plan](10-paper-and-live-rollout.md)

## Purpose and Disclaimer

This plan defines the records and reviews needed to explain trades, reconcile broker activity, support tax preparation, and demonstrate compliance with broker and data terms. It is engineering documentation, not legal, regulatory, tax, accounting, or investment advice.

> For informational purposes only. This document does not constitute legal, regulatory, tax, accounting, financial, or investment advice.

Tax rates, allowances, product rules, residency facts, broker eligibility, and regulatory treatment change. The owner must verify current primary sources and obtain qualified UK professional advice before any separately approved Stage 5 operation.

## Applicability

The current design assumes:

- One UK-resident owner trading only the owner's account.
- Liquid US-listed ETFs held directly through an approved broker.
- Long-only, unleveraged daily strategies.
- GBP as the proposed reporting currency, pending owner approval.
- Paper trading during the implementation and validation stages.
- No client money, advice, signals service, copying service, pooled capital, or trading for another person.

A change in residence, account wrapper, beneficial owner, instrument, broker entity, leverage, shorting, derivatives, employment restriction, or commercial use requires a fresh applicability review.

## Record Classes

| Record class | Examples | System of record |
|---|---|---|
| Identity and approvals | Account fingerprint, broker entity, charter, stage and risk approvals | Approval registry and immutable gate bundle |
| Strategy evidence | Thesis, registration, parameters, trials, reports, promotion decision | Experiment store and immutable artefacts |
| Market data lineage | Provider, terms reference, request, raw hash, dataset hash, actions, calendar | Dataset manifests |
| Decisions and risk | Inputs, decision, reason, risk snapshot, limit result | Structured audit log |
| Orders and fills | Intent, client and broker IDs, lifecycle, fills, cancel and reject events | Trading state journal |
| Positions and cash | Broker and internal snapshots, marks, PnL, capital flows | Ledger and reconciliation reports |
| Costs and currency | Commission, spread estimate, fees, taxes, financing, FX source and rate | Fill and cash journals |
| Corporate actions | Splits, dividends, mergers, symbol changes, delistings | Action dataset and ledger events |
| Broker evidence | Contract notes, statements, activity exports, account notices | Restricted document archive |
| Tax workpapers | Disposal matching, pooled basis, income, gains and losses, summaries | Separate restricted tax archive |
| Operations and incidents | Daily reports, alerts, backups, recoveries, changes, incidents | Report and incident stores |

Records are linked by stable IDs rather than filename inference. A corrected record supersedes and references the original; it does not erase history.

## Order and Fill Records

For every logical order, retain:

- Mode, account fingerprint, strategy ID and version, session, decision ID, intent ID, logical order ID, client order ID, and broker order ID.
- Instrument ID, dated symbol, exchange, currency, side, original quantity, order type, prices, time in force, purpose, and all lifecycle timestamps in UTC.
- Risk decision ID, effective risk-profile hash, projected position and exposure, and result reason code.
- Every submission attempt and whether its outcome was acknowledged, rejected, or initially unknown.
- Cancel and replacement relationships.

For every fill, retain:

- Stable broker fill or activity ID and linked client, broker, logical, and strategy IDs.
- UTC timestamp plus exchange-local date needed for statement and tax interpretation.
- Instrument identity, side, quantity, price, trade currency, and gross consideration.
- Commission, venue or regulatory fees, transaction taxes, financing, borrow, and other broker charges as separate fields.
- Broker-supplied and system-calculated net cash effect.
- FX rate, source, timestamp, conversion fee, and GBP-equivalent values when the base currency is approved as GBP.
- Settlement date or status where supplied.
- Import source, retrieval timestamp, and reconciliation state.

Decimal source values are preserved at full available precision. Display rounding is not used for accounting or tax calculations.

## Cash Fees FX and Corporate Actions

- Record deposits and withdrawals separately from PnL with bank or broker reference and effective time.
- Record interest, subscription charges, data fees, financing, borrow fees, and taxes by explicit type.
- Preserve trade-currency and base-currency amounts together; never overwrite one with a conversion.
- Define one approved FX source and conversion-time rule for internal reporting.
- Preserve broker FX conversions as separate cash events and compare them with the internal reporting conversion.
- Record cash dividends with gross amount, withholding tax, net amount, currency, ex-date, pay date, and source.
- Record splits as quantity and basis transformations without artificial gain.
- Preserve merger, spinoff, symbol-change, and delisting evidence; unsupported events require manual professional review before tax export.
- Reconcile fees and cash events to broker statements, not only order endpoints.

Fixed project expenses such as data or hosting are tracked separately from trade PnL. Their tax deductibility is not assumed.

## Tax Lot and Disposal Records

For direct holdings potentially subject to UK Capital Gains Tax, the engineering design must be able to retain acquisitions and disposals at sufficient detail for the applicable UK share-identification rules. Based on the reviewed plan, the expected matching order to verify with a professional is:

1. Acquisitions on the same day as the disposal.
2. Acquisitions in the following 30 days.
3. The remaining Section 104 pooled holding.

The implementation must not use a generic FIFO report as a substitute without professional confirmation. It should:

- Keep exact trade and settlement dates, quantity, consideration, allowable broker costs, currency, and GBP conversion evidence.
- Maintain a replayable per-instrument acquisition pool.
- Delay final matching where later acquisitions can affect an earlier disposal.
- Treat partial disposals, fractional units, reorganizations, returns of capital, and transferred holdings explicitly.
- Reconcile opening and closing pools to prior filed workpapers.
- Version calculation rules and preserve the rule version used in an export.
- Produce an exception list for missing FX, action, fee, or basis facts.

An accountant-ready export is an aid to review, not an assertion that the system has determined the owner's tax liability.

## Statements and Reconciliation

At least monthly during paper and after every statement period in a separately approved later stage:

1. Archive broker statements, contract notes or trade confirmations, activity exports, and fee schedules where available.
2. Verify document origin, account fingerprint, period, completeness, and file hash.
3. Compare all broker orders and fills with the event journal.
4. Compare opening and closing positions, cash by currency, equity, dividends, interest, fees, taxes, FX, deposits, and withdrawals.
5. Investigate every difference and preserve both views.
6. Record correction events with evidence; never edit imported broker facts silently.
7. Sign the period reconciliation and carry forward only a proven opening state.

The broker statement is critical external evidence but may not contain every strategy, decision-time, or tax-calculation field, which is why the internal journal is retained.

## UK Tax Review

Before Stage 5, obtain current professional confirmation of at least:

- Owner residence and domicile facts relevant to the account.
- Tax treatment of the exact ETF domicile, distributions, and broker entity.
- Capital Gains Tax rates and annual exempt amount for the applicable tax year.
- Same-day, following-30-day, and Section 104 matching rules and treatment of fractional shares.
- GBP conversion source and acceptable date or transaction-time convention.
- Dividend and foreign withholding treatment.
- Whether any expenses or losses are allowable and how they must be evidenced.
- Self Assessment registration and reporting obligations.
- Required record-retention period measured from the applicable filing date.
- Treatment of an ISA or another wrapper if one is ever proposed and whether API trading is permitted.
- Consequences of later introducing CFDs, spread betting, margin, shorting, futures, options, or crypto.

Do not hard-code figures from the 30 August 2026 planning review into long-lived logic. Store tax-year rules as versioned data with source and reviewer references.

## Broker and Product Review

Record and reverify:

- Contracting broker legal entity, regulator, account classification, residency eligibility, and relevant investor protections.
- Whether API and automated trading are permitted for the account and product.
- Paper-versus-real endpoint and fill behavior limitations.
- Order types, fractional trading, market hours, corporate actions, shorting and margin defaults, rate limits, and outage procedures.
- Commission, spread, FX, data, custody, inactivity, financing, and transfer fee schedules.
- Best-execution disclosures and order-routing behavior relevant to the strategy.
- Account statement, confirmation, and historical export availability.
- Emergency support, credential-revocation, order-cancel, and account-restriction procedures.
- Broker changes to terms, APIs, symbols, or permissions that can invalidate implementation assumptions.

Do not elect a professional or otherwise less-protected client classification merely to obtain leverage or features without independent professional review and a charter change.

## Market Data Licensing

For every source, retain a dated review of whether terms permit:

- Automated downloading at the intended rate.
- Local raw and derived storage.
- Historical replay and backup.
- Use for paper and any separately approved future account operation.
- Display in private reports.
- Sharing only derived, redacted evidence with advisers or maintainers.
- Retention after subscription cancellation.

Do not commit licensed raw data to a public repository or include it in shareable test fixtures. Provider attribution, non-display fees, exchange agreements, and redistribution limits are reviewed before unattended operation and after a source or use change.

## Personal Use Boundary

The approved scope is software for the owner's own account and research. The project must stop for legal review before:

- Accepting, controlling, pooling, or trading another person's money.
- Selling signals, recommendations, copy trading, account access, or managed service.
- Giving personalized investment advice.
- Advertising returns or soliciting investment.
- Sharing licensed data outside permitted terms.
- Operating through a company or partnership without tax and regulatory review.
- Connecting multiple beneficial owners or accounts.

Repository documentation and educational discussion do not authorize any of these activities.

## Retention Access and Export

- Set retention periods by record class after professional and provider review; no implementation default may delete tax or broker evidence prematurely.
- Use encrypted storage and backup for account, fill, statement, and tax records.
- Limit access to the owner and explicitly authorized professional advisers.
- Log exports by record set, period, purpose, recipient class, hash, and time without logging confidential contents.
- Create adviser exports from a copy with only necessary fields; remove API and operational secrets.
- Preserve source statement files and hashes alongside normalized exports.
- Test restoration and tax-year replay before relying on automated retention.
- Destruction after expiry must be deliberate, logged, and include backup copies where required.

Expected exports include complete trade ledger, open holdings and acquisition pool, realized disposal candidates, dividends and withholding, fees, FX evidence, capital flows, unresolved exceptions, and period reconciliation sign-off.

## Periodic Review

| Frequency or trigger | Review |
|---|---|
| Each session | Order, fill, position, cash, fee, and daily report completeness |
| Monthly | Broker statement reconciliation and exception review |
| Tax-year preparation | Full record export, pool roll-forward, professional tax review |
| Before Stage 5 | Broker, product, data-license, tax, protection, retention, and emergency review |
| At least annually after that gate | Refresh all external assumptions and approvals |
| Broker or provider notice | Assess terms, pricing, API, symbol, or permission impact before next eligible session |
| Residence instrument wrapper or ownership change | Stop and obtain fresh applicability advice |
| Incident or missing evidence | Preserve, reconcile, correct, and add a prevention control |

## Preactivation Checklist

- [ ] Owner identity, residence assumptions, account, and broker entity are confirmed.
- [ ] Exact instruments and account wrapper receive current tax review.
- [ ] Capital Gains Tax, income, FX, matching, and retention rules are documented by tax year.
- [ ] Broker API and automated-trading terms are accepted and archived by reference.
- [ ] Market-data storage and use rights are documented.
- [ ] Order, fill, fee, FX, dividend, action, and capital-flow schemas are complete.
- [ ] Paper records generate an accountant-reviewable export with explicit exceptions.
- [ ] Monthly paper statement reconciliation has been rehearsed.
- [ ] Sensitive records and backups are encrypted and access-restricted.
- [ ] Personal-use boundary remains true.
- [ ] All professional confirmations are current and linked to the Stage 5 evidence bundle.

No incomplete checklist row can be waived by strategy performance.

## Open Decisions

| Decision | Needed by | Blocking effect |
|---|---|---|
| Approve base reporting currency | Ledger implementation | Blocks canonical conversion reporting |
| Select authoritative internal FX source and timing rule | Accounting implementation | Blocks GBP-equivalent records |
| Confirm account and ETF tax treatment with UK professional | Stage 5 review | Keeps Stage 5 denied |
| Define record retention by class | Persistent paper operation | Blocks automated deletion |
| Select encrypted statement and tax archive | Paper statement rehearsal | Blocks secure evidence storage |
| Confirm broker statement and activity export coverage | Adapter acceptance | Blocks period reconciliation design |
