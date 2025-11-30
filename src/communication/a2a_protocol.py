"""
A2A Protocol - Agent-to-Agent Communication

This allows agents to talk to each other directly.
Think of it like a messaging system between agents.

Example:
- Scanner Agent finds a complex issue
- Scanner asks Fixer Agent: "What's the best way to fix this?"
- Fixer responds with a strategy
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class A2AMessage:
    """
    Message format for agent-to-agent communication
    
    Simple structure:
    - from_agent: Who sent it
    - to_agent: Who should receive it
    - message_type: What kind of message (query, delegate, notify)
    - payload: The actual data
    """
    from_agent: str
    to_agent: str
    message_type: str  # 'query', 'delegate', 'notify', 'response'
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'from_agent': self.from_agent,
            'to_agent': self.to_agent,
            'message_type': self.message_type,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat(),
            'trace_id': self.trace_id
        }


class A2AProtocol:
    """
    Agent-to-Agent communication protocol
    
    Simple explanation:
    - Agents can send messages to each other
    - Messages are routed to the right agent
    - Agents can query, delegate tasks, or notify each other
    """
    
    def __init__(self):
        """Initialize A2A protocol"""
        self.message_queue: List[A2AMessage] = []
        self.message_history: List[A2AMessage] = []
        self.agent_handlers: Dict[str, Any] = {}  # Agent name -> handler function
    
    def register_agent(self, agent_name: str, handler_function):
        """
        Register an agent to receive messages
        
        Example:
            protocol.register_agent("FixerAgent", fixer.handle_message)
        """
        self.agent_handlers[agent_name] = handler_function
    
    def send_message(self, message: A2AMessage) -> bool:
        """
        Send a message from one agent to another
        
        Returns:
            True if message was sent successfully
        """
        self.message_queue.append(message)
        self.message_history.append(message)
        
        # Try to deliver immediately if handler is registered
        if message.to_agent in self.agent_handlers:
            try:
                handler = self.agent_handlers[message.to_agent]
                response = handler(message)
                return True
            except Exception as e:
                print(f"⚠️  Error delivering message to {message.to_agent}: {e}")
                return False
        
        return True
    
    def query(self, from_agent: str, to_agent: str, question: str, context: Dict = None) -> Optional[Dict]:
        """
        Send a query message (ask a question)
        
        Example:
            response = protocol.query("ScannerAgent", "FixerAgent", 
                                    "What's the best fix for missing values?", 
                                    {"column": "age", "count": 5})
        """
        message = A2AMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type="query",
            payload={
                'question': question,
                'context': context or {}
            }
        )
        
        self.send_message(message)
        
        # If handler exists, get response
        if to_agent in self.agent_handlers:
            handler = self.agent_handlers[to_agent]
            return handler(message)
        
        return None
    
    def delegate(self, from_agent: str, to_agent: str, task: str, data: Any) -> Optional[Any]:
        """
        Delegate a task to another agent
        
        Example:
            result = protocol.delegate("Orchestrator", "ScannerAgent", 
                                     "scan_column", column_data)
        """
        message = A2AMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type="delegate",
            payload={
                'task': task,
                'data': str(data)  # Serialize data
            }
        )
        
        self.send_message(message)
        
        if to_agent in self.agent_handlers:
            handler = self.agent_handlers[to_agent]
            return handler(message)
        
        return None
    
    def notify(self, from_agent: str, to_agent: str, event: str, details: Dict = None):
        """
        Send a notification (one-way message)
        
        Example:
            protocol.notify("FixerAgent", "ValidatorAgent", 
                          "fix_completed", {"fixes": 3})
        """
        message = A2AMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type="notify",
            payload={
                'event': event,
                'details': details or {}
            }
        )
        
        self.send_message(message)
    
    def get_message_history(self, agent_name: str = None) -> List[Dict[str, Any]]:
        """Get message history, optionally filtered by agent"""
        if agent_name:
            return [m.to_dict() for m in self.message_history 
                   if m.from_agent == agent_name or m.to_agent == agent_name]
        return [m.to_dict() for m in self.message_history]

