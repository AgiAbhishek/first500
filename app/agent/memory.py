"""
Session-based conversation memory management.
"""

import time
import logging
import uuid
from typing import Dict, List, Optional
from collections import defaultdict
from app.config import settings

logger = logging.getLogger(__name__)


class Message:
    """Represents a single message in the conversation."""
    
    def __init__(self, role: str, content: str, timestamp: float = None):
        self.role = role  # 'user', 'assistant', 'system'
        self.content = content
        self.timestamp = timestamp or time.time()
    
    def to_dict(self):
        """Convert to dictionary for OpenAI API."""
        return {"role": self.role, "content": self.content}
    
    def __repr__(self):
        return f"Message(role={self.role}, content={self.content[:50]}...)"


class SessionMemory:
    """Manages conversation history for sessions."""
    
    def __init__(self):
        """Initialize session memory."""
        self.sessions: Dict[str, List[Message]] = defaultdict(list)
        self.session_timestamps: Dict[str, float] = {}
        self.max_history = settings.max_conversation_history
        self.ttl = settings.session_ttl
        logger.info(f"Session memory initialized (TTL: {self.ttl}s, max history: {self.max_history})")
    
    def create_session(self) -> str:
        """
        Create a new session.
        
        Returns:
            New session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        self.session_timestamps[session_id] = time.time()
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to a session's history.
        
        Args:
            session_id: Session identifier
            role: Message role ('user', 'assistant', 'system')
            content: Message content
        """
        if not self._is_session_valid(session_id):
            logger.warning(f"Session {session_id} is invalid or expired")
            return
        
        message = Message(role=role, content=content)
        self.sessions[session_id].append(message)
        
        # Update session timestamp
        self.session_timestamps[session_id] = time.time()
        
        # Trim history if needed (keep only recent messages)
        if len(self.sessions[session_id]) > self.max_history * 2:  # *2 for user+assistant pairs
            # Keep system messages and most recent conversations
            system_messages = [m for m in self.sessions[session_id] if m.role == 'system']
            recent_messages = [m for m in self.sessions[session_id] if m.role != 'system'][-self.max_history * 2:]
            self.sessions[session_id] = system_messages + recent_messages
            logger.info(f"Trimmed session {session_id} history to {len(self.sessions[session_id])} messages")
    
    def get_history(self, session_id: str) -> List[Dict]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dictionaries in OpenAI format
        """
        if not self._is_session_valid(session_id):
            logger.warning(f"Session {session_id} not found or expired")
            return []
        
        return [msg.to_dict() for msg in self.sessions[session_id]]
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists and is valid.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session exists and is valid
        """
        return self._is_session_valid(session_id)
    
    def _is_session_valid(self, session_id: str) -> bool:
        """
        Check if session exists and hasn't expired.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if valid, False otherwise
        """
        if session_id not in self.sessions:
            return False
        
        # Check if session has expired
        last_access = self.session_timestamps.get(session_id, 0)
        if time.time() - last_access > self.ttl:
            logger.info(f"Session {session_id} expired")
            self._cleanup_session(session_id)
            return False
        
        return True
    
    def _cleanup_session(self, session_id: str):
        """
        Remove a session from memory.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.session_timestamps:
            del self.session_timestamps[session_id]
        logger.info(f"Cleaned up session {session_id}")
    
    def cleanup_expired_sessions(self):
        """Clean up all expired sessions."""
        current_time = time.time()
        expired_sessions = [
            sid for sid, timestamp in self.session_timestamps.items()
            if current_time - timestamp > self.ttl
        ]
        
        for session_id in expired_sessions:
            self._cleanup_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_session_count(self) -> int:
        """Get number of active sessions."""
        return len(self.sessions)


# Global instance
session_memory = SessionMemory()
