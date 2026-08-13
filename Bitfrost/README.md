# Bifrost AI Gateway — Practical Lab

![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white)
![Bifrost](https://img.shields.io/badge/Bifrost-AI%20Gateway-111827?logo=lightning&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Integrations-1C3C3C?logo=langchain&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-D02B2B?logo=qdrant&logoColor=white)
![Jina AI](https://img.shields.io/badge/Jina%20AI-Embeddings-5B4BDB)
![Groq](https://img.shields.io/badge/Groq-Provider-F55036)
![Mistral AI](https://img.shields.io/badge/Mistral%20AI-Provider-000000)

> Hands-on examples for building resilient, observable, and retrieval-aware LLM applications with Bifrost AI Gateway.

## Overview

This repository is a practical notebook-based lab for exploring Bifrost AI Gateway with Groq and Mistral AI. It demonstrates how a single OpenAI-compatible gateway can centralize provider routing, automatic failover, load balancing, streaming, virtual-key governance, MCP tools, and a Qdrant + Jina AI RAG pipeline.

The main walkthrough lives in [`bif.ipynb`](./bif.ipynb), with Rich-formatted output and small, focused experiments that make each gateway capability easy to observe.

## Architecture

```text
                         ┌──────────────────────────────┐
                         │        bif.ipynb              │
                         │  Python / HTTPX / LangChain   │
                         └──────────────┬───────────────┘
                                        │ OpenAI-compatible API
                                        ▼
                         ┌──────────────────────────────┐
                         │      Bifrost AI Gateway       │
                         │ routing · fallback · SSE     │
                         │ virtual keys · MCP           │
                         └───────┬──────────────┬───────┘
                                 │              │
                         ┌───────▼──────┐  ┌────▼─────────┐
                         │ Groq /       │  │ Qdrant Cloud │
                         │ Mistral AI   │  │ + Jina AI    │
                         └──────────────┘  └──────────────┘
```

## Key Concepts Covered

- **Direct provider calls:** Compare Groq and Mistral responses, latency, and token usage.
- **Manual fallback:** Catch a provider failure in application code and retry with a second provider.
- **Automatic provider fallback:** Pass a fallback model through Bifrost using the `x-bifrost-fallback-models` header.
- **Load balancing and routing:** Observe which configured provider key handled each request through Bifrost routing metadata.
- **SSE / real-time streaming:** Stream tokens directly from a provider and through Bifrost using the OpenAI-compatible `stream=True` interface.
- **Virtual Keys:** Route requests through gateway-issued keys and demonstrate access and budget enforcement.
- **MCP tools:** Discover registered MCP clients and invoke optional DeepWiki and Tavily servers through a chat completion request.
- **Embeddings:** Implement a small LangChain-compatible `JinaEmbeddings` adapter using Jina AI's embeddings API.
- **Qdrant knowledge base:** Create a collection, configure cosine similarity, and index a small document set in Qdrant Cloud.
- **RAG pipeline:** Retrieve the top matching documents, inject them into a grounded prompt, and generate the answer through Bifrost.

## Tech Stack

| Category | Technologies |
| --- | --- |
| Runtime | Python 3.13+, Jupyter / IPython kernel |
| Gateway | [Bifrost AI Gateway](https://github.com/maximhq/bifrost), OpenAI-compatible Chat Completions API |
| LLM providers | [Groq](https://groq.com/), [Mistral AI](https://mistral.ai/) |
| LLM framework | [LangChain Core](https://python.langchain.com/), LangChain Community, LangChain Groq, LangChain Mistral, LangChain OpenAI |
| Retrieval | [Qdrant](https://qdrant.tech/), `qdrant-client`, LangChain Qdrant integration |
| Embeddings | [Jina AI Embeddings](https://jina.ai/embeddings/), `jina-embeddings-v4` |
| HTTP and utilities | HTTPX, Requests, `python-dotenv`, Rich |

## Prerequisites & Setup

You will need:

- Python **3.13 or newer**
- Docker, for running a local Bifrost gateway
- A Groq API key and a Mistral API key
- A Qdrant Cloud cluster and API key
- A Jina AI API key
- Optional: configured DeepWiki and Tavily MCP servers in Bifrost

### 1. Clone the repository and create an environment

```bash
git clone <your-fork-url>
cd Bifrost

python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1
```

### 2. Install dependencies

The project dependencies are declared in `pyproject.toml`. Install the repository in editable mode:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

For a standalone notebook environment, the equivalent dependency install is:

```bash
python -m pip install \
  httpx ipykernel langchain-community langchain-core \
  langchain-groq langchain-mistralai langchain-openai \
  langchain-qdrant mistralai python-dotenv qdrant-client \
  requests rich groq openai
```

### 3. Configure environment variables

Create a `.env` file in the repository root. Never commit real credentials or virtual keys.

```dotenv
# Model providers
GROQ_API_KEY=gsk_...
MISTRAL_API_KEY=...

# Local Bifrost gateway
BIFROST_BASE_URL=http://localhost:8080

# Optional Bifrost Virtual Keys created in the gateway UI
BIFROST_GROQ_VKEY=
BIFROST_MISTRAL_VKEY=

# Qdrant Cloud
QDRANT_CLUSTER=https://<cluster-id>.<region>.cloud.qdrant.io
QDRANT_API_KEY=...

# Jina AI
JINA_API_KEY=jina_...
```

The notebook reads these variables with `python-dotenv`. `BIFROST_BASE_URL` defaults to `http://localhost:8080` when it is not set.

### 4. Start Bifrost locally

Start a new gateway instance with Docker:

```bash
docker run -d --name bifrost -p 8080:8080 maximhq/bifrost
```

Open [http://localhost:8080](http://localhost:8080), configure the Groq and Mistral providers, and create any Virtual Keys needed by the notebook. If a container named `bifrost` already exists, start it with:

```bash
docker start bifrost
```

Verify that the gateway is reachable:

```bash
curl http://localhost:8080/health
```

The notebook also performs this health check in its first cells. For the gateway's current setup options, see the [official Bifrost gateway setup guide](https://docs.getbifrost.ai/quickstart/gateway/setting-up).

### 5. Run the notebook

Open [`bif.ipynb`](./bif.ipynb) in VS Code or Jupyter and run the cells from top to bottom. To launch Jupyter locally:

```bash
python -m pip install jupyter
jupyter notebook bif.ipynb
```

The MCP and RAG sections require their corresponding external services. The earlier provider, routing, streaming, fallback, and Virtual Key examples can be explored independently.

## Notebook Walkthrough

| Cells | Section | What happens |
| --- | --- | --- |
| 0–4 | Initialization and model configuration | Load `.env`, read provider/gateway credentials, check `/health`, define test prompts, and display the primary/fallback model matrix. |
| 5–8 | Groq and Mistral | Call both providers directly and print the response, latency, and token usage with Rich. |
| 9–10 | Streaming | Stream Groq response chunks to the terminal as they arrive. |
| 11–13 | Manual fallback | Try Groq first, catch an exception, and retry with Mistral; a deliberately invalid model demonstrates the fallback path. |
| 14–17 | Bifrost client and routing | Create an OpenAI-compatible client pointed at `/v1`, route requests with `provider/model` names, and read the selected provider from response metadata. |
| 18–20 | Automatic provider fallback | Configure a Mistral fallback using `x-bifrost-fallback-models` and show that a bad model name (404) does not trigger the fallback by design. |
| 21–25 | Load balancing and observability | Inspect routing-key metadata, stream through Bifrost, and query the latest gateway logs from `/api/logs`. |
| 26–29 | Virtual Keys | Call Bifrost with a gateway-issued key and surface invalid, missing, or over-budget key errors. |
| 30–36 | MCP with tools | List registered MCP clients from `/api/mcp/clients` and conditionally call the DeepWiki and Tavily servers when configured. |
| 37–43 | Qdrant and Jina setup | Connect to Qdrant Cloud, define the Jina AI embeddings adapter, and verify the embedding dimensionality. |
| 44–47 | Knowledge base | Recreate the `bifrost_rag_demo` collection with cosine distance and index the example documents. |
| 48–52 | RAG pipeline | Retrieve the top-k documents, build a context-grounded prompt, query the selected model through Bifrost, and inspect the retrieved context. |

## Useful Gateway Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Check whether the local gateway is online. |
| `POST /v1/chat/completions` | Send OpenAI-compatible chat completion requests. |
| `GET /api/logs?limit=5` | Inspect recent gateway request logs. |
| `GET /api/mcp/clients` | List MCP clients registered in Bifrost. |

## Notes

- Model identifiers in the notebook use Bifrost's provider-qualified format, such as `groq/openai/gpt-oss-120b` and `mistral/mistral-large-latest`.
- The RAG example deletes and recreates the `bifrost_rag_demo` collection before indexing documents. Use a dedicated Qdrant collection or cluster when experimenting.
- MCP examples are optional and depend on the relevant MCP servers being registered and available in the local Bifrost instance.
- This repository is an educational lab and a starting point for experimentation, not a production-ready gateway configuration.

## License & Acknowledgments

This project is licensed under the **MIT License**. See [`LICENSE`](./LICENSE) for the full text.

Thanks to the teams and open-source communities behind:

- [Bifrost AI Gateway](https://github.com/maximhq/bifrost) for the unified gateway, routing, fallback, streaming, and governance concepts.
- [LangChain](https://www.langchain.com/) for the model and vector-store abstractions.
- [Qdrant](https://qdrant.tech/) for vector storage and similarity search.
- [Jina AI](https://jina.ai/) for the embedding API.
- [Groq](https://groq.com/) and [Mistral AI](https://mistral.ai/) for the model providers used in the examples.
