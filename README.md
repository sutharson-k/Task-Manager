# Professional Task Manager 📋

[![CI/CD Pipeline](https://github.com/sutharson20069/professional-task-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/sutharson20069/professional-task-manager/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/sutharson20069/professional-task-manager/branch/main/graph/badge.svg)](https://codecov.io/gh/sutharson20069/professional-task-manager)
[![PyPI version](https://badge.fury.io/py/professional-task-manager.svg)](https://badge.fury.io/py/professional-task-manager)
[![Python versions](https://img.shields.io/pypi/pyversions/professional-task-manager.svg)](https://pypi.org/project/professional-task-manager/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful command-line task management application with rich interface, advanced features, and professional Python development practices. Built for productivity enthusiasts who want complete control over their tasks.

## ✨ Features

- 🎯 **Rich CLI Interface**: Beautiful, colorful output with tables and panels
- 📊 **Advanced Filtering**: Filter by status, priority, category, due dates
- 🔍 **Smart Search**: Search across titles, descriptions, and tags
- 📅 **Due Date Management**: Track overdue tasks and upcoming deadlines
- 🏷️ **Tagging System**: Organize tasks with custom tags
- 📈 **Statistics Dashboard**: Visual insights into task completion
- 💾 **Data Persistence**: JSON-based storage with backup support
- 📤 **Export Options**: JSON, CSV, and Markdown export formats
- 🎨 **Priority Levels**: Low, Medium, High, Urgent priority system
- 📱 **Status Tracking**: Todo, In Progress, Done, Cancelled states

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install professional-task-manager

# Or install from source
git clone https://github.com/sutharson20069/professional-task-manager.git
cd professional-task-manager
pip install -e .
```

### Basic Usage

```bash
# Show main dashboard
task-manager

# Add a new task
task-manager add "Complete project proposal" -d "Prepare and submit Q1 proposal" -p high -c work --due 2024-02-15 -t ["urgent", "proposal"]

# List all tasks
task-manager list

# Filter tasks by status
task-manager list --status todo
task-manager list --status in_progress

# Filter by priority
task-manager list --priority urgent

# Show overdue tasks
task-manager list --overdue

# Show tasks due soon
task-manager list --due-soon 7

# Search tasks
task-manager search "project"

# Show task details
task-manager show 12345

# Update task
task-manager update 12345 --title "Updated title" --priority urgent

# Mark task status
task-manager done 12345
task-manager progress 12345
task-manager cancel 12345

# Delete task
task-manager delete 12345

# Show statistics
task-manager stats

# Export tasks
task-manager export --format json --output tasks.json
task-manager export --format csv --output tasks.csv
task-manager export --format markdown --output tasks.md
```

## 📖 Command Reference

### Task Management

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Add a new task | `task-manager add "New task" -p high -c work` |
| `list` | List tasks with filters | `task-manager list --status todo --priority high` |
| `show` | Show task details | `task-manager show 12345` |
| `update` | Update existing task | `task-manager update 12345 --title "New title"` |
| `delete` | Delete a task | `task-manager delete 12345` |

### Status Commands

| Command | Description | Example |
|---------|-------------|---------|
| `done` | Mark task as completed | `task-manager done 12345` |
| `progress` | Mark task as in progress | `task-manager progress 12345` |
| `cancel` | Cancel a task | `task-manager cancel 12345` |

### Utility Commands

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Search tasks | `task-manager search "urgent"` |
| `stats` | Show statistics | `task-manager stats` |
| `export` | Export tasks | `task-manager export --format json` |

## 🔧 Advanced Features

### Priority Levels

- 🔴 **Urgent**: Critical tasks requiring immediate attention
- 🟠 **High**: Important tasks with high priority
- 🟡 **Medium**: Standard priority tasks (default)
- 🟢 **Low**: Low priority tasks

### Task Status

- ⏳ **Todo**: Tasks not yet started
- 🔄 **In Progress**: Tasks currently being worked on
- ✅ **Done**: Completed tasks
- ❌ **Cancelled**: Cancelled or abandoned tasks

### Smart Filtering

```bash
# Multiple filters
task-manager list --status todo --priority high --c work

# Due soon tasks (within 7 days)
task-manager list --due-soon 7

# Overdue tasks only
task-manager list --overdue
```

### Search Capabilities

Search across multiple fields:
- **Titles**: Find tasks by title
- **Descriptions**: Search within task descriptions  
- **Tags**: Find tasks by tags

```bash
# Find all tasks related to "project"
task-manager search "project"

# Tasks with specific tags
task-manager search "urgent"
```

### Export Formats

#### JSON Export
```json
{
  "tasks": [...],
  "exported_at": "2024-01-26T20:30:00"
}
```

#### CSV Export
```csv
ID,Title,Description,Status,Priority,Category,Due Date,Created At,Completed At,Tags
12345,Task Title,Description,todo,high,work,2024-02-15,2024-01-26,,"urgent,project"
```

#### Markdown Export
```markdown
# Tasks

## ✅ Task Title
**ID:** 12345
**Status:** done
**Priority:** high
**Category:** work
**Due Date:** 2024-02-15
**Description:** Task description
**Tags:** urgent, project
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/sutharson20069/professional-task-manager.git
cd professional-task-manager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=task_manager --cov-report=html

# Run specific test file
pytest tests/test_task_manager.py
```

### Code Quality

The project uses professional development tools:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing framework

## 📊 Data Storage

Tasks are stored in `tasks.json` in the current directory by default. The file contains:

```json
{
  "tasks": [
    {
      "id": 1234567890,
      "title": "Example task",
      "description": "Task description",
      "status": "todo",
      "priority": 2,
      "category": "work",
      "due_date": "2024-02-15T10:00:00",
      "created_at": "2024-01-26T20:30:00",
      "updated_at": "2024-01-26T20:30:00",
      "completed_at": null,
      "tags": ["example", "task"]
    }
  ],
  "version": "1.0",
  "last_updated": "2024-01-26T20:30:00"
}
```

## 📈 Statistics

The `task-manager stats` command provides insights:

- Total tasks count
- Tasks by status
- Overdue tasks count
- Completion rate percentage
- Task categories

Example output:
```
┌─────────────────────────────────────┐
│        Task Statistics        │
├─────────────────────────────────────┤
│ Total Tasks: 25                │
│ ✅ Completed: 15                │
│ 🔄 In Progress: 3               │
│ ⏳ Todo: 5                      │
│ ❌ Cancelled: 2                  │
│ ⚠️  Overdue: 1                   │
│ 📊 Completion Rate: 60.0%        │
└─────────────────────────────────────┘

Categories: general, work, personal, shopping
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings for public methods
- Maintain 95%+ test coverage
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Rich** library for beautiful CLI output
- **Click** inspiration for CLI design patterns
- **Python** datetime and JSON modules
- Open source community for best practices

## 📞 Support

- 📧 Email: sutharson20069@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/sutharson20069/professional-task-manager/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/sutharson20069/professional-task-manager/discussions)

## 🌟 Show Your Support

If you find this project useful:

- ⭐ Star the repository
- 🍴 Fork and contribute
- 📢 Share with others
- 💝 Report bugs and suggest features

---

**Made with ❤️ by [sutharson20069](https://github.com/sutharson20069)**

Boost your productivity with Professional Task Manager! 🚀