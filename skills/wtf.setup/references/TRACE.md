---
name: Trace
about: One pass over the Feature's Spine — implements one story's Scenario Claim end-to-end
title: "☄️ Trace: "
labels: trace
assignees: ""
---

# ☄️ Trace: {{title}}

---

## Story

<!-- 👤 Copied verbatim from the parent Feature. Do not re-derive it. Do not reword it. -->

- As a **_, I want _** so that \_\_\_

---

## Scenario Claim

<!-- The names of the scenarios this Trace implements. The claims of one story's Traces cover all its scenarios, with no overlap. The Feature body is canonical — edit scenarios there. -->

- Scenario:

<details>
<summary>Claimed scenarios — synced from Feature #N — edit there, not here</summary>

```gherkin
Scenario:
  Given
  When
  Then
```

</details>

---

## Spine Position

<!-- Skeleton | Extension | Deepening. The Skeleton is Trace 1 and proves the Spine. An Extension adds a further story to the Spine. A Deepening claims further scenarios of a story already started. Name the Traces this one builds on. -->

- Position:
- Builds on: Trace #

---

## Contracts & Interfaces

<!-- 👤 Tech Lead — These are the spec. Implementation must match these exactly. -->

### Request

```json
{}
```

### Response

```json
{}
```

### Events / Side Effects

<!-- Describe any events emitted, webhooks triggered, or state changes. Write "None" when the Trace emits nothing. -->

- None

---

## Technical Approach

<!-- 👤 Developer — Filled by implement-trace at implementation time -->

- Architecture decisions:
- Data flow:
- Trade-offs:

### Aggregates & Invariants

<!-- Which Aggregates does this Trace modify? What business rules must hold after the change? -->

- Aggregates:
- Invariants:

---

## Observability

<!-- How do we verify this works in production? -->

- Logs:
- Metrics:
- Alerts:

---

## Design Reference

<!-- Optional. Filled by design-trace: Figma frames / component specs for the claimed scenarios. -->

## Definition of Done

- [ ] All claimed scenarios covered by tests
- [ ] Contracts match implementation
- [ ] Observability in place
- [ ] System releasable after merge
- [ ] Code reviewed
- [ ] Design reviewed (if UI)
- [ ] Documentation updated

---

## Test Mapping

| Claimed scenario | Test file | Status |
| ---------------- | --------- | ------ |
|                  |           |        |
