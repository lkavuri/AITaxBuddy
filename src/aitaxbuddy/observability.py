"""Observability setup with Langfuse for tracing and monitoring."""

import logging
from typing import Any
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from aitaxbuddy.config import settings

logger = logging.getLogger(__name__)


class ObservabilityManager:
    """Manages tracing and observability for the AI Tax Buddy agent."""
    
    def __init__(self):
        self.langfuse_client = None
        self.callback_handler = None
        self._initialize_langfuse()
    
    def _initialize_langfuse(self) -> None:
        """Initialize Langfuse client and callback handler."""
        if not all([settings.langfuse_public_key, settings.langfuse_secret_key]):
            logger.warning(
                "Langfuse credentials not configured. Observability will be disabled."
            )
            return
        
        try:
            self.langfuse_client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
            )
            
            self.callback_handler = CallbackHandler(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
            )
            
            logger.info("Langfuse observability initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse: {e}")
    
    def get_callback_handler(self) -> CallbackHandler | None:
        """Get the Langfuse callback handler for tracing."""
        return self.callback_handler
    
    def trace_agent_run(
        self,
        session_id: str,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """Create a trace for an agent run."""
        if not self.langfuse_client:
            return None
        
        return self.langfuse_client.trace(
            name="tax_buddy_conversation",
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {},
        )
    
    def score_response(
        self,
        trace_id: str,
        score_name: str,
        score_value: float,
        comment: str | None = None,
    ) -> None:
        """Score a response for quality evaluation."""
        if not self.langfuse_client:
            return
        
        try:
            self.langfuse_client.score(
                trace_id=trace_id,
                name=score_name,
                value=score_value,
                comment=comment,
            )
        except Exception as e:
            logger.error(f"Failed to record score: {e}")
    
    def flush(self) -> None:
        """Flush all pending traces to Langfuse."""
        if self.langfuse_client:
            self.langfuse_client.flush()


# Global observability manager instance
observability = ObservabilityManager()
