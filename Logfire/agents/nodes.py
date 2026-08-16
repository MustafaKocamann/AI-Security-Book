import os
import time
import logfire
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage

from .state import AgentState
from .llm import groq_llm

load_dotenv()

# Lazy getters for singletons
_groq_instance = None
def get_groq():
    global _groq_instance
    if _groq_instance is None:
        _groq_instance = groq_llm()
    return _groq_instance

_tavily_instance = None
def get_tavily():
    global _tavily_instance
    if _tavily_instance is None:
        try:
            from langchain_tavily import TavilySearch
            _tavily_instance = TavilySearch(max_results=4)
        except Exception:
            try:
                from langchain_community.tools.tavily_search import TavilySearchResults
                _tavily_instance = TavilySearchResults(max_results=4)
            except Exception:
                _tavily_instance = None
    return _tavily_instance

# ── Specialized System Prompts ─────────────────────────────────────────────

_PLANNER_PROMPT = """You are an intent classification engine for a multi-agent system.
Classify the user's query into EXACTLY one of these categories:
- explain  → "what is", "how does", "why", "tell me about", "describe", conceptual learning
- analyze  → "compare", "pros and cons", "evaluate", "difference", "vs", "tradeoffs", benchmarks
- create   → "write", "generate", "brainstorm", "create", "ideas for", "draft", architecture design
- search   → "latest", "current", "news", "today", "recent", "2024", "2025", "search for", real-time info

Reply with ONLY ONE WORD (lowercase): explain, analyze, create, or search.
Do NOT add any punctuation, markdown, or explanation."""

_EXPLAINER_PROMPT = """You are an expert technical educator and senior mentor.
Explain the topic clearly using simple language, real-world analogies, and structured bullet points.
Break down complex technical concepts into digestible insights.
Be comprehensive yet concise — aim for 150-250 words."""

_ANALYST_PROMPT = """You are a senior systems architect and technical analyst.
Provide a sharp, structured analysis:
1. Executive Summary & Core Comparison
2. Key Architectural Differences / Pros & Cons
3. Trade-offs & Production Considerations
4. Actionable Recommendation / Decision Matrix
Use clear markdown headers, bold keywords, and bullet points. Aim for 200-300 words."""

_CREATOR_PROMPT = """You are an elite creative AI solutions architect and prompt strategist.
Generate fresh, highly specific, actionable, and innovative ideas, architectures, or content.
Format as a numbered breakdown with brief rationale and implementation pointers. Aim for 150-250 words."""

_FORMATTER_PROMPT = """You are a senior technical editor and presentation formatter.
Polish and structure the given draft response for maximum readability:
- Use clean Markdown hierarchy (#, ##, ###, bullet points, bold key terms, code blocks if needed).
- Add relevant emoji callout highlights for key takeaways.
- Do NOT alter core factual content, but enhance aesthetic presentation, clarity, and tone.
- Keep the response direct and elegant."""


# ── Node Implementations ───────────────────────────────────────────────────

def planner(state: AgentState) -> dict:
    llm = get_groq()
    question = state["question"]
    session_id = state.get("session_id", "")
    
    with logfire.span("planner_node", question=question, session_id=session_id):
        response = llm.invoke([
            SystemMessage(content=_PLANNER_PROMPT),
            HumanMessage(content=question),
        ])
        raw_intent = response.content.strip().lower().split()[0].replace(".", "").replace(",", "")
        
        valid_intents = ("explain", "analyze", "create", "search")
        intent = raw_intent if raw_intent in valid_intents else "explain"

        logfire.info("intent_classified",
                     classified_intent=intent,
                     raw_output=response.content,
                     question=question)

        return {
            "intent": intent,
            "node_path": state.get("node_path", []) + ["planner"],
        }


def explainer(state: AgentState) -> dict:
    llm = get_groq()
    question = state["question"]
    with logfire.span("explainer_specialist",
                      question=question,
                      specialist="Explainer",
                      model="llama-3.3-70b-versatile"):
        response = llm.invoke([
            SystemMessage(content=_EXPLAINER_PROMPT),
            HumanMessage(content=question),
        ])
        logfire.info("explainer_completed",
                     output_char_count=len(response.content))
        return {
            "specialist_output": response.content,
            "model_used": "Groq LLaMA 3.3 70B (Explainer)",
            "node_path": state.get("node_path", []) + ["explainer"],
        }


