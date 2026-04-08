---
name: DDD Writing Rules
description: Shared DDD vocabulary and anti-pattern rules for writing Epics, Features, and Tasks in Ubiquitous Language. Referenced by write-epic, write-feature, and write-task.
---

# DDD Writing Rules

Apply these rules whenever writing or reviewing Epic, Feature, or Task content.

## Domain Actor Naming

Use named domain roles — never generic terms:

- ✅ "Fulfilment Manager", "Payment Auditor", "Merchant"
- ❌ "user", "admin", "the system"

## Domain Verb vs CRUD

Use business actions — not generic CRUD verbs:

- ✅ allocate, settle, reconcile, dispute, approve, fulfil, cancel
- ❌ create, update, delete, store, query, render, process

## Domain Event Naming

Events must use **past-tense domain names** from the **domain's perspective**:

- ✅ `OrderPlaced`, `PaymentSettled`, `ShipmentDispatched`
- ❌ `order_status_updated`, `payment_processed_successfully`, `ShipmentServiceUpdatedStatus`

## Business Outcomes, Not System States

Describe observable business results — not technical system state:

- ✅ "The Merchant receives a settlement notification within 2 minutes"
- ❌ "The `orders` table has `status = 'settled'`", "HTTP 200 returned"

## Tech Jargon Anti-Patterns

Remove these from any domain-facing content (Epic goals, Feature ACs, Gherkin scenarios, user stories):

- REST API, HTTP, JSON payload, SQL query, database record/row/table
- Mock, stub, endpoint, microservice, lambda
- Any implementation framework name in a business description

Reframe in business terms before writing.

## Bounded Context Seams

Name every bounded context explicitly. When a Feature or Task crosses a seam:

- Identify which context **emits** and which **consumes**
- Use each context's own vocabulary on its side of the seam
- Example: "Sales Context emits `OrderPlaced`; Warehouse Context consumes it"
