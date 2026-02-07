"""
Command-line interface for Professional Task Manager.

This module provides CLI commands for task management with rich
output formatting and interactive features.
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional, Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from .task import TaskPriority, TaskStatus
from .task_manager import TaskManager

if TYPE_CHECKING:
    from .task import Task

# Type alias for argparse namespace
ArgsNamespace = argparse.Namespace


class TaskCLI:
    """Command-line interface for task management."""

    def __init__(self) -> None:
        """Initialize CLI with rich console."""
        self.console = Console()
        self.manager = TaskManager()

    def run(self, args: Optional[list] = None) -> None:
        """
        Run the CLI application.

        Args:
            args: Optional command-line arguments
        """
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        try:
            # Handle commands
            if hasattr(parsed_args, "func"):
                parsed_args.func(parsed_args)
            else:
                self.show_dashboard()

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operation cancelled by user.[/yellow]")
            sys.exit(0)
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)

    def create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser."""
        parser = argparse.ArgumentParser(
            description="Professional Task Manager - CLI task management application",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  task-manager                          # Show dashboard
  task-manager add "New task"            # Add new task
  task-manager list --status todo           # List todo tasks
  task-manager done 123                   # Mark task as done
  task-manager search "urgent"            # Search tasks
            """,
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Add command
        add_parser = subparsers.add_parser("add", help="Add a new task")
        add_parser.add_argument("title", help="Task title")
        add_parser.add_argument(
            "-d", "--description", default="", help="Task description"
        )
        add_parser.add_argument(
            "-p",
            "--priority",
            choices=["low", "medium", "high", "urgent"],
            default="medium",
            help="Task priority",
        )
        add_parser.add_argument(
            "-c", "--category", default="general", help="Task category"
        )
        add_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
        add_parser.add_argument("-t", "--tags", nargs="*", help="Task tags")
        add_parser.set_defaults(func=self.add_task)

        # List command
        list_parser = subparsers.add_parser("list", help="List tasks")
        list_parser.add_argument(
            "-s",
            "--status",
            choices=["todo", "in_progress", "done", "cancelled"],
            help="Filter by status",
        )
        list_parser.add_argument(
            "-p",
            "--priority",
            choices=["low", "medium", "high", "urgent"],
            help="Filter by priority",
        )
        list_parser.add_argument("-c", "--category", help="Filter by category")
        list_parser.add_argument(
            "--overdue", action="store_true", help="Show only overdue tasks"
        )
        list_parser.add_argument(
            "--due-soon", type=int, metavar="DAYS", help="Show tasks due within N days"
        )
        list_parser.set_defaults(func=self.list_tasks)

        # Show command
        show_parser = subparsers.add_parser("show", help="Show task details")
        show_parser.add_argument("task_id", type=int, help="Task ID")
        show_parser.set_defaults(func=self.show_task)

        # Update command
        update_parser = subparsers.add_parser("update", help="Update a task")
        update_parser.add_argument("task_id", type=int, help="Task ID")
        update_parser.add_argument("-t", "--title", help="New title")
        update_parser.add_argument("-d", "--description", help="New description")
        update_parser.add_argument(
            "-p",
            "--priority",
            choices=["low", "medium", "high", "urgent"],
            help="New priority",
        )
        update_parser.add_argument("-c", "--category", help="New category")
        update_parser.add_argument("--due", help="New due date (YYYY-MM-DD)")
        update_parser.add_argument("--tags", nargs="*", help="New tags")
        update_parser.set_defaults(func=self.update_task)

        # Status commands
        done_parser = subparsers.add_parser("done", help="Mark task as done")
        done_parser.add_argument("task_id", type=int, help="Task ID")
        done_parser.set_defaults(func=self.mark_done)

        progress_parser = subparsers.add_parser(
            "progress", help="Mark task as in progress"
        )
        progress_parser.add_argument("task_id", type=int, help="Task ID")
        progress_parser.set_defaults(func=self.mark_in_progress)

        cancel_parser = subparsers.add_parser("cancel", help="Cancel a task")
        cancel_parser.add_argument("task_id", type=int, help="Task ID")
        cancel_parser.set_defaults(func=self.mark_cancelled)

        # Delete command
        delete_parser = subparsers.add_parser("delete", help="Delete a task")
        delete_parser.add_argument("task_id", type=int, help="Task ID")
        delete_parser.set_defaults(func=self.delete_task)

        # Search command
        search_parser = subparsers.add_parser("search", help="Search tasks")
        search_parser.add_argument("query", help="Search query")
        search_parser.set_defaults(func=self.search_tasks)

        # Statistics command
        stats_parser = subparsers.add_parser("stats", help="Show statistics")
        stats_parser.set_defaults(func=self.show_statistics)

        # Export command
        export_parser = subparsers.add_parser("export", help="Export tasks")
        export_parser.add_argument(
            "-f",
            "--format",
            choices=["json", "csv", "markdown"],
            default="json",
            help="Export format",
        )
        export_parser.add_argument(
            "-o", "--output", help="Output file (default: stdout)"
        )
        export_parser.set_defaults(func=self.export_tasks)

        return parser

    def add_task(self, args: ArgsNamespace) -> None:
        """Add a new task."""
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.URGENT,
        }

        due_date = None
        if args.due:
            try:
                due_date = datetime.strptime(args.due, "%Y-%m-%d")
            except ValueError:
                self.console.print("[red]Invalid date format. Use YYYY-MM-DD[/red]")
                return

        task = self.manager.create_task(
            title=args.title,
            description=args.description,
            priority=priority_map[args.priority],
            category=args.category,
            due_date=due_date,
            tags=args.tags or [],
        )

        self.console.print(f"[green]✅ Task created with ID: {task.id}[/green]")
        self.show_task_simple(task)

    def list_tasks(self, args: ArgsNamespace) -> None:
        """List tasks with optional filtering."""
        tasks = self.manager.get_all_tasks()

        # Apply filters
        if args.status:
            status_map = {
                "todo": TaskStatus.TODO,
                "in_progress": TaskStatus.IN_PROGRESS,
                "done": TaskStatus.DONE,
                "cancelled": TaskStatus.CANCELLED,
            }
            tasks = [t for t in tasks if t.status == status_map[args.status]]

        if args.priority:
            priority_map = {
                "low": TaskPriority.LOW,
                "medium": TaskPriority.MEDIUM,
                "high": TaskPriority.HIGH,
                "urgent": TaskPriority.URGENT,
            }
            tasks = [t for t in tasks if t.priority == priority_map[args.priority]]

        if args.category:
            tasks = [t for t in tasks if t.category == args.category]

        if args.overdue:
            tasks = self.manager.get_overdue_tasks()

        if args.due_soon:
            tasks = self.manager.get_due_soon_tasks(args.due_soon)

        if not tasks:
            self.console.print("[yellow]No tasks found.[/yellow]")
            return

        self.show_tasks_table(tasks)

    def show_task(self, args: ArgsNamespace) -> None:
        """Show detailed task information."""
        task = self.manager.get_task(args.task_id)
        if not task:
            self.console.print(f"[red]Task with ID {args.task_id} not found.[/red]")
            return

        self.show_task_details(task)

    def update_task(self, args: ArgsNamespace) -> None:
        """Update an existing task."""
        # Parse priority if provided
        priority = None
        if args.priority:
            priority_map = {
                "low": TaskPriority.LOW,
                "medium": TaskPriority.MEDIUM,
                "high": TaskPriority.HIGH,
                "urgent": TaskPriority.URGENT,
            }
            priority = priority_map[args.priority]

        # Parse due date if provided
        due_date = None
        if args.due:
            try:
                due_date = datetime.strptime(args.due, "%Y-%m-%d")
            except ValueError:
                self.console.print("[red]Invalid date format. Use YYYY-MM-DD[/red]")
                return

        success = self.manager.update_task(
            task_id=args.task_id,
            title=args.title,
            description=args.description,
            priority=priority,
            category=args.category,
            due_date=due_date,
            tags=args.tags,
        )

        if success:
            self.console.print(
                f"[green]✅ Task {args.task_id} updated successfully[/green]"
            )
        else:
            self.console.print(f"[red]Task with ID {args.task_id} not found.[/red]")

    def mark_done(self, args: ArgsNamespace) -> None:
        """Mark task as done."""
        if self.manager.mark_task_done(args.task_id):
            self.console.print(f"[green]✅ Task {args.task_id} marked as done[/green]")
        else:
            self.console.print(f"[red]Task with ID {args.task_id} not found.[/red]")

    def mark_in_progress(self, args: ArgsNamespace) -> None:
        """Mark task as in progress."""
        if self.manager.mark_task_in_progress(args.task_id):
            self.console.print(
                f"[yellow]🔄 Task {args.task_id} marked as in progress[/yellow]"
            )
        else:
            self.console.print(f"[red]Task with ID {args.task_id} not found.[/red]")

    def mark_cancelled(self, args: ArgsNamespace) -> None:
        """Mark task as cancelled."""
        if self.manager.mark_task_cancelled(args.task_id):
            self.console.print(f"[red]❌ Task {args.task_id} cancelled[/red]")
        else:
            self.console.print(f"[red]Task with ID {args.task_id} not found.[/red]")

    def delete_task(self, args: ArgsNamespace) -> None:
        """Delete a task."""
        task = self.manager.get_task(args.task_id)
        if not task:
            self.console.print(f"[red]Task with ID {args.task_id} not found.[/red]")
            return

        if Confirm.ask(f"Are you sure you want to delete task '{task.title}'?"):
            if self.manager.delete_task(args.task_id):
                self.console.print(f"[red]🗑️  Task {args.task_id} deleted[/red]")
            else:
                self.console.print(f"[red]Failed to delete task {args.task_id}[/red]")
        else:
            self.console.print("[yellow]Operation cancelled.[/yellow]")

    def search_tasks(self, args: ArgsNamespace) -> None:
        """Search for tasks."""
        tasks = self.manager.search_tasks(args.query)
        if not tasks:
            self.console.print(
                f"[yellow]No tasks found matching '{args.query}'[/yellow]"
            )
            return

        self.console.print(
            f"[cyan]Found {len(tasks)} tasks matching '{args.query}':[/cyan]"
        )
        self.show_tasks_table(tasks)

    def show_statistics(self, args: Optional[ArgsNamespace]) -> None:
        """Show task statistics."""
        stats = self.manager.get_statistics()

        # Create statistics panel
        stats_text = f"""
Total Tasks: {stats['total']}
✅ Completed: {stats['completed']}
🔄 In Progress: {stats['in_progress']}
⏳ Todo: {stats['todo']}
❌ Cancelled: {stats['cancelled']}
⚠️  Overdue: {stats['overdue']}
📊 Completion Rate: {stats['completion_rate']}%
        """.strip()

        panel = Panel(
            stats_text,
            title="[bold blue]Task Statistics[/bold blue]",
            border_style="blue",
        )
        self.console.print(panel)

        # Show categories
        categories = self.manager.get_categories()
        if categories:
            self.console.print(f"\n[bold]Categories:[/bold] {', '.join(categories)}")

    def export_tasks(self, args: ArgsNamespace) -> None:
        """Export tasks in specified format."""
        try:
            exported_data = self.manager.export_tasks(args.format)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(exported_data)
                self.console.print(f"[green]✅ Tasks exported to {args.output}[/green]")
            else:
                self.console.print(exported_data)

        except Exception as e:
            self.console.print(f"[red]Export failed: {e}[/red]")

    def show_dashboard(self) -> None:
        """Show main dashboard."""
        # Show statistics
        self.show_statistics(None)

        # Show recent tasks
        recent_tasks = sorted(
            self.manager.get_all_tasks(), key=lambda t: t.created_at, reverse=True
        )[:5]

        if recent_tasks:
            self.console.print("\n[bold]📋 Recent Tasks:[/bold]")
            self.show_tasks_table(recent_tasks, show_details=False)

        # Show overdue tasks
        overdue = self.manager.get_overdue_tasks()
        if overdue:
            self.console.print("\n[bold red]⚠️  Overdue Tasks:[/bold red]")
            self.show_tasks_table(overdue, show_details=False)

    def show_tasks_table(self, tasks: List["Task"], show_details: bool = True) -> None:
        """Display tasks in a formatted table."""
        table = Table(show_header=True, header_style="bold magenta")

        table.add_column("ID", style="cyan", width=6)
        table.add_column("Status", style="green", width=12)
        table.add_column("Priority", style="yellow", width=10)
        table.add_column("Title", style="white", width=30)
        table.add_column("Category", style="blue", width=12)
        table.add_column("Due", style="red", width=12)

        if show_details:
            table.add_column("Tags", style="magenta", width=20)

        for task in tasks:
            status_text = {
                TaskStatus.TODO: "⏳ Todo",
                TaskStatus.IN_PROGRESS: "🔄 In Progress",
                TaskStatus.DONE: "✅ Done",
                TaskStatus.CANCELLED: "❌ Cancelled",
            }

            priority_text = {
                TaskPriority.LOW: "🟢 Low",
                TaskPriority.MEDIUM: "🟡 Medium",
                TaskPriority.HIGH: "🟠 High",
                TaskPriority.URGENT: "🔴 Urgent",
            }

            due_text = ""
            if task.due_date:
                if task.is_overdue():
                    due_text = f"[red]Overdue![/red]"
                else:
                    days = task.days_until_due()
                    due_text = f"{days}d" if days is not None else ""

            tags_text = ", ".join(task.tags[:3]) if task.tags else ""
            if len(task.tags) > 3:
                tags_text += "..."

            row = [
                str(task.id),
                status_text[task.status],
                priority_text[task.priority],
                task.title[:27] + "..." if len(task.title) > 30 else task.title,
                task.category,
                due_text,
            ]

            if show_details:
                row.append(tags_text)

            table.add_row(*row)

        self.console.print(table)

    def show_task_details(self, task: "Task") -> None:
        """Show detailed task information."""
        status_text = {
            TaskStatus.TODO: "⏳ Todo",
            TaskStatus.IN_PROGRESS: "🔄 In Progress",
            TaskStatus.DONE: "✅ Done",
            TaskStatus.CANCELLED: "❌ Cancelled",
        }

        priority_text = {
            TaskPriority.LOW: "🟢 Low",
            TaskPriority.MEDIUM: "🟡 Medium",
            TaskPriority.HIGH: "🟠 High",
            TaskPriority.URGENT: "🔴 Urgent",
        }

        details = f"""
[bold]ID:[/bold] {task.id}
[bold]Title:[/bold] {task.title}
[bold]Status:[/bold] {status_text[task.status]}
[bold]Priority:[/bold] {priority_text[task.priority]}
[bold]Category:[/bold] {task.category}
[bold]Description:[/bold] {task.description if task.description else 'No description'}
[bold]Tags:[/bold] {', '.join(task.tags) if task.tags else 'No tags'}
[bold]Created:[/bold] {task.created_at.strftime('%Y-%m-%d %H:%M')}
[bold]Updated:[/bold] {task.updated_at.strftime('%Y-%m-%d %H:%M')}
        """.strip()

        if task.due_date:
            details += f"\n[bold]Due:[/bold] {task.due_date.strftime('%Y-%m-%d %H:%M')}"
            if task.is_overdue():
                details += " [red](OVERDUE!)[/red]"

        if task.completed_at:
            details += f"\n[bold]Completed:[/bold] {task.completed_at.strftime('%Y-%m-%d %H:%M')}"

        panel = Panel(
            details, title=f"[bold blue]Task Details[/bold blue]", border_style="blue"
        )
        self.console.print(panel)

    def show_task_simple(self, task: "Task") -> None:
        """Show task in simple format."""
        self.console.print(f"  [cyan]{task.id}[/cyan]: {task}")


def main() -> None:
    """Main entry point for the CLI application."""
    cli = TaskCLI()
    cli.run()


if __name__ == "__main__":
    main()
