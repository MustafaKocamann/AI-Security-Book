import os
import time
import uuid
import json
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Nexus Multi-Agent AI Studio | Logfire Observability",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for High-End Master UI/UX Design ────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, .brand-title {
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.02em;
    }

    code, pre, .mono-font {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Gradient Brand Header */
    .brand-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .brand-title {
        background: linear-gradient(135deg, #60a5fa 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.2;
    }

    .brand-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 6px;
        font-weight: 400;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 18px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        font-family: 'Outfit', sans-serif;
    }

    /* Badge Pills */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-bottom: 8px;
    }
    .badge-explain {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-analyze {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-create {
        background: rgba(168, 85, 247, 0.15);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }
    .badge-search {
        background: rgba(6, 182, 212, 0.15);
        color: #22d3ee;
        border: 1px solid rgba(6, 182, 212, 0.3);
    }
    .badge-logfire {
        background: rgba(255, 87, 34, 0.15);
        color: #ff7043;
        border: 1px solid rgba(255, 87, 34, 0.3);
    }

    /* Path Nodes Flow */
    .flow-step {
        display: inline-block;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        color: #cbd5e1;
        font-family: 'JetBrains Mono', monospace;
    }
    .flow-arrow {
        color: #64748b;
        font-size: 0.8rem;
        margin: 0 4px;
    }

    /* Glass Expanders */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.3) !important;
        border-radius: 8px !important;
    }

    /* Chat Messages styling */
    .stChatMessage {
        border-radius: 14px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)


# ── Initialization & Graph Loading (Cached) ────────────────────────────────
@st.cache_resource(show_spinner="Initializing Agent Orchestrator & Logfire Tracing...")
def init_agent_system():
    from agents.trace import setup_tracing
    from agents.graph import build_graph
    setup_tracing()
    compiled_graph = build_graph()
    return compiled_graph

try:
    graph = init_agent_system()
except Exception as e:
    st.error(f"⚠️ Error initializing Agent system: {e}")
    graph = None


# ── Sidebar Configuration & Telemetry ──────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛️ Command Center")
    
    # Session Management
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"sess_{str(uuid.uuid4())[:8]}"

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        st.caption("Active Session ID:")
        st.code(st.session_state.session_id, language="text")
    with col_s2:
        if st.button("🔄", help="Start fresh session"):
            st.session_state.session_id = f"sess_{str(uuid.uuid4())[:8]}"
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # System Telemetry & Status
    st.markdown("#### ⚡ System Telemetry")
    groq_ok = bool(os.getenv("GROQ_API_KEY"))
    gemini_ok = bool(os.getenv("GOOGLE_API_KEY"))
    tavily_ok = bool(os.getenv("TAVILY_API_KEY"))
    logfire_ok = bool(os.getenv("LOG_FIRE_TOKEN") or os.getenv("LOGFIRE_TOKEN"))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"{'🟢' if groq_ok else '🔴'} **Groq LLaMA**")
        st.markdown(f"{'🔵' if gemini_ok else '⚪'} **Gemini 2.5**")
    with c2:
        st.markdown(f"{'🌐' if tavily_ok else '⚪'} **Tavily Search**")
        st.markdown(f"{'🔥' if logfire_ok else '⚪'} **Logfire Trace**")

    st.divider()

    # Routing & Specialist Architecture Map
    st.markdown("#### 🗺️ Multi-Agent Architecture")
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06); font-size: 0.82rem;">
        <div style="margin-bottom: 6px;"><b>1. 🧠 Planner</b> <span style="color:#94a3b8;">(Intent Classifier)</span></div>
        <div style="margin-left: 12px; margin-bottom: 4px;">├─ <span class="badge badge-explain">🎓 Explainer</span> <span style="color:#64748b;">Concept breakdown</span></div>
        <div style="margin-left: 12px; margin-bottom: 4px;">├─ <span class="badge badge-analyze">🔍 Analyst</span> <span style="color:#64748b;">Tradeoffs & comparisons</span></div>
        <div style="margin-left: 12px; margin-bottom: 4px;">├─ <span class="badge badge-create">✨ Creator</span> <span style="color:#64748b;">Solutions & ideation</span></div>
        <div style="margin-left: 12px; margin-bottom: 6px;">└─ <span class="badge badge-search">🌐 Searcher</span> <span style="color:#64748b;">Live web retrieval</span></div>
        <div><b>2. 🎨 Formatter</b> <span style="color:#94a3b8;">(Executive Polish & Delivery)</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Observability Portal Link
    st.markdown("#### 🔥 Logfire Observability")
    st.caption("Inspect live spans, latencies, tokens, and model completions in real-time.")
    st.link_button("Open Logfire Console ↗", "https://logfire-eu.pydantic.dev", use_container_width=True)

    st.divider()

    # Chat controls
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── Main Header & Hero Banner ──────────────────────────────────────────────
st.markdown("""
<div class="brand-container">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
            <h1 class="brand-title">⚡ Nexus Multi-Agent AI Studio</h1>
            <div class="brand-subtitle">
                Autonomous LangGraph Specialist Orchestrator · Real-Time Logfire Observability · Groq & Gemini Powered
            </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <span class="badge badge-logfire">🔥 Logfire Active</span>
            <span class="badge badge-explain">🤖 Multi-Agent</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Top Metrics Bar ────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

user_msgs_count = len([m for m in st.session_state.messages if m["role"] == "user"])
last_latency = st.session_state.get("last_latency", 0.0)
last_intent = st.session_state.get("last_intent", "Idle")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Queries</div>
        <div class="metric-value">{user_msgs_count}</div>
    </div>
    """, unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Last Classified Intent</div>
        <div class="metric-value" style="font-size: 1.05rem; text-transform: capitalize;">{last_intent}</div>
    </div>
    """, unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Last Execution Time</div>
        <div class="metric-value">{last_latency:.2f}s</div>
    </div>
    """, unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Specialist Nodes</div>
        <div class="metric-value">4 Active</div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer


# ── Empty State / Quick-Start Inspirations ─────────────────────────────────
if not st.session_state.messages:
    st.markdown("### 💡 Quick-Start Inspiration Prompts")
    st.caption("Click any query below to test automated specialist routing:")
    
    col_q1, col_q2 = st.columns(2)
    
    with col_q1:
        if st.button("🎓 **Explainer:** What is Attention Mechanism and why is it important in LLMs?", use_container_width=True):
            st.session_state.selected_prompt = "What is Attention Mechanism and why is it important in LLMs?"
            st.rerun()
        if st.button("🔍 **Analyst:** Compare RAG vs Fine-Tuning for domain-specific knowledge.", use_container_width=True):
            st.session_state.selected_prompt = "Compare RAG vs Fine-Tuning for domain-specific knowledge."
            st.rerun()

    with col_q2:
        if st.button("✨ **Creator:** Give me 5 innovative architecture ideas for LLM Guardrails & Security.", use_container_width=True):
            st.session_state.selected_prompt = "Give me 5 innovative architecture ideas for LLM Guardrails & Security."
            st.rerun()
        if st.button("🌐 **Web Search:** What are the latest developments and releases in OpenAI GPT models?", use_container_width=True):
            st.session_state.selected_prompt = "What are the latest developments and releases in OpenAI GPT models?"
            st.rerun()

    st.markdown("---")


# ── Render Chat History ───────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="⚡"):
            meta = msg.get("meta", {})
            intent = meta.get("intent", "explain")
            
            badge_class = f"badge-{intent}" if intent in ("explain", "analyze", "create", "search") else "badge-explain"
            badge_icon = {
                "explain": "🎓 Explainer Specialist",
                "analyze": "🔍 Analyst Specialist",
                "create": "✨ Creator Specialist",
                "search": "🌐 Web Search Specialist"
            }.get(intent, "🤖 AI Specialist")
            
            st.markdown(f'<span class="badge {badge_class}">{badge_icon}</span>', unsafe_allow_html=True)
            st.markdown(msg["content"])
            
            if meta:
                with st.expander("⚡ Deep Logfire Trace & Pipeline Diagnostics", expanded=False):
                    tab_trace, tab_sources, tab_raw = st.tabs(["📊 Execution Path & Telemetry", "🌐 Sources & Search", "🔍 Raw JSON State"])
                    
                    with tab_trace:
                        path_nodes = meta.get("path_nodes", [])
                        if path_nodes:
                            flow_html = ' <span class="flow-arrow">➔</span> '.join([f'<span class="flow-step">{node}</span>' for node in path_nodes])
                            st.markdown(f"**Pipeline Flow:** {flow_html}", unsafe_allow_html=True)
                        
                        col_m1, col_m2 = st.columns(2)
                        with col_m1:
                            st.caption("⏱️ Execution Latency:")
                            st.markdown(f"**{meta.get('latency_s', 0):.2f} seconds**")
                        with col_m2:
                            st.caption("🤖 Model Chain:")
                            st.markdown(f"`{meta.get('model_used', 'Groq')}`")
                    
                    with tab_sources:
                        sources = meta.get("sources", [])
                        if sources:
                            st.markdown("**Web Citations Retrieved by Tavily:**")
                            for idx, s in enumerate(sources, 1):
                                st.markdown(f"- [{s}]({s})")
                        else:
                            st.info("No external web retrieval required. Response generated from internal specialist knowledge.")

                    with tab_raw:
                        st.json(meta)


# ── Chat Input & Agent Execution Flow ──────────────────────────────────────
user_query = st.chat_input("Ask a question, request an analysis, brainstorm ideas, or search real-time info...")

if getattr(st.session_state, "selected_prompt", None):
    user_query = st.session_state.selected_prompt
    st.session_state.selected_prompt = None

if user_query:
    if graph is None:
        st.error("Agent graph is not initialized. Please check your API keys and configuration.")
        st.stop()

    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_query)

    # 2. Execute Multi-Agent Graph
    with st.chat_message("assistant", avatar="⚡"):
        with st.status("🧠 Multi-Agent Orchestration in Progress...", expanded=True) as status_box:
            st.write("🔍 Classifying query intent with **Planner Node**...")
            t_start = time.time()
            
            initial_state = {
                "question": user_query,
                "session_id": st.session_state.session_id,
                "intent": "",
                "specialist_output": "",
                "search_results": "",
                "final_answer": "",
                "model_used": "",
                "node_path": [],
                "sources": [],
            }

            try:
                result = graph.invoke(initial_state)
                t_end = time.time()
                latency = t_end - t_start
                
                st.session_state.last_latency = latency
                st.session_state.last_intent = result.get("intent", "explain")
                
                intent = result.get("intent", "explain")
                specialist_name = {
                    "explain": "Explainer",
                    "analyze": "Analyst",
                    "create": "Creator",
                    "search": "Web Searcher"
                }.get(intent, "Specialist")
                st.write(f"✨ Routed to **{specialist_name} Specialist** ➔ Polishing in **Formatter Node**")
                
                status_box.update(label=f"✅ Completed via {specialist_name} in {latency:.2f}s", state="complete", expanded=False)

            except Exception as e:
                status_box.update(label="❌ Execution Failed", state="error", expanded=True)
                st.error(f"Error during agent invocation: {e}")
                st.stop()

        # Render output
        final_answer = result.get("final_answer", result.get("specialist_output", "No response generated."))
        
        badge_class = f"badge-{intent}" if intent in ("explain", "analyze", "create", "search") else "badge-explain"
        badge_icon = {
            "explain": "🎓 Explainer Specialist",
            "analyze": "🔍 Analyst Specialist",
            "create": "✨ Creator Specialist",
            "search": "🌐 Web Search Specialist"
        }.get(intent, "🤖 AI Specialist")
        
        st.markdown(f'<span class="badge {badge_class}">{badge_icon}</span>', unsafe_allow_html=True)
        st.markdown(final_answer)

        # Meta info
        meta_data = {
            "intent": intent,
            "path_nodes": result.get("node_path", []),
            "model_used": result.get("model_used", "Groq LLaMA 3.3 70B"),
            "session_id": result.get("session_id", st.session_state.session_id),
            "latency_s": round(latency, 3),
            "sources": result.get("sources", []),
            "specialist_raw_output": result.get("specialist_output", ""),
        }

        with st.expander("⚡ Deep Logfire Trace & Pipeline Diagnostics", expanded=False):
            st.json(meta_data)

        # Append to state
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_answer,
            "meta": meta_data,
        })
