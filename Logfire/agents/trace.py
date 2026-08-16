import os
import logfire
from dotenv import load_dotenv

load_dotenv()

def setup_tracing() -> None:
    """
    Configure Logfire once for the entire app.
    Call this exactly once — cached in Streamlit via st.cache_resource.
    """
    token = os.getenv("LOG_FIRE_TOKEN") or os.getenv("LOGFIRE_TOKEN")
    try:
        if token:
            logfire.configure(
                token=token,
                service_name="multi-agent-system",
                send_to_logfire=True,
                console=False,
            )
        else:
            logfire.configure(
                send_to_logfire=False,
                console=False,
            )
        # Instrument OpenAI-compatible calls (Groq & Gemini)
        logfire.instrument_openai()
    except Exception as e:
        print(f"[Logfire Setup Warning] Could not configure Logfire: {e}")