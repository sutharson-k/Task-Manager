"""
Test suite for the TaskManager class.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from task_manager.task import Task, TaskPriority, TaskStatus
from task_manager.task_manager import TaskManager


class TestTaskManager:
    """Test cases for the TaskManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Use temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.manager = TaskManager(self.temp_file.name)

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_task_manager_initialization(self):
        """Test task manager initialization."""
        assert isinstance(self.manager.tasks, dict)
        assert len(self.manager.tasks) == 0
        assert self.manager.data_file == Path(self.temp_file.name)

    def test_create_task(self):
        """Test creating a new task."""
        task = self.manager.create_task(
            title="Test Task",
            description="Test description",
            priority=TaskPriority.HIGH,
            category="test",
            tags=["test"],
        )

        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.priority == TaskPriority.HIGH
        assert task.category == "test"
        assert task.tags == ["test"]
        assert task.id in self.manager.tasks
        assert self.manager.tasks[task.id] == task

    def test_create_task_defaults(self):
        """Test creating a task with default values."""
        task = self.manager.create_task(title="Simple Task")

        assert task.title == "Simple Task"
        assert task.description == ""
        assert task.priority == TaskPriority.MEDIUM
        assert task.category == "general"
        assert task.tags == []

    def test_get_task(self):
        """Test getting a task by ID."""
        task = self.manager.create_task(title="Test Task")

        retrieved_task = self.manager.get_task(task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.title == task.title

        # Test non-existent task
        non_existent = self.manager.get_task(99999)
        assert non_existent is None

    def test_get_all_tasks(self):
        """Test getting all tasks."""
        # Initially empty
        assert self.manager.get_all_tasks() == []

        # Add tasks
        task1 = self.manager.create_task(title="Task 1")
        task2 = self.manager.create_task(title="Task 2")

        all_tasks = self.manager.get_all_tasks()
        assert len(all_tasks) == 2
        assert task1 in all_tasks
        assert task2 in all_tasks

    def test_get_tasks_by_status(self):
        """Test filtering tasks by status."""
        task1 = self.manager.create_task(title="Task 1")
        task2 = self.manager.create_task(title="Task 2")
        task3 = self.manager.create_task(title="Task 3")

        # Mark some tasks with different statuses
        task1.mark_done()
        task2.mark_in_progress()
        # task3 remains TODO

        # Test filtering
        done_tasks = self.manager.get_tasks_by_status(TaskStatus.DONE)
        in_progress_tasks = self.manager.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        todo_tasks = self.manager.get_tasks_by_status(TaskStatus.TODO)

        assert len(done_tasks) == 1
        assert task1 in done_tasks
        assert len(in_progress_tasks) == 1
        assert task2 in in_progress_tasks
        assert len(todo_tasks) == 1
        assert task3 in todo_tasks

    def test_get_tasks_by_priority(self):
        """Test filtering tasks by priority."""
        task1 = self.manager.create_task(title="Low Task", priority=TaskPriority.LOW)
        task2 = self.manager.create_task(title="High Task", priority=TaskPriority.HIGH)
        task3 = self.manager.create_task(
            title="Urgent Task", priority=TaskPriority.URGENT
        )

        low_tasks = self.manager.get_tasks_by_priority(TaskPriority.LOW)
        high_tasks = self.manager.get_tasks_by_priority(TaskPriority.HIGH)
        urgent_tasks = self.manager.get_tasks_by_priority(TaskPriority.URGENT)

        assert len(low_tasks) == 1
        assert task1 in low_tasks
        assert len(high_tasks) == 1
        assert task2 in high_tasks
        assert len(urgent_tasks) == 1
        assert task3 in urgent_tasks

    def test_get_tasks_by_category(self):
        """Test filtering tasks by category."""
        task1 = self.manager.create_task(title="Work Task", category="work")
        task2 = self.manager.create_task(title="Personal Task", category="personal")
        task3 = self.manager.create_task(title="Another Work Task", category="work")

        work_tasks = self.manager.get_tasks_by_category("work")
        personal_tasks = self.manager.get_tasks_by_category("personal")

        assert len(work_tasks) == 2
        assert task1 in work_tasks
        assert task3 in work_tasks
        assert len(personal_tasks) == 1
        assert task2 in personal_tasks

    def test_search_tasks(self):
        """Test searching tasks."""
        task1 = self.manager.create_task(
            title="Python Project",
            description="Backend development",
            tags=["python", "backend"],
        )
        task2 = self.manager.create_task(
            title="Web Design",
            description="Frontend project",
            tags=["design", "frontend"],
        )
        task3 = self.manager.create_task(
            title="Python Tutorial",
            description="Learning Python",
            tags=["python", "learning"],
        )

        # Search by title
        python_tasks = self.manager.search_tasks("python")
        assert len(python_tasks) == 2
        assert task1 in python_tasks
        assert task3 in python_tasks

        # Search by description
        dev_tasks = self.manager.search_tasks("development")
        assert len(dev_tasks) == 1
        assert task1 in dev_tasks

        # Search by tags
        frontend_tasks = self.manager.search_tasks("frontend")
        assert len(frontend_tasks) == 1
        assert task2 in frontend_tasks

        # Search with no results
        database_tasks = self.manager.search_tasks("database")
        assert len(database_tasks) == 0

    def test_get_overdue_tasks(self):
        """Test getting overdue tasks."""
        # Task without due date
        task1 = self.manager.create_task(title="No Due Date Task")

        # Task with future due date
        future_date = datetime.now() + timedelta(days=7)
        task2 = self.manager.create_task(title="Future Task", due_date=future_date)

        # Task with past due date
        past_date = datetime.now() - timedelta(days=1)
        task3 = self.manager.create_task(title="Past Due Task", due_date=past_date)

        # Completed task with past due date
        task4 = self.manager.create_task(
            title="Completed Overdue Task", due_date=past_date
        )
        task4.mark_done()

        overdue_tasks = self.manager.get_overdue_tasks()
        assert len(overdue_tasks) == 1
        assert task3 in overdue_tasks
        assert task1 not in overdue_tasks  # No due date
        assert task2 not in overdue_tasks  # Future date
        assert task4 not in overdue_tasks  # Completed

    def test_get_due_soon_tasks(self):
        """Test getting tasks due soon."""
        # Create tasks with different due dates
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        next_month = today + timedelta(days=30)

        task1 = self.manager.create_task(title="Due Tomorrow", due_date=tomorrow)
        task2 = self.manager.create_task(title="Due Next Week", due_date=next_week)
        task3 = self.manager.create_task(title="Due Next Month", due_date=next_month)

        # Tasks due within 7 days
        due_soon = self.manager.get_due_soon_tasks(7)
        assert len(due_soon) == 2
        assert task1 in due_soon
        assert task2 in due_soon
        assert task3 not in due_soon

    def test_update_task(self):
        """Test updating a task."""
        task = self.manager.create_task(title="Original Title")

        success = self.manager.update_task(
            task.id,
            title="Updated Title",
            description="Updated Description",
            priority=TaskPriority.URGENT,
        )

        assert success is True

        updated_task = self.manager.get_task(task.id)
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated Description"
        assert updated_task.priority == TaskPriority.URGENT

        # Test updating non-existent task
        success = self.manager.update_task(99999, title="Won't Work")
        assert success is False

    def test_delete_task(self):
        """Test deleting a task."""
        task = self.manager.create_task(title="To Be Deleted")
        task_id = task.id

        success = self.manager.delete_task(task_id)
        assert success is True
        assert task_id not in self.manager.tasks

        # Test deleting non-existent task
        success = self.manager.delete_task(99999)
        assert success is False

    def test_mark_task_done(self):
        """Test marking task as done."""
        task = self.manager.create_task(title="To Be Done")

        success = self.manager.mark_task_done(task.id)
        assert success is True

        done_task = self.manager.get_task(task.id)
        assert done_task.status == TaskStatus.DONE
        assert done_task.completed_at is not None

        # Test marking non-existent task
        success = self.manager.mark_task_done(99999)
        assert success is False

    def test_mark_task_in_progress(self):
        """Test marking task as in progress."""
        task = self.manager.create_task(title="In Progress Task")

        success = self.manager.mark_task_in_progress(task.id)
        assert success is True

        progress_task = self.manager.get_task(task.id)
        assert progress_task.status == TaskStatus.IN_PROGRESS

        # Test marking non-existent task
        success = self.manager.mark_task_in_progress(99999)
        assert success is False

    def test_mark_task_cancelled(self):
        """Test marking task as cancelled."""
        task = self.manager.create_task(title="To Be Cancelled")

        success = self.manager.mark_task_cancelled(task.id)
        assert success is True

        cancelled_task = self.manager.get_task(task.id)
        assert cancelled_task.status == TaskStatus.CANCELLED

        # Test marking non-existent task
        success = self.manager.mark_task_cancelled(99999)
        assert success is False

    def test_get_statistics(self):
        """Test getting task statistics."""
        # Create tasks with different statuses
        task1 = self.manager.create_task(title="Task 1")
        task2 = self.manager.create_task(title="Task 2")
        task3 = self.manager.create_task(title="Task 3")
        task4 = self.manager.create_task(title="Task 4")

        # Mark tasks with different statuses
        task1.mark_done()
        task2.mark_in_progress()
        task3.mark_cancelled()
        # task4 remains TODO

        # Create overdue task
        past_date = datetime.now() - timedelta(days=1)
        overdue_task = self.manager.create_task(
            title="Overdue Task", due_date=past_date
        )

        stats = self.manager.get_statistics()

        assert stats["total"] == 5
        assert stats["completed"] == 1
        assert stats["in_progress"] == 1
        assert (
            stats["todo"] == 2
        )  # task4 and overdue_task are both in 'todo' state (overdue_task is not completed/cancelled)
        assert stats["cancelled"] == 1
        assert stats["overdue"] == 1
        assert stats["completion_rate"] == 20.0  # 1/5 * 100

    def test_get_statistics_empty(self):
        """Test getting statistics with no tasks."""
        stats = self.manager.get_statistics()

        assert stats["total"] == 0
        assert stats["completed"] == 0
        assert stats["in_progress"] == 0
        assert stats["todo"] == 0
        assert stats["cancelled"] == 0
        assert stats["overdue"] == 0
        assert stats["completion_rate"] == 0.0

    def test_get_categories(self):
        """Test getting all unique categories."""
        self.manager.create_task(title="Work Task 1", category="work")
        self.manager.create_task(title="Work Task 2", category="work")
        self.manager.create_task(title="Personal Task", category="personal")
        self.manager.create_task(title="Shopping Task", category="shopping")

        categories = self.manager.get_categories()
        assert len(categories) == 3
        assert "work" in categories
        assert "personal" in categories
        assert "shopping" in categories
        assert categories == sorted(categories)  # Should be sorted

    def test_persistence_save_load(self):
        """Test saving and loading tasks."""
        # Create some tasks
        task1 = self.manager.create_task(title="Task 1", category="test1")
        task2 = self.manager.create_task(title="Task 2", category="test2")

        # Create new manager with same file
        new_manager = TaskManager(self.temp_file.name)

        # Check that tasks were loaded
        loaded_tasks = new_manager.get_all_tasks()
        assert len(loaded_tasks) == 2

        loaded_ids = {task.id for task in loaded_tasks}
        assert task1.id in loaded_ids
        assert task2.id in loaded_ids

    def test_export_tasks_json(self):
        """Test exporting tasks to JSON format."""
        self.manager.create_task(title="Export Test Task")

        json_export = self.manager.export_tasks("json")

        # Verify it's valid JSON
        data = json.loads(json_export)
        assert "tasks" in data
        assert "exported_at" in data
        assert len(data["tasks"]) == 1

    def test_export_tasks_markdown(self):
        """Test exporting tasks to Markdown format."""
        self.manager.create_task(
            title="Markdown Test Task", description="Test description"
        )

        markdown_export = self.manager.export_tasks("markdown")

        assert "# Tasks" in markdown_export
        assert "Markdown Test Task" in markdown_export
        assert "Test description" in markdown_export

    def test_export_tasks_csv(self):
        """Test exporting tasks to CSV format."""
        self.manager.create_task(title="CSV Test Task", description="Test description")

        csv_export = self.manager.export_tasks("csv")

        assert "ID" in csv_export
        assert "Title" in csv_export
        assert "Description" in csv_export
        assert "CSV Test Task" in csv_export
