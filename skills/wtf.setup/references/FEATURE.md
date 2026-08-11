---
name: Feature
about: A user-facing capability within an Epic
title: "🚀 Feature: "
labels: feature
assignees: ""
---

# 🚀 Feature: {{title}}

## Bounded Context

---

## User Stories

<!-- 👤 PO — 1..n co-related stories that share one Spine. This body is canonical for all scenarios: PMs and designers edit them here, not in Trace issues. Repeat the story block for each story. -->

### Story 1: [name]

- As a **_, I want _** so that \_\_\_

#### Acceptance Criteria

<!-- Each AC maps to one or more scenarios below. -->

- [ ]

#### Scenarios

<!-- Canonical Gherkin for this story. Traces claim subsets of these by name. -->

```gherkin
Scenario: Happy path
  Given
  When
  Then

Scenario: Edge case
  Given
  When
  Then
```

## Design Handoff

<!-- Link Figma frames, component specs, or annotated mockups -->

- Figma:
- States covered: (default / loading / error / empty)
- Accessibility notes:

---

## Edge Cases

## <!-- Explicitly name them here so Deepening Traces can claim scenarios that cover them. Use domain language. -->

## Domain Events

<!-- Events this feature emits or consumes. Use past-tense domain names (e.g. OrderPlaced, PaymentSettled). -->

- Emits:
- Consumes:

---

## Definition of Ready

<!-- This feature is ready for a Trace Plan when: -->

- [ ] User stories agreed by PO
- [ ] Design handoff complete
- [ ] Acceptance criteria written and reviewed
- [ ] Edge cases identified

---

## Trace Plan

<!-- Ordered checklist — the current aim, not a contract. Item 1 is the Skeleton. Each item names its story, its Scenario Claim, and what it adds to the Spine. Link Trace issues as they are created. -->

1. [ ] ☄️ Skeleton — [story]: [what it proves of the Spine] (claims: "[scenario name]")
2. [ ] ☄️ [story]: [what it adds to the Spine] (claims: "[scenario names]")

---

## Delivery Override

<!-- Optional. Set only when this Feature must not use the `delivery` mode in `.wtf/config.json`. State the reason. Leave blank to use the config. -->

- Mode: <!-- staged | trunk -->
- Reason:
