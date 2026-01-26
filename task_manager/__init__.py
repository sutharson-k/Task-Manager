"""
Professional Task Manager - CLI task management application.

A powerful command-line task manager with priorities, due dates, categories, and progress tracking.
"""

__version__ = "1.0.0"
__author__ = "sutharson20069"
__email__ = "sutharson20069@example.com"

from .task import Task, TaskStatus, TaskPriority
from .task_manager import TaskManager
from .cli import main

__all__ = ["Task", "TaskStatus", "TaskPriority", "TaskManager", "main"]