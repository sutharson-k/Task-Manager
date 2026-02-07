"""
Test suite for the CLI module.
"""

import json
import tempfile
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from task_manager.cli import TaskCLI
from task_manager.task import TaskPriority, TaskStatus
from task_manager.task_manager import TaskManager


class TestTaskCLI:
    """Test cases for the TaskCLI class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Use temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()

        # Create CLI instance with test file
        with patch("task_manager.cli.TaskManager") as mock_manager:
            mock_manager.return_value = TaskManager(self.temp_file.name)
            self.cli = TaskCLI()
            self.manager = self.cli.manager

    def teardown_method(self):
        """Clean up test fixtures."""
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_cli_initialization(self):
        """Test CLI initialization."""
        assert hasattr(self.cli, "console")
        assert hasattr(self.cli, "manager")
        assert isinstance(self.cli.console, Console)

    @patch("sys.stdout", new_callable=StringIO)
    def test_show_dashboard(self, mock_stdout):
        """Test showing dashboard."""
        # Create some test tasks
        self.manager.create_task("Test Task 1")
        self.manager.create_task("Test Task 2")

        self.cli.show_dashboard()

        output = mock_stdout.getvalue()
        assert "Task Statistics" in output
        assert "Total Tasks" in output
        assert "Recent Tasks" in output

    @patch("builtins.input", return_value="y")
    @patch("sys.stdout", new_callable=StringIO)
    def test_delete_task_confirmation(self, mock_stdout, mock_input):
        """Test task deletion with confirmation."""
        # Create a task
        task = self.manager.create_task("To Be Deleted")

        # Mock Confirm.ask to return True
        with patch("task_manager.cli.Confirm.ask", return_value=True):
            self.cli.delete_task(type("Args", (), {"task_id": task.id})())

        # Check task was deleted
        assert self.manager.get_task(task.id) is None

    def test_add_task(self):
        """Test adding a new task."""
        args = type(
            "Args",
            (),
            {
                "title": "New Test Task",
                "description": "Test description",
                "priority": "high",
                "category": "test",
                "due": None,
                "tags": ["test", "cli"],
            },
        )()

        self.cli.add_task(args)

        tasks = self.manager.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "New Test Task"
        assert tasks[0].description == "Test description"
        assert tasks[0].priority == TaskPriority.HIGH
        assert tasks[0].category == "test"
        assert tasks[0].tags == ["test", "cli"]

    def test_add_task_with_due_date(self):
        """Test adding a task with due date."""
        due_date_str = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        args = type(
            "Args",
            (),
            {
                "title": "Task with Due Date",
                "description": "",
                "priority": "medium",
                "category": "general",
                "due": due_date_str,
                "tags": [],
            },
        )()

        self.cli.add_task(args)

        tasks = self.manager.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].due_date is not None
        # Allow for potential day boundary issues (e.g., due to timezone differences)
        days_until = tasks[0].days_until_due()
        assert days_until in [6, 7]  # Could be 6 or 7 depending on exact timing

    def test_list_tasks_all(self):
        """Test listing all tasks."""
        # Create test tasks
        self.manager.create_task("Task 1", priority=TaskPriority.HIGH)
        self.manager.create_task("Task 2", priority=TaskPriority.LOW)

        args = type(
            "Args",
            (),
            {
                "status": None,
                "priority": None,
                "category": None,
                "overdue": False,
                "due_soon": None,
            },
        )()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.cli.list_tasks(args)
            output = mock_stdout.getvalue()
            assert "Task 1" in output
            assert "Task 2" in output

    def test_list_tasks_by_status(self):
        """Test listing tasks filtered by status."""
        # Create test tasks
        task1 = self.manager.create_task("Todo Task")
        task2 = self.manager.create_task("Done Task")
        task2.mark_done()

        args = type(
            "Args",
            (),
            {
                "status": "done",
                "priority": None,
                "category": None,
                "overdue": False,
                "due_soon": None,
            },
        )()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.cli.list_tasks(args)
            output = mock_stdout.getvalue()
            assert "Done Task" in output
            assert "Todo Task" not in output

    def test_list_tasks_by_priority(self):
        """Test listing tasks filtered by priority."""
        # Create test tasks
        self.manager.create_task("Low Priority Task", priority=TaskPriority.LOW)
        self.manager.create_task("High Priority Task", priority=TaskPriority.HIGH)

        args = type(
            "Args",
            (),
            {
                "status": None,
                "priority": "high",
                "category": None,
                "overdue": False,
                "due_soon": None,
            },
        )()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.cli.list_tasks(args)
            output = mock_stdout.getvalue()
            assert "High Priority Task" in output
            assert "Low Priority Task" not in output

    def test_show_task(self):
        """Test showing task details."""
        task = self.manager.create_task(
            "Detailed Task", description="Detailed description"
        )

        args = type("Args", (), {"task_id": task.id})()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.cli.show_task(args)
            output = mock_stdout.getvalue()
            assert "Detailed Task" in output
            assert "Detailed description" in output
            assert str(task.id) in output

    def test_show_task_not_found(self):
        """Test showing non-existent task."""
        args = type("Args", (), {"task_id": 99999})()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.cli.show_task(args)
            output = mock_stdout.getvalue()
            assert "not found" in output

    def test_update_task(self):
        """Test updating a task."""
        task = self.manager.create_task("Original Task")

        args = type(
            "Args",
            (),
            {
                "task_id": task.id,
                "title": "Updated Task",
                "description": "Updated description",
                "priority": "urgent",
                "category": "updated",
                "due": None,
                "tags": ["updated"],
            },
        )()

        self.cli.update_task(args)

        updated_task = self.manager.get_task(task.id)
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Updated description"
        assert updated_task.priority == TaskPriority.URGENT
        assert updated_task.category == "updated"
        assert updated_task.tags == ["updated"]

    def test_mark_done(self):
        """Test marking task as done."""
        task = self.manager.create_task("To Be Done")

        args = type("Args", (), {"task_id": task.id})()

        self.cli.mark_done(args)

        done_task = self.manager.get_task(task.id)
        assert done_task.status == TaskStatus.DONE

    def test_mark_in_progress(self):
        """Test marking task as in progress."""
        task = self.manager.create_task("In Progress Task")

        args = type("Args", (), {"task_id": task.id})()

        self.cli.mark_in_progress(args)

        progress_task = self.manager.get_task(task.id)
        assert progress_task.status == TaskStatus.IN_PROGRESS

    def test_mark_cancelled(self):
        """Test marking task as cancelled."""
        task = self.manager.create_task("To Be Cancelled")

        args = type("Args", (), {"task_id": task.id})()

        self.cli.mark_cancelled(args)

        cancelled_task = self.manager.get_task(task.id)
        assert cancelled_task.status == TaskStatus.CANCELLED

    def test_search_tasks(self):
        """Test searching tasks."""
        self.manager.create_task("Python Project", description="Backend development")
        self.manager.create_task("Web Design", description="Frontend design")

        args = type("Args", (), {"query": "python"})()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.cli.search_tasks(args)
            output = mock_stdout.getvalue()
            assert "Found" in output
            assert "python" in output
            assert "Python Project" in output
            assert "Web Design" not in output

    def test_export_tasks_json(self):
        """Test exporting tasks to JSON."""
        self.manager.create_task("Export Test Task")

        args = type("Args", (), {"format": "json", "output": None})()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.cli.export_tasks(args)
            output = mock_stdout.getvalue()

            # Verify it's valid JSON
            data = json.loads(output)
            assert "tasks" in data
            assert len(data["tasks"]) == 1

    def test_export_tasks_csv(self):
        """Test exporting tasks to CSV."""
        self.manager.create_task("CSV Export Task")

        args = type("Args", (), {"format": "csv", "output": None})()

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.cli.export_tasks(args)
            output = mock_stdout.getvalue()
            assert "ID" in output
            assert "Title" in output
            assert "CSV Export Task" in output
