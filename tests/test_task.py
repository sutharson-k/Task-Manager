"""
Test suite for the Task class.
"""

import pytest
from datetime import datetime, timedelta
from task_manager.task import Task, TaskStatus, TaskPriority


class TestTask:
    """Test cases for the Task class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.task = Task(
            title="Test Task",
            description="Test description",
            priority=TaskPriority.HIGH,
            category="test",
            tags=["test", "unit"]
        )
    
    def test_task_initialization(self):
        """Test task initialization with all parameters."""
        assert self.task.title == "Test Task"
        assert self.task.description == "Test description"
        assert self.task.priority == TaskPriority.HIGH
        assert self.task.category == "test"
        assert self.task.tags == ["test", "unit"]
        assert self.task.status == TaskStatus.TODO
        assert isinstance(self.task.id, int)
        assert isinstance(self.task.created_at, datetime)
        assert isinstance(self.task.updated_at, datetime)
        assert self.task.completed_at is None
    
    def test_task_initialization_defaults(self):
        """Test task initialization with default values."""
        task = Task(title="Simple Task")
        
        assert task.title == "Simple Task"
        assert task.description == ""
        assert task.priority == TaskPriority.MEDIUM
        assert task.category == "general"
        assert task.tags == []
        assert task.status == TaskStatus.TODO
    
    def test_task_mark_done(self):
        """Test marking task as done."""
        original_updated = self.task.updated_at
        
        self.task.mark_done()
        
        assert self.task.status == TaskStatus.DONE
        assert self.task.completed_at is not None
        assert self.task.updated_at > original_updated
    
    def test_task_mark_in_progress(self):
        """Test marking task as in progress."""
        original_updated = self.task.updated_at
        
        self.task.mark_in_progress()
        
        assert self.task.status == TaskStatus.IN_PROGRESS
        assert self.task.updated_at > original_updated
    
    def test_task_mark_cancelled(self):
        """Test marking task as cancelled."""
        original_updated = self.task.updated_at
        
        self.task.mark_cancelled()
        
        assert self.task.status == TaskStatus.CANCELLED
        assert self.task.updated_at > original_updated
    
    def test_task_update(self):
        """Test task update with all parameters."""
        new_title = "Updated Task"
        new_description = "Updated description"
        new_priority = TaskPriority.URGENT
        new_category = "updated"
        new_tags = ["updated"]
        new_due_date = datetime.now() + timedelta(days=7)
        
        self.task.update(
            title=new_title,
            description=new_description,
            priority=new_priority,
            category=new_category,
            tags=new_tags,
            due_date=new_due_date
        )
        
        assert self.task.title == new_title
        assert self.task.description == new_description
        assert self.task.priority == new_priority
        assert self.task.category == new_category
        assert self.task.tags == new_tags
        assert self.task.due_date == new_due_date
    
    def test_task_update_partial(self):
        """Test task update with partial parameters."""
        original_title = self.task.title
        original_description = self.task.description
        
        self.task.update(title="New Title")
        
        assert self.task.title == "New Title"
        assert self.task.description == original_description  # Should remain unchanged
    
    def test_task_is_overdue(self):
        """Test overdue task detection."""
        # Task without due date
        assert not self.task.is_overdue()
        
        # Task with future due date
        future_date = datetime.now() + timedelta(days=7)
        self.task.update(due_date=future_date)
        assert not self.task.is_overdue()
        
        # Task with past due date
        past_date = datetime.now() - timedelta(days=1)
        self.task.update(due_date=past_date)
        assert self.task.is_overdue()
        
        # Completed task should not be overdue
        self.task.mark_done()
        assert not self.task.is_overdue()
    
    def test_task_days_until_due(self):
        """Test days until due calculation."""
        # Task without due date
        assert self.task.days_until_due() is None
        
        # Task with future due date
        future_date = datetime.now() + timedelta(days=5)
        self.task.update(due_date=future_date)
        assert self.task.days_until_due() == 5
        
        # Task with past due date
        past_date = datetime.now() - timedelta(days=2)
        self.task.update(due_date=past_date)
        assert self.task.days_until_due() == -2
    
    def test_task_to_dict(self):
        """Test task to dictionary conversion."""
        due_date = datetime.now() + timedelta(days=1)
        self.task.update(due_date=due_date)
        
        task_dict = self.task.to_dict()
        
        assert task_dict['title'] == self.task.title
        assert task_dict['description'] == self.task.description
        assert task_dict['status'] == self.task.status.value
        assert task_dict['priority'] == self.task.priority.value
        assert task_dict['category'] == self.task.category
        assert task_dict['due_date'] == due_date.isoformat()
        assert task_dict['created_at'] == self.task.created_at.isoformat()
        assert task_dict['updated_at'] == self.task.updated_at.isoformat()
        assert task_dict['completed_at'] is None
        assert task_dict['tags'] == self.task.tags
    
    def test_task_from_dict(self):
        """Test task creation from dictionary."""
        due_date = datetime.now() + timedelta(days=1)
        created_at = datetime.now() - timedelta(days=1)
        updated_at = datetime.now() - timedelta(hours=1)
        
        task_dict = {
            'id': 12345,
            'title': 'Test Task from Dict',
            'description': 'Test description',
            'status': 'in_progress',
            'priority': 3,
            'category': 'test',
            'due_date': due_date.isoformat(),
            'created_at': created_at.isoformat(),
            'updated_at': updated_at.isoformat(),
            'completed_at': None,
            'tags': ['test']
        }
        
        task = Task.from_dict(task_dict)
        
        assert task.id == 12345
        assert task.title == 'Test Task from Dict'
        assert task.description == 'Test description'
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.category == 'test'
        assert task.due_date == due_date
        assert task.created_at == created_at
        assert task.updated_at == updated_at
        assert task.completed_at is None
        assert task.tags == ['test']
    
    def test_task_str_representation(self):
        """Test task string representation."""
        task_str = str(self.task)
        assert "Test Task" in task_str
        assert "🟠" in task_str  # High priority icon
        assert "⏳" in task_str  # Todo status icon
    
    def test_task_repr(self):
        """Test task detailed string representation."""
        task_repr = repr(self.task)
        assert "Task(" in task_repr
        assert "title='Test Task'" in task_repr
        assert "status='todo'" in task_repr
        assert "priority=3" in task_repr