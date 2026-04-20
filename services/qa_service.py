""" 
QA Service module.
Connects RAG pipeline with LLM to answer questions.
"""
import asyncio
import concurrent.futures
import logging
import time
from typing import Dict, Optional, Tuple

from rag.rag_pipeline import RAGPipeline
from ai.llm import GroqLLM
from ai.prompt import build_prompt, get_system_prompt
from services.service import get_child_summary, get_latest_activity_timestamp

logger = logging.getLogger(__name__)

# Thread pool shared across requests for CPU / IO-bound work
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# In-memory cache: child_id -> (summary_text, expiry_timestamp, last_activity_ts)
# If DB is updated within TTL we invalidate so the AI uses updated data.
_child_summary_cache: Dict[str, Tuple[str, float, Optional[object]]] = {}
_CHILD_SUMMARY_TTL_SECONDS = 120  # 2 minutes


def _get_cached_child_summary(child_id: str) -> Optional[str]:
    """Return cached summary if present, not expired, and DB unchanged; otherwise None."""
    print(f">>> _get_cached_child_summary({child_id})", flush=True)
    now = time.time()
    if child_id not in _child_summary_cache:
        print("    cache MISS (not in cache)", flush=True)
        return None
    summary, expiry, last_ts = _child_summary_cache[child_id]
    if now >= expiry:
        del _child_summary_cache[child_id]
        print("    cache EXPIRED", flush=True)
        return None
    _ts_start = time.time()
    current_ts = get_latest_activity_timestamp(child_id)
    print(f"    get_latest_activity_timestamp took {time.time()-_ts_start:.2f}s", flush=True)
    if current_ts != last_ts:
        del _child_summary_cache[child_id]
        print("    cache INVALIDATED (DB changed)", flush=True)
        return None
    print("    cache HIT", flush=True)
    return summary


def _set_cached_child_summary(child_id: str, summary: str) -> None:
    """Store summary in cache with TTL and current last-activity ts."""
    _s = time.time()
    last_ts = get_latest_activity_timestamp(child_id)
    print(f"    _set_cached_child_summary -> get_latest_activity_timestamp: {time.time()-_s:.2f}s", flush=True)
    _child_summary_cache[child_id] = (
        summary,
        time.time() + _CHILD_SUMMARY_TTL_SECONDS,
        last_ts,
    )


class QAService:
    """Service for answering questions using RAG + LLM."""
    
    def __init__(self):
        """Initialize QA service with RAG pipeline and LLM."""
        self.rag_pipeline = RAGPipeline()
        self.llm = GroqLLM()
        
        # Initialize RAG pipeline
        self.rag_pipeline.initialize()
    
    # ── Synchronous helpers (run inside thread pool) ──────────────

    def _fetch_context(self, question: str) -> list:
        """Retrieve RAG context chunks (CPU + disk IO)."""
        print(">>> _fetch_context START (RAG retrieval)", flush=True)
        _s = time.time()
        result = self.rag_pipeline.retrieve_context(question, top_k=3)
        print(f"<<< _fetch_context DONE: {time.time()-_s:.2f}s  ({len(result)} chunks)", flush=True)
        return result

    @staticmethod
    def _fetch_child_summary(child_id: str) -> str:
        """Return child summary text, using in-memory cache when possible."""
        print(f">>> _fetch_child_summary START (child_id={child_id})", flush=True)
        _s = time.time()
        summary = _get_cached_child_summary(child_id)
        cache_hit = summary is not None
        if summary is None:
            print("    calling get_child_summary() ...", flush=True)
            summary = get_child_summary(child_id)
            print(f"    get_child_summary() returned in {time.time()-_s:.2f}s", flush=True)
            _set_cached_child_summary(child_id, summary)
        print(f"<<< _fetch_child_summary DONE (cache_hit={cache_hit}): {time.time()-_s:.2f}s", flush=True)
        return f"\n\n[Child Summary]\n{summary}"

    # ── Public async entry point ─────────────────────────────────

    async def answer_question_async(self, question: str, child_id: Optional[str] = None) -> Dict[str, str]:
        """
        Async version: runs RAG retrieval and child-summary fetch **in parallel**,
        then calls the LLM. Keeps the event loop free for other requests.
        """
        _total_start = time.time()
        print("\n" + "="*60, flush=True)
        print(f">>> answer_question_async START  question='{question[:60]}...'", flush=True)
        print("="*60, flush=True)
        loop = asyncio.get_event_loop()

        # Launch RAG retrieval and child-summary fetch concurrently
        print(">>> Launching parallel: _fetch_context + _fetch_child_summary", flush=True)
        context_future = loop.run_in_executor(_executor, self._fetch_context, question)

        child_summary_future = None
        if child_id:
            child_summary_future = loop.run_in_executor(_executor, self._fetch_child_summary, child_id)

        # Await both results (parallel) — child summary has a 5s timeout to avoid blocking
        context_chunks = await context_future
        child_summary_text = ""
        if child_summary_future:
            try:
                child_summary_text = await asyncio.wait_for(child_summary_future, timeout=2.0)
            except asyncio.TimeoutError:
                print("    ⚠️ _fetch_child_summary TIMED OUT (>5s) — skipping personalization", flush=True)
                child_summary_text = ""
            except Exception:
                child_summary_text = ""

        print(f"<<< Parallel phase DONE: {time.time()-_total_start:.2f}s", flush=True)

        # Build prompt (fast, CPU-only)
        print(">>> build_prompt START", flush=True)
        _bp = time.time()
        prompt = build_prompt(question, context_chunks)

        if child_summary_text:
            prompt = (
                f"{prompt}{child_summary_text}\n\n"
                "When the question is about this child's progress, activities, or performance: "
                "answer directly from the [Child Summary] above. Do NOT mention that this information "
                "is not in the PDFs or knowledge base\u2014simply give a clear, helpful answer based on the child's data."
            )

        system_prompt = get_system_prompt()
        print(f"<<< build_prompt DONE: {time.time()-_bp:.2f}s  (prompt len={len(prompt)})", flush=True)

        # LLM call
        print(">>> LLM generate START (Groq API call)", flush=True)
        _llm_start = time.time()
        try:
            answer = await loop.run_in_executor(
                _executor,
                lambda: self.llm.generate(prompt=prompt, system_prompt=system_prompt),
            )
            print(f"<<< LLM generate DONE: {time.time()-_llm_start:.2f}s", flush=True)
            print(f"<<< answer_question_async TOTAL: {time.time()-_total_start:.2f}s", flush=True)
            print("="*60 + "\n", flush=True)
            return {"answer": answer}

        except Exception as e:
            error_msg_en = f"I apologize, but I encountered an error while processing your question. Please try again later. Error: {str(e)}"
            error_msg_si = f"කණගාටුයි, නමුත් ඔබේ ප්‍රශ්නය සැකසීමේදී දෝෂයක් ඇති විය. කරුණාකර පසුව නැවත උත්සාහ කරන්න. දෝෂය: {str(e)}"
            from ai.prompt import detect_language
            lang = detect_language(question)
            error_msg = error_msg_si if lang == 'sinhala' else error_msg_en
            return {"answer": error_msg}

    def answer_question(self, question: str, child_id: Optional[str] = None) -> Dict[str, str]:
        """
        Synchronous fallback (kept for backward compatibility).
        Prefer answer_question_async from async endpoints.
        """
        context_chunks = self.rag_pipeline.retrieve_context(question, top_k=3)
        prompt = build_prompt(question, context_chunks)

        child_summary_text = ""
        if child_id:
            try:
                summary = _get_cached_child_summary(child_id)
                if summary is None:
                    summary = get_child_summary(child_id)
                    _set_cached_child_summary(child_id, summary)
                child_summary_text = f"\n\n[Child Summary]\n{summary}"
            except Exception:
                child_summary_text = ""

        if child_summary_text:
            prompt = (
                f"{prompt}{child_summary_text}\n\n"
                "When the question is about this child's progress, activities, or performance: "
                "answer directly from the [Child Summary] above. Do NOT mention that this information "
                "is not in the PDFs or knowledge base—simply give a clear, helpful answer based on the child's data."
            )

        system_prompt = get_system_prompt()

        try:
            answer = self.llm.generate(prompt=prompt, system_prompt=system_prompt)
            return {"answer": answer}
        except Exception as e:
            error_msg_en = f"I apologize, but I encountered an error while processing your question. Please try again later. Error: {str(e)}"
            error_msg_si = f"කණගාටුයි, නමුත් ඔබේ ප්‍රශ්නය සැකසීමේදී දෝෂයක් ඇති විය. කරුණාකර පසුව නැවත උත්සාහ කරන්න. දෝෂය: {str(e)}"
            from ai.prompt import detect_language
            lang = detect_language(question)
            error_msg = error_msg_si if lang == 'sinhala' else error_msg_en
            return {"answer": error_msg}
    
    def reload_knowledge_base(self) -> Dict[str, str]:
        """
        Reload the knowledge base from PDFs.
        
        Returns:
            Dictionary with status message
        """
        try:
            self.rag_pipeline.initialize(force_reload=True)
            return {"status": "Knowledge base reloaded successfully"}
        except Exception as e:
            return {"status": f"Error reloading knowledge base: {str(e)}"}
    
    def add_single_pdf(self, filename: str) -> Dict[str, str]:
        """
        Add a single PDF to the knowledge base without reloading everything.
        This is much faster than reloading the entire knowledge base.
        
        Args:
            filename: Name of the PDF file to add
        
        Returns:
            Dictionary with status message
        """
        try:
            self.rag_pipeline.add_single_pdf(filename)
            return {"status": f"PDF {filename} added to knowledge base successfully"}
        except Exception as e:
            return {"status": f"Error adding PDF {filename}: {str(e)}"}
    
    def remove_single_pdf(self, filename: str) -> Dict[str, str]:
        """
        Remove a single PDF from the knowledge base without reloading everything.
        This is much faster than reloading the entire knowledge base.
        
        Args:
            filename: Name of the PDF file to remove
        
        Returns:
            Dictionary with status message
        """
        try:
            self.rag_pipeline.remove_single_pdf(filename)
            return {"status": f"PDF {filename} removed from knowledge base successfully"}
        except Exception as e:
            return {"status": f"Error removing PDF {filename}: {str(e)}"}