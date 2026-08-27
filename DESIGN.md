# Design Note — Support AI

## 1. Failure Modes

### 1.1 Incorrect LLM classification or hallucination

The LLM may incorrectly classify a ticket, assign the wrong urgency, or generate unsupported troubleshooting information. This is particularly risky for P1 incidents because an incorrect classification can route the ticket to the wrong team.

The system mitigates this by combining LLM reasoning with deterministic Python rules for high-confidence cases such as billing, obvious production outages, and explicit How-To requests. Structured Pydantic validation is also used to ensure that the model returns the expected schema. Knowledge-base retrieval provides grounding for known issues and troubleshooting responses.

The evaluation harness provides regression testing for classification accuracy and evidence-grounding behavior.

### 1.2 Knowledge-base retrieval failure

The retrieval layer may return irrelevant or incomplete documents. A poor retrieval result could cause the system to incorrectly mark a ticket as a known issue or provide inappropriate troubleshooting instructions.

The system therefore separates retrieval from the final classification and records the retrieved document and relevance information in the response. If no sufficiently relevant document is found, the system should avoid claiming that the issue is a known issue.

In production, retrieval quality would be monitored using relevance metrics and manually reviewed failure samples.

### 1.3 External AI service failure

The Gemini API can experience rate limits, quota exhaustion, latency, or temporary unavailability. This was observed during development when the free-tier request quota was exceeded.

The application handles AI-service failures separately from normal application errors and returns an appropriate service-unavailable response. Response caching is also used during development to avoid repeatedly sending identical requests. In production, I would additionally use bounded retries with exponential backoff, request timeouts, rate limiting, and an optional fallback model or deterministic response path.

---

## 2. Latency vs Quality

A deliberate trade-off in this solution is the use of Gemini Flash together with lightweight local retrieval and deterministic Python rules.

Using a larger model or multiple LLM calls could potentially improve reasoning quality, but it would increase latency, cost, and rate-limit pressure. Instead, the system performs deterministic processing locally and uses the LLM primarily for tasks requiring natural-language reasoning and synthesis.

For example, account metrics such as the 90-day ticket window, ticket counts, renewal timing, and data-quality checks are calculated in Python rather than asking the LLM to calculate them. Gemini then receives the structured snapshot and produces the executive summary, risks, and TAM talking points.

If latency became the hard constraint, I would route high-confidence tickets entirely through deterministic rules and use the LLM only for ambiguous cases. I would also cache repeated requests and use asynchronous API processing for longer-running account summaries.

---

## 3. Data Sensitivity

The provided dataset is synthetic, and the solution uses only the mock accounts, tickets, and knowledge-base documents supplied with the task.

API credentials are stored in environment variables rather than source code. The real `.env` file is excluded from version control, while `.env.example` contains only the required variable names.

In a production deployment, ticket and account information could contain PII or confidential customer information. Before sending data to an external LLM provider, I would minimize the payload to only the information required for the task and introduce a PII-redaction layer where appropriate. Sensitive fields that are not required for classification or summarization should not be sent to the model.

Access to the resulting API would also be protected using authentication, authorization, audit logging, and encrypted transport.

---

## 4. Scaling

The current implementation is designed for the provided dataset of 500 tickets and 50 accounts. With 10× the volume, the first bottlenecks would likely be LLM API requests, rate limits, retrieval/indexing cost, and application latency.

The current local retrieval approach is sufficient for the mock dataset, but at larger volumes I would build a persistent retrieval index rather than repeatedly processing the knowledge base. Frequently requested account summaries and repeated ticket classifications could be cached.

For higher throughput, the API layer could use asynchronous request handling and a background queue for expensive account-summary operations. Rate limiting would prevent bursts from overwhelming the external LLM service.

At significantly larger scale, I would separate ingestion, retrieval, LLM inference, and API serving into independent services. Monitoring would track request latency, error rates, token usage, retrieval quality, LLM failures, and evaluation scores so that regressions can be detected before they affect internal users.