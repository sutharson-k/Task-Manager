"""
Task Manager class for Professional Task Manager.

This module provides the TaskManager class which handles task operations,
data persistence, and task management logic.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .task import Task, TaskPriority, TaskStatus


class TaskManager:
    """
    Main task management class.

    Handles task creation, storage, retrieval, and persistence.
    """

    def __init__(self, data_file: str = "tasks.json") -> None:
        """
        Initialize task manager.

        Args:
            data_file: Path to JSON data file for persistence
        """
        self.data_file = Path(data_file)
        self.tasks: Dict[int, Task] = {}
        self.load_tasks()

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        category: str = "general",
        due_date: Optional[datetime] = None,
        tags: Optional[list] = None,
    ) -> Task:
        """
        Create a new task.

        Args:
            title: Task title
            description: Task description
            priority: Task priority
            category: Task category
            due_date: Optional due date
            tags: List of tags

        Returns:
            Created task instance
        """
        task = Task(
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date,
            tags=tags,
        )

        self.tasks[task.id] = task
        self.save_tasks()
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Get task by ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            Task instance if found, None otherwise
        """
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks.

        Returns:
            List of all tasks
        """
        return list(self.tasks.values())

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        Get tasks by status.

        Args:
            status: Task status to filter by

        Returns:
            List of tasks with specified status
        """
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """
        Get tasks by priority.

        Args:
            priority: Task priority to filter by

        Returns:
            List of tasks with specified priority
        """
        return [task for task in self.tasks.values() if task.priority == priority]

    def get_tasks_by_category(self, category: str) -> List[Task]:
        """
        Get tasks by category.

        Args:
            category: Category to filter by

        Returns:
            List of tasks in specified category
        """
        return [task for task in self.tasks.values() if task.category == category]

    def search_tasks(self, query: str) -> List[Task]:
        """
        Search tasks by title or description.

        Args:
            query: Search query string

        Returns:
            List of tasks matching query
        """
        query_lower = query.lower()
        matching_tasks = []

        for task in self.tasks.values():
            if (
                query_lower in task.title.lower()
                or query_lower in task.description.lower()
                or any(query_lower in tag.lower() for tag in task.tags)
            ):
                matching_tasks.append(task)

        return matching_tasks

    def get_overdue_tasks(self) -> List[Task]:
        """
        Get all overdue tasks.

        Returns:
            List of overdue tasks
        """
        return [task for task in self.tasks.values() if task.is_overdue()]

    def get_due_soon_tasks(self, days: int = 7) -> List[Task]:
        """
        Get tasks due within specified days.

        Args:
            days: Number of days to look ahead

        Returns:
            List of tasks due soon
        """
        cutoff_date = datetime.now() + timedelta(days=days)
        return [
            task
            for task in self.tasks.values()
            if (
                task.due_date
                and task.due_date <= cutoff_date
                and task.status != TaskStatus.DONE
            )
        ]

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[TaskPriority] = None,
        category: Optional[str] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[list] = None,
    ) -> bool:
        """
        Update existing task.

        Args:
            task_id: ID of task to update
            title: New title
            description: New description
            priority: New priority
            category: New category
            due_date: New due date
            tags: New tags

        Returns:
            True if task was updated, False if not found
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.update(title, description, priority, category, due_date, tags)
        self.save_tasks()
        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Delete task.

        Args:
            task_id: ID of task to delete

        Returns:
            True if task was deleted, False if not found
        """
        if task_id not in self.tasks:
            return False

        del self.tasks[task_id]
        self.save_tasks()
        return True

    def mark_task_done(self, task_id: int) -> bool:
        """
        Mark task as done.

        Args:
            task_id: ID of task to mark done

        Returns:
            True if task was marked done, False if not found
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.mark_done()
        self.save_tasks()
        return True

    def mark_task_in_progress(self, task_id: int) -> bool:
        """
        Mark task as in progress.

        Args:
            task_id: ID of task to mark in progress

        Returns:
            True if task was marked in progress, False if not found
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.mark_in_progress()
        self.save_tasks()
        return True

    def mark_task_cancelled(self, task_id: int) -> bool:
        """
        Mark task as cancelled.

        Args:
            task_id: ID of task to mark cancelled

        Returns:
            True if task was marked cancelled, False if not found
        """
        task = self.get_task(task_id)
        if not task:
            return False

        task.mark_cancelled()
        self.save_tasks()
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get task statistics.

        Returns:
            Dictionary with task statistics
        """
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            return {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "todo": 0,
                "cancelled": 0,
                "overdue": 0,
                "completion_rate": 0.0,
            }

        completed = len(self.get_tasks_by_status(TaskStatus.DONE))
        in_progress = len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS))
        todo = len(self.get_tasks_by_status(TaskStatus.TODO))
        cancelled = len(self.get_tasks_by_status(TaskStatus.CANCELLED))
        overdue = len(self.get_overdue_tasks())

        completion_rate = (completed / total_tasks) * 100 if total_tasks > 0 else 0

        return {
            "total": total_tasks,
            "completed": completed,
            "in_progress": in_progress,
            "todo": todo,
            "cancelled": cancelled,
            "overdue": overdue,
            "completion_rate": round(completion_rate, 1),
        }

    def get_categories(self) -> List[str]:
        """
        Get all unique task categories.

        Returns:
            List of unique categories
        """
        categories = set(task.category for task in self.tasks.values())
        return sorted(list(categories))

    def save_tasks(self) -> None:
        """Save tasks to JSON file."""
        try:
            tasks_data = {
                "tasks": [task.to_dict() for task in self.tasks.values()],
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
            }

            # Ensure directory exists
            self.data_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise RuntimeError(f"Failed to save tasks: {e}")

    def load_tasks(self) -> None:
        """Load tasks from JSON file."""
        if not self.data_file.exists():
            # Create empty data file if it doesn't exist
            self.save_tasks()
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            tasks_data = data.get("tasks", [])
            for task_data in tasks_data:
                task = Task.from_dict(task_data)
                self.tasks[task.id] = task

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If file is corrupted, start fresh
            self.tasks = {}
            self.save_tasks()
        except Exception as e:
            raise RuntimeError(f"Failed to load tasks: {e}")

    def export_tasks(self, format: str = "json") -> str:
        """
        Export tasks in specified format.

        Args:
            format: Export format ('json', 'csv', 'markdown')

        Returns:
            Exported data as string
        """
        if format.lower() == "json":
            return json.dumps(
                {
                    "tasks": [task.to_dict() for task in self.tasks.values()],
                    "exported_at": datetime.now().isoformat(),
                },
                indent=2,
            )

        elif format.lower() == "csv":
            import csv
            from io import StringIO

            output = StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(
                [
                    "ID",
                    "Title",
                    "Description",
                    "Status",
                    "Priority",
                    "Category",
                    "Due Date",
                    "Created At",
                    "Completed At",
                    "Tags",
                ]
            )

            # Write tasks
            for task in self.tasks.values():
                writer.writerow(
                    [
                        task.id,
                        task.title,
                        task.description,
                        task.status.value,
                        task.priority.value,
                        task.category,
                        task.due_date.isoformat() if task.due_date else "",
                        task.created_at.isoformat(),
                        task.completed_at.isoformat() if task.completed_at else "",
                        ", ".join(task.tags),
                    ]
                )

            return output.getvalue()

        elif format.lower() == "markdown":
            lines = ["# Tasks\n"]
            for task in self.tasks.values():
                status_icon = {
                    TaskStatus.TODO: "⏳",
                    TaskStatus.IN_PROGRESS: "🔄",
                    TaskStatus.DONE: "✅",
                    TaskStatus.CANCELLED: "❌",
                }

                lines.append(f"## {status_icon[task.status]} {task.title}")
                lines.append(f"**ID:** {task.id}")
                lines.append(f"**Status:** {task.status.value}")
                lines.append(f"**Priority:** {task.priority.value}")
                lines.append(f"**Category:** {task.category}")

                if task.due_date:
                    lines.append(f"**Due Date:** {task.due_date.strftime('%Y-%m-%d')}")

                if task.description:
                    lines.append(f"**Description:** {task.description}")

                if task.tags:
                    lines.append(f"**Tags:** {', '.join(task.tags)}")

                lines.append("")

            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported export format: {format}")