def analyst(state: AgentState) -> dict:
    llm = get_groq()
    question = state["question"]
    with logfire.span("analyst_specialist",
                      question=question,
                      specialist="Analyst",
                      model="llama-3.3-70b-versatile"):
        response = llm.invoke([
            SystemMessage(content=_ANALYST_PROMPT),
            HumanMessage(content=question),
        ])
        logfire.info("analyst_completed",
                     output_char_count=len(response.content))
        return {
            "specialist_output": response.content,
            "model_used": "Groq LLaMA 3.3 70B (Analyst)",
            "node_path": state.get("node_path", []) + ["analyst"],
        }


def creator(state: AgentState) -> dict:
    llm = get_groq()
    question = state["question"]
    with logfire.span("creator_specialist",
                      question=question,
                      specialist="Creator",
                      model="llama-3.3-70b-versatile"):
        response = llm.invoke([
            SystemMessage(content=_CREATOR_PROMPT),
            HumanMessage(content=question),
        ])
        logfire.info("creator_completed",
                     output_char_count=len(response.content))
        return {
            "specialist_output": response.content,
            "model_used": "Groq LLaMA 3.3 70B (Creator)",
            "node_path": state.get("node_path", []) + ["creator"],
        }


def web_searcher(state: AgentState) -> dict:
    llm = get_groq()
    tavily_tool = get_tavily()
    question = state["question"]
    with logfire.span("web_searcher_specialist",
                      query=question,
                      specialist="WebSearcher"):

        sources = []
        raw_results_str = ""

        # Step 1: Tavily Live Search
        with logfire.span("tavily_live_search", query=question):
            try:
                if tavily_tool is not None and os.getenv("TAVILY_API_KEY"):
                    tav_res = tavily_tool.invoke(question)
                    if isinstance(tav_res, list):
                        formatted_items = []
                        for i, r in enumerate(tav_res):
                            if isinstance(r, dict):
                                url = r.get("url", "")
                                content = r.get("content", "")
                                if url:
                                    sources.append(url)
                                formatted_items.append(f"[{i+1}] {url}\n{content}")
                            else:
                                formatted_items.append(str(r))
                        raw_results_str = "\n\n".join(formatted_items)
                    elif isinstance(tav_res, dict) and "results" in tav_res:
                        for item in tav_res["results"]:
                            url = item.get("url", "")
                            if url:
                                sources.append(url)
                        raw_results_str = str(tav_res)
                    else:
                        raw_results_str = str(tav_res)
                else:
                    raw_results_str = "Tavily Search API not configured. Falling back to internal knowledge synthesis."
            except Exception as e:
                logfire.warning("tavily_search_failed", error=str(e))
                raw_results_str = f"Live search encountered an exception: {e}. Answering based on LLM knowledge."

            logfire.info("web_search_finished",
                         num_sources=len(sources),
                         sources=sources)

        # Step 2: Synthesis by Groq LLM
        with logfire.span("synthesize_search_results",
                          model="llama-3.3-70b-versatile"):
            synthesis_prompt = (
                "You are an expert research analyst. Synthesize the web search findings below into a clear, "
                "accurate, and timely response. Highlight key facts, recent developments, and cite the source URLs.\n\n"
                f"Question: {question}\n\n"
                f"Search Findings:\n{raw_results_str}"
            )
            summary_response = llm.invoke([
                SystemMessage(content="Synthesize search results accurately with citations."),
                HumanMessage(content=synthesis_prompt),
            ])
            logfire.info("synthesis_completed",
                         synthesis_char_count=len(summary_response.content))

        return {
            "specialist_output": summary_response.content,
            "search_results": raw_results_str,
            "sources": sources,
            "model_used": "Tavily Search 🌐 + Groq LLaMA 3.3 70B",
            "node_path": state.get("node_path", []) + ["web_searcher"],
        }


def formatter(state: AgentState) -> dict:
    llm = get_groq()
    intent = state.get("intent", "general")
    specialist_out = state.get("specialist_output", "")
    
    with logfire.span("formatter_node",
                      intent=intent,
                      model="llama-3.3-70b-versatile"):
        response = llm.invoke([
            SystemMessage(content=_FORMATTER_PROMPT),
            HumanMessage(content=f"Original Draft ({intent} specialist):\n\n{specialist_out}"),
        ])
        final_answer = response.content
        model_chain = state.get("model_used", "Groq") + " -> Formatter (Groq LLaMA 3.3)"

        logfire.info("formatter_completed",
                     input_len=len(specialist_out),
                     output_len=len(final_answer))

        return {
            "final_answer": final_answer,
            "model_used": model_chain,
            "node_path": state.get("node_path", []) + ["formatter"],
        }
