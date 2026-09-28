"""Couche LLM : Llama (Groq) via LangChain, avec modèles de secours."""
import os
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

_PROMPT = ChatPromptTemplate.from_messages([("system", "{system}"), ("human", "{user}")])


def _models() -> list[str]:
    primary = os.getenv("GROQ_MODEL", "llama-3.2-3b-preview")
    fallbacks = os.getenv("GROQ_FALLBACK_MODELS", "llama-3.1-8b-instant,llama-3.3-70b-versatile")
    out = []
    for m in [primary, *[x.strip() for x in fallbacks.split(",") if x.strip()]]:
        if m not in out:
            out.append(m)
    return out


def llm_available() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def ask(system: str, user: str, temperature: float = 0.2, max_tokens: int = 700):
    """Retourne (texte, modèle_utilisé) ou (None, None) si le LLM est indisponible."""
    if not llm_available():
        return None, None
    for model in _models():
        try:
            llm = ChatGroq(model=model, temperature=temperature, max_tokens=max_tokens,
                           timeout=30, max_retries=1)
            chain = _PROMPT | llm | StrOutputParser()
            return chain.invoke({"system": system, "user": user}).strip(), model
        except Exception:
            continue
    return None, None
