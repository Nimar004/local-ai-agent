"""
Memory System for AI Agent
Provides conversation memory, learning, and context retention.
"""

import asyncio
import json
import logging
import os
import pickle
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
import hashlib


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    content: str
    memory_type: str  # conversation, fact, preference, skill
    timestamp: float
    importance: float  # 0.0 to 1.0
    access_count: int = 0
    last_accessed: float = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationMemory:
    """Memory for a conversation session."""
    session_id: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class MemoryManager:
    """
    Manages AI agent memory with learning and context retention.
    
    Features:
    - Short-term memory (current conversation)
    - Long-term memory (persistent storage)
    - Semantic memory (facts and knowledge)
    - Episodic memory (past experiences)
    - Procedural memory (skills and procedures)
    """
    
    def __init__(self, storage_dir: str = "~/ai-agent/memory"):
        """Initialize the Memory Manager."""
        self.logger = logging.getLogger("MemoryManager")
        self._storage_dir = Path(os.path.expanduser(storage_dir))
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory stores
        self._short_term: Dict[str, ConversationMemory] = {}
        self._long_term: Dict[str, MemoryEntry] = {}
        self._semantic: Dict[str, MemoryEntry] = {}
        self._episodic: List[MemoryEntry] = []
        self._procedural: Dict[str, MemoryEntry] = {}
        
        # Load existing memories
        self._load_memories()
        
    def _load_memories(self) -> None:
        """Load memories from disk."""
        try:
            # Load long-term memories
            long_term_file = self._storage_dir / "long_term.pkl"
            if long_term_file.exists():
                with open(long_term_file, "rb") as f:
                    self._long_term = pickle.load(f)
                    
            # Load semantic memories
            semantic_file = self._storage_dir / "semantic.pkl"
            if semantic_file.exists():
                with open(semantic_file, "rb") as f:
                    self._semantic = pickle.load(f)
                    
            # Load episodic memories
            episodic_file = self._storage_dir / "episodic.pkl"
            if episodic_file.exists():
                with open(episodic_file, "rb") as f:
                    self._episodic = pickle.load(f)
                    
            # Load procedural memories
            procedural_file = self._storage_dir / "procedural.pkl"
            if procedural_file.exists():
                with open(procedural_file, "rb") as f:
                    self._procedural = pickle.load(f)
                    
            self.logger.info(f"Loaded {len(self._long_term)} long-term memories")
            
        except Exception as e:
            self.logger.error(f"Failed to load memories: {e}")
            
    def _save_memories(self) -> None:
        """Save memories to disk."""
        try:
            # Save long-term memories
            with open(self._storage_dir / "long_term.pkl", "wb") as f:
                pickle.dump(self._long_term, f)
                
            # Save semantic memories
            with open(self._storage_dir / "semantic.pkl", "wb") as f:
                pickle.dump(self._semantic, f)
                
            # Save episodic memories
            with open(self._storage_dir / "episodic.pkl", "wb") as f:
                pickle.dump(self._episodic, f)
                
            # Save procedural memories
            with open(self._storage_dir / "procedural.pkl", "wb") as f:
                pickle.dump(self._procedural, f)
                
        except Exception as e:
            self.logger.error(f"Failed to save memories: {e}")
            
    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for memory content."""
        return hashlib.md5(content.encode()).hexdigest()[:16]
        
    def add_conversation_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to conversation memory."""
        if session_id not in self._short_term:
            self._short_term[session_id] = ConversationMemory(session_id=session_id)
            
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        self._short_term[session_id].messages.append(message)
        self._short_term[session_id].updated_at = time.time()
        
        # Extract important information for long-term memory
        if role == "user":
            self._extract_important_info(content, session_id)
            
    def _extract_important_info(self, content: str, session_id: str) -> None:
        """Extract important information from user messages."""
        # Simple keyword-based extraction
        important_keywords = [
            "remember", "important", "always", "never", "prefer",
            "like", "dislike", "favorite", "name", "call me"
        ]
        
        content_lower = content.lower()
        for keyword in important_keywords:
            if keyword in content_lower:
                # Store as preference
                self.add_memory(
                    content=content,
                    memory_type="preference",
                    importance=0.7,
                    tags=["user_preference", session_id]
                )
                break
                
    def add_memory(
        self,
        content: str,
        memory_type: str = "fact",
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a memory entry."""
        memory_id = self._generate_id(content)
        
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            timestamp=time.time(),
            importance=importance,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store in appropriate memory type
        if memory_type == "fact":
            self._semantic[memory_id] = entry
        elif memory_type == "experience":
            self._episodic.append(entry)
        elif memory_type == "skill":
            self._procedural[memory_id] = entry
        else:
            self._long_term[memory_id] = entry
            
        # Save to disk
        self._save_memories()
        
        self.logger.info(f"Added {memory_type} memory: {content[:50]}...")
        return memory_id
        
    def search_memories(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memories by content."""
        results = []
        query_lower = query.lower()
        
        # Search all memory types
        all_memories = []
        all_memories.extend(self._long_term.values())
        all_memories.extend(self._semantic.values())
        all_memories.extend(self._episodic)
        all_memories.extend(self._procedural.values())
        
        # Filter by memory type if specified
        if memory_types:
            all_memories = [m for m in all_memories if m.memory_type in memory_types]
            
        # Search by content
        for memory in all_memories:
            if query_lower in memory.content.lower():
                # Update access count
                memory.access_count += 1
                memory.last_accessed = time.time()
                results.append(memory)
                
        # Sort by importance and access count
        results.sort(key=lambda m: (m.importance, m.access_count), reverse=True)
        
        return results[:limit]
        
    def get_relevant_context(
        self,
        query: str,
        max_tokens: int = 2000
    ) -> str:
        """Get relevant context for a query."""
        memories = self.search_memories(query, limit=5)
        
        if not memories:
            return ""
            
        context_parts = []
        for memory in memories:
            context_parts.append(f"[{memory.memory_type}] {memory.content}")
            
        context = "\n".join(context_parts)
        
        # Truncate if too long
        if len(context) > max_tokens:
            context = context[:max_tokens] + "..."
            
        return context
        
    def get_conversation_history(
        self,
        session_id: str,
        max_messages: int = 20
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        if session_id not in self._short_term:
            return []
            
        messages = self._short_term[session_id].messages
        return messages[-max_messages:]
        
    def learn_from_interaction(
        self,
        user_input: str,
        agent_response: str,
        feedback: Optional[str] = None
    ) -> None:
        """Learn from user interaction."""
        # Store the interaction
        interaction = f"User: {user_input}\nAgent: {agent_response}"
        
        self.add_memory(
            content=interaction,
            memory_type="experience",
            importance=0.6,
            tags=["interaction", "learning"]
        )
        
        # Learn from feedback if provided
        if feedback:
            self.add_memory(
                content=f"Feedback: {feedback}",
                memory_type="preference",
                importance=0.8,
                tags=["feedback", "learning"]
            )
            
    def get_user_preferences(self) -> Dict[str, Any]:
        """Get learned user preferences."""
        preferences = {}
        
        # Search for preference memories
        pref_memories = self.search_memories(
            "prefer",
            memory_types=["preference"],
            limit=20
        )
        
        for memory in pref_memories:
            # Extract preference from content
            if "prefer" in memory.content.lower():
                preferences[memory.id] = {
                    "content": memory.content,
                    "importance": memory.importance,
                    "timestamp": memory.timestamp
                }
                
        return preferences
        
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "short_term_sessions": len(self._short_term),
            "long_term_memories": len(self._long_term),
            "semantic_memories": len(self._semantic),
            "episodic_memories": len(self._episodic),
            "procedural_memories": len(self._procedural),
            "total_memories": (
                len(self._long_term) +
                len(self._semantic) +
                len(self._episodic) +
                len(self._procedural)
            )
        }
        
    def clear_session(self, session_id: str) -> None:
        """Clear a conversation session."""
        if session_id in self._short_term:
            del self._short_term[session_id]
            
    def clear_all_memories(self) -> None:
        """Clear all memories (use with caution)."""
        self._short_term.clear()
        self._long_term.clear()
        self._semantic.clear()
        self._episodic.clear()
        self._procedural.clear()
        
        # Delete files
        for file in self._storage_dir.glob("*.pkl"):
            file.unlink()
            
        self.logger.warning("All memories cleared")