# Pilot unit-economics model — input template

**Status:** calculation framework only. No provider, hosting region, contractual price, token distribution, storage footprint or paid-pilot usage data has been verified here. All numeric inputs must be populated from invoices, provider price sheets and measured pilot usage before pricing decisions are made. Do not treat blanks as zero.

## 1. Required source facts

| Input | Required evidence | Owner |
|---|---|---|
| Hosting provider, region and instance/service SKU | Production deployment manifest and current provider invoice | Deployment owner |
| Database and compute utilization | At least one representative billing period plus CPU/RAM/IO metrics | Operations |
| Object storage class, region, request pricing and egress | Bucket configuration, storage inventory and provider price sheet | Storage owner |
| Backup storage, retention and restore copies | Backup manifests, actual encrypted bundle sizes and retention policy | Operations |
| Email, monitoring, logging, CDN and secrets costs | Provider invoices and usage reports | Operations |
| AI provider, endpoint, model/version and region | Exact production configuration and signed commercial terms | AI integration owner |
| Input/output token pricing, cached input, batch and retry rules | Provider price sheet effective for the billing period | AI integration owner |
| OCR, embeddings, reranking and other auxiliary charges | Exact enabled services and price sheets | AI integration owner |
| Payment processing, tax, support and customer-success overhead | Contracts, finance records and time tracking | Commercial owner |
| Firm seats, matters, documents, AI requests and peak concurrency | Firm-scoped product metrics over representative pilot weeks | Product owner |

## 2. Monthly hosting and storage cost per firm

Use actual monthly costs and document the allocation rule for shared infrastructure.

`Monthly hosting per firm = (shared fixed infrastructure cost / active paying firms) + firm-attributable compute + firm-attributable database + firm-attributable network + firm-attributable operations`

`Monthly storage per firm = stored original bytes × storage price/GB-month + derived bytes × storage price/GB-month + backup bytes × backup price/GB-month + request/egress charges`

Count all retained copies: original documents, extracted text, previews, version history, exports awaiting expiry, backups and recovery copies. Avoid double-counting replicated storage when the provider invoice already includes it.

| Monthly input | Firm A | Firm B | Firm C | Source / period |
|---|---:|---:|---:|---|
| Allocated compute and database | — | — | — | |
| Allocated network/egress | — | — | — | |
| Original file storage (GB-month) | — | — | — | |
| Derived/preview storage (GB-month) | — | — | — | |
| Backup/recovery storage (GB-month) | — | — | — | |
| Email, monitoring and shared services | — | — | — | |
| Support/customer-success hours × loaded hourly cost | — | — | — | |
| **Total monthly cost per firm** | **—** | **—** | **—** | |

Allocation methods must be stated (measured tenant usage, metered requests, storage share, or equal allocation). Equal allocation is a temporary estimate only and should be replaced when usage evidence is available.

## 3. AI cost per request

Calculate a request as the sum of every provider call and auxiliary service used to produce the result, including retries that incurred cost.

For each model call:

`Call cost = input tokens × input price + cached input tokens × cached-input price + output tokens × output price`

Then:

`AI request cost = sum(model call costs) + OCR page charges + embedding charges + reranking charges + other provider charges`

Track at minimum:
- firm pseudonymous ID and request ID;
- provider, endpoint, model/version, region and price-sheet effective date;
- input, cached-input and output token counts for each call;
- OCR pages, embedding tokens, reranker calls and any other billable units;
- retry count, failed-call charges and final request status;
- currency, exchange-rate source/date and tax treatment.

Do not store prompts, answers, matter titles or client names in the commercial cost ledger. Keep request IDs and aggregate costs separate from legal content. AI-1 owns provider-call and token-usage instrumentation in its tools; AI-2 consumes approved aggregate cost records for product economics.

| Request class | Calls/request | Mean input tokens | Mean output tokens | Auxiliary units | Mean cost/request | P95 cost/request |
|---|---:|---:|---:|---:|---:|---:|
| Research answer | — | — | — | — | — | — |
| Follow-up answer | — | — | — | — | — | — |
| Document OCR/extraction | — | — | — | — | — | — |
| Draft generation | — | — | — | — | — | — |
| Other enabled workflow | — | — | — | — | — | — |

Populate from measured request samples by model/version and firm-approved processing path. Do not mix sandbox pricing with production prices.

## 4. Sustainable subscription price

First calculate monthly fully loaded cost per firm:

`Fully loaded cost = hosting + storage + AI usage + payment fees + support + customer-success + allocated operations`

Then calculate a price floor for a target gross margin:

`Price floor before tax = fully loaded cost / (1 - target gross margin)`

Add taxes, payment fees and any contractual pass-through costs according to finance and counsel advice. Model at least:
- low, median and high usage firms;
- one, three and five-seat configurations;
- average and P95 AI request volume;
- storage growth and retention/backup overhead;
- failed requests and retries;
- support-heavy onboarding and renewal periods.

Do not choose plan limits solely from average usage. Use measured P95 demand plus an explicit safety buffer, then validate concurrency and abuse controls at those limits.

| Plan | Seats | Matters | Original storage | AI requests/month | Support scope | Proposed price | Cost at P50 | Cost at P95 |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| Pilot | — | — | — | — | — | — | — | — |
| Standard | — | — | — | — | — | — | — | — |
| Advanced | — | — | — | — | — | — | — | — |

## 5. First-three-firm evidence

Use one row per firm and a fixed measurement window. A sign-in event is not a unique active user. When the WAU dashboard metric is deployed, use its published qualifying-workflow definition and keep sign-ins separate; until then mark WAU **not measured**.

| Evidence | Firm A | Firm B | Firm C |
|---|---:|---:|---:|
| Active seats / contracted seats | — | — | — |
| Weekly active users | — | — | — |
| Successful sign-in events | — | — | — |
| AI requests by class | — | — | — |
| Storage growth (GB/week) | — | — | — |
| Support hours | — | — | — |
| Fully loaded monthly cost | — | — | — |
| Owner-confirmed workflow value | — | — | — |
| Written price response | — | — | — |
| Paid invoice / cleared prepayment | — | — | — |

A blank means not measured. Do not substitute demo activity, invitations, sign-ins, verbal interest or forecasts for actual paying-firm usage.

## 6. Decision gates

- [ ] Production provider, region, SKUs and current price sheets verified.
- [ ] AI token and auxiliary-service costs measured for representative requests.
- [ ] Storage inventory reconciled with original files, derived files, exports and backups.
- [ ] Three firms have at least four complete weeks of measured usage, or the sample limitation is explicitly recorded.
- [ ] Plan limits tested against actual seat, matter, storage, AI and concurrency usage.
- [ ] Support and customer-success cost included.
- [ ] Finance owner approves tax, currency, payment-fee and gross-margin assumptions.
- [ ] Willingness-to-pay evidence includes an actual written offer and decision-maker response.
- [ ] Prepayment target counted only from cleared payments or binding purchase commitments.

Until these gates are met, pricing is provisional and per-firm cost/AI cost figures must be reported as **not yet measured**, not estimated customer facts.
