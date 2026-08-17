# 🛡️ AI Security, Gateways & LLMOps Reference Architecture

A concise, production-oriented repository demonstrating security guardrails, resilient gateway patterns, multi-agent orchestration, and distributed observability for LLM applications.

---

### 🚀 Core Modules & Implementations

* **Guardrails AI (`guardrails_ai_book.ipynb`)**
  * **PII Redaction**: Pre-call masking of credit cards, emails, and personal identifiers[cite: 2].
  * **Policy Enforcement**: Keyword and semantic filters for competitors, toxic language, and out-of-domain topics[cite: 2].
  * **Deterministic Actions & Self-Healing**: Handled edge cases using `FIX`, `FILTER`, `REFRAIN`, `EXCEPTION`, and iterative `REASK` self-correction loops[cite: 2].
  * **Runtime Validation**: Live stream validation and native LangChain (LCEL) integration via `guard.to_runnable()`[cite: 2].

* **LiteLLM Gateway (`gateway.ipynb`)**
  * **Unified Interface**: Standardized proxy across 100+ model providers[cite: 3].
  * **Perimeter Defense**: Custom pre-call hooks (`input_callback`) to scrub PII (including Turkish TCKN and phone numbers) and block prompt injection/jailbreak patterns before reaching the LLM[cite: 3].
  * **Performance & Cost Optimization**: In-memory caching delivering ~370x speedups with zero token cost on duplicate queries[cite: 3].
  * **Task-Based Routing**: Intent classifier directing tasks (e.g., code vs. summary) to optimized model tiers with automatic fallbacks[cite: 3].

* **Portkey AI Gateway (`portkey-ai-book.ipynb`)**
  * **Key Management**: Virtual keys and slug abstractions (`@gkey/...`) isolating production credentials from code[cite: 4].
  * **Resilience Patterns**: Automated retries with exponential backoff on `429/5xx` status codes and hard request timeout enforcement[cite: 4].
  * **Traffic Orchestration**: Weighted load balancing (e.g., 70% Large / 30% Small models) and forced fallback routing under provider failure[cite: 4].
  * **Granular Audit Trails**: Request metadata tagging (`_user`, `session_id`, `feature`, `environment`) for tracing and cost attribution[cite: 4].

* **Bifrost Gateway & MCP Tools (`bif.ipynb`)**
  * **Failover & Load Balancing**: Gateway-level fallback routing and key load balancing[cite: 1].
  * **Model Context Protocol (MCP)**: Native tool execution integrating DeepWiki repo indexing and Tavily live web search[cite: 1].
  * **Enterprise RAG Pipeline**: Vector retrieval pipeline backed by Jina Embeddings v4 (2048-dim) and Qdrant Cloud[cite: 1].

* **Pydantic Logfire & OpenTelemetry (`pydantic_logfire.ipynb`, `trace.py`)**
  * **Distributed Tracing**: Hierarchical span tracking (`logfire.span`) capturing latency, token usage, and payload metadata across agent pipelines[cite: 5].
  * **Type-Safe Validation**: Pydantic schema validation for request and response envelopes (`LLMRequest`, `LLMResponse`)[cite: 5].
  * **Zero-Code Instrumentation**: Native OpenAI-compatible auto-instrumentation for Groq and Gemini models[cite: 5].

* **Multi-Agent Intent Router (`graph.py`, `nodes.py`, `llm.py`)**
  * **StateGraph Workflow**: LangGraph architecture routing queries from a `planner` node to dedicated specialists (`explainer`, `analyst`, `creator`, `web_searcher`) and converging into a unified `formatter` node.
  * **Graceful Degradation**: Fallback to internal knowledge synthesis if external search tools encounter errors or missing API configurations.

---

### 🏗️ High-Level Architecture

```mermaid
flowchart TD
    User([Client / User]) --> InputGuard[Pre-Call Security: LiteLLM & Guardrails AI\nPII Masking & Prompt Injection Defense]
    InputGuard --> Router[LangGraph Multi-Agent Router]
    
    subgraph Gateway [Gateway & Traffic Layer: Portkey / Bifrost]
        Router --> Cache{In-Memory / Semantic Cache?}
        Cache -- Hit (0ms / $0) --> Formatter
        Cache -- Miss --> LB[Load Balancer & Virtual Keys]
        LB --> Resilience[Retry & Timeout Policies]
    end
    
    subgraph Execution [Model Providers & External Tools]
        Resilience --> Primary[Primary LLM: Groq Llama 3.3 / Gemini 2.5]
        Primary -- 401 / 503 / Timeout --> Fallback[Fallback LLM: Llama 8B / Mistral]
        Resilience --> MCP[MCP Tools: Tavily / DeepWiki]
        Resilience --> VectorDB[(Qdrant / FAISS Vector Store)]
    end
    
    Primary --> Tracing[Pydantic Logfire / Distributed Tracing]
    Fallback --> Tracing
    
    Tracing --> OutputGuard[Output Sanitization & Self-Healing REASK]
    OutputGuard --> Formatter[LangGraph Formatter Node]
    Formatter --> Response([Validated Production Output])
