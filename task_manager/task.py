"""
Task model for the Professional Task Manager.

This module defines the Task class and related enums for managing tasks
with properties like priority, status, due dates, and categories.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
import json


class TaskStatus(Enum):
    """Enumeration for task status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Enumeration for task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class Task:
    """
    Represents a single task with all its properties.
    
    Attributes:
        id: Unique identifier for the task
        title: Task title/description
        description: Detailed task description
        status: Current task status
        priority: Task priority level
        category: Task category for organization
        due_date: Optional due date for the task
        created_at: Task creation timestamp
        updated_at: Last update timestamp
        completed_at: Task completion timestamp
        tags: List of tags for task categorization
    """
    
    def __init__(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        category: str = "general",
        due_date: Optional[datetime] = None,
        tags: Optional[list] = None,
        task_id: Optional[int] = None
    ) -> None:
        """
        Initialize a new task.
        
        Args:
            title: Task title/description
            description: Detailed task description
            priority: Task priority level
            category: Task category
            due_date: Optional due date
            tags: List of tags for categorization
            task_id: Optional existing task ID
        """
        self.id = task_id or self._generate_id()
        self.title = title
        self.description = description
        self.status = TaskStatus.TODO
        self.priority = priority
        self.category = category
        self.due_date = due_date
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at = None
        self.tags = tags or []
    
    def _generate_id(self) -> int:
        """Generate a unique task ID based on timestamp."""
        return int(datetime.now().timestamp() * 1000)
    
    def mark_done(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_in_progress(self) -> None:
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()
    
    def mark_cancelled(self) -> None:
        """Mark task as cancelled."""
        self.status = TaskStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[TaskPriority] = None,
        category: Optional[str] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[list] = None
    ) -> None:
        """
        Update task properties.
        
        Args:
            title: New task title
            description: New task description
            priority: New task priority
            category: New task category
            due_date: New due date
            tags: New tags list
        """
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        if category is not None:
            self.category = category
        if due_date is not None:
            self.due_date = due_date
        if tags is not None:
            self.tags = tags
        
        self.updated_at = datetime.now()
    
    def is_overdue(self) -> bool:
        """
        Check if task is overdue.
        
        Returns:
            True if task is overdue, False otherwise
        """
        if self.due_date is None or self.status in [TaskStatus.DONE, TaskStatus.CANCELLED]:
            return False
        return datetime.now() > self.due_date
    
    def days_until_due(self) -> Optional[int]:
        """
        Get days remaining until due date.
        
        Returns:
            Number of days until due, None if no due date
        """
        if self.due_date is None:
            return None
        
        delta = self.due_date - datetime.now()
        return delta.days
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert task to dictionary representation.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'category': self.category,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create task from dictionary representation.
        
        Args:
            data: Dictionary containing task data
            
        Returns:
            Task instance
        """
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            priority=TaskPriority(data.get('priority', TaskPriority.MEDIUM.value)),
            category=data.get('category', 'general'),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            tags=data.get('tags', []),
            task_id=data['id']
        )
        
        task.status = TaskStatus(data.get('status', TaskStatus.TODO.value))
        task.created_at = datetime.fromisoformat(data['created_at'])
        task.updated_at = datetime.fromisoformat(data['updated_at'])
        if data.get('completed_at'):
            task.completed_at = datetime.fromisoformat(data['completed_at'])
        
        return task
    
    def __str__(self) -> str:
        """String representation of the task."""
        status_icon = {
            TaskStatus.TODO: "⏳",
            TaskStatus.IN_PROGRESS: "🔄", 
            TaskStatus.DONE: "✅",
            TaskStatus.CANCELLED: "❌"
        }
        
        priority_color = {
            TaskPriority.LOW: "🟢",
            TaskPriority.MEDIUM: "🟡",
            TaskPriority.HIGH: "🟠",
            TaskPriority.URGENT: "🔴"
        }
        
        return f"{status_icon[self.status]} {priority_color[self.priority]} {self.title}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Task(id={self.id}, title='{self.title}', status={self.status.value}, priority={self.priority.value})"