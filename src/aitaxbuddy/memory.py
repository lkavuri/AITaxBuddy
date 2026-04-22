"""Memory management for AI Tax Buddy using Mem0."""

import logging
from typing import Any
from mem0 import Memory
from aitaxbuddy.config import settings

logger = logging.getLogger(__name__)


class TaxBuddyMemory:
    """Manages episodic and semantic memory for tax conversations."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.memory = None
        self._initialize_memory()
    
    def _initialize_memory(self) -> None:
        """Initialize Mem0 memory instance."""
        try:
            config = {
                "vector_store": {
                    "provider": "chroma",
                    "config": {
                        "collection_name": "tax_buddy_memory",
                        "path": "./chroma_db",
                    },
                },
            }
            
            if settings.mem0_api_key:
                config["api_key"] = settings.mem0_api_key
            
            self.memory = Memory.from_config(config)
            logger.info(f"Memory initialized for user: {self.user_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Mem0: {e}")
            logger.warning("Memory features will be disabled")
    
    def add_conversation(self, messages: list[dict[str, str]]) -> None:
        """
        Add a conversation to memory.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
        """
        if not self.memory:
            return
        
        try:
            self.memory.add(messages=messages, user_id=self.user_id)
            logger.debug(f"Added conversation to memory for user: {self.user_id}")
        except Exception as e:
            logger.error(f"Failed to add to memory: {e}")
    
    def add_fact(self, fact: str, metadata: dict[str, Any] | None = None) -> None:
        """
        Add a specific fact to memory (e.g., user is a sole trader).
        
        Args:
            fact: The fact to remember
            metadata: Additional metadata about the fact
        """
        if not self.memory:
            return
        
        try:
            self.memory.add(
                messages=[{"role": "user", "content": fact}],
                user_id=self.user_id,
                metadata=metadata or {},
            )
            logger.debug(f"Added fact to memory: {fact}")
        except Exception as e:
            logger.error(f"Failed to add fact: {e}")
    
    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        Search memory for relevant information.
        
        Args:
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of relevant memory items
        """
        if not self.memory:
            return []
        
        try:
            results = self.memory.search(query=query, user_id=self.user_id, limit=limit)
            return results if results else []
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []
    
    def get_all(self) -> list[dict[str, Any]]:
        """
        Get all memories for the user.
        
        Returns:
            List of all memory items
        """
        if not self.memory:
            return []
        
        try:
            results = self.memory.get_all(user_id=self.user_id)
            return results if results else []
        except Exception as e:
            logger.error(f"Failed to get memories: {e}")
            return []
    
    def delete_all(self) -> None:
        """Delete all memories for the user."""
        if not self.memory:
            return
        
        try:
            self.memory.delete_all(user_id=self.user_id)
            logger.info(f"Deleted all memories for user: {self.user_id}")
        except Exception as e:
            logger.error(f"Failed to delete memories: {e}")
    
    def get_context(self, query: str | None = None) -> str:
        """
        Get relevant memory context as a formatted string.
        
        Args:
            query: Optional query to search for relevant memories
        
        Returns:
            Formatted context string
        """
        if query:
            memories = self.search(query, limit=3)
        else:
            memories = self.get_all()
        
        if not memories:
            return "No previous context available."
        
        context_parts = ["Previous context about the user:"]
        for i, mem in enumerate(memories[:5], 1):
            content = mem.get("memory", mem.get("content", ""))
            if content:
                context_parts.append(f"{i}. {content}")
        
        return "\n".join(context_parts)
