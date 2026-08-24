#!/usr/bin/env python3
"""
Task Tracker Script
A simple command-line task management system with persistent storage.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class TaskTracker:
    """A simple task tracker with JSON-based storage."""
    
    def __init__(self, storage_file: str = "tasks.json"):
        """Initialize the task tracker with a storage file."""
        self.storage_file = Path(storage_file)
        self.tasks: List[Dict] = self._load_tasks()
    
    def _load_tasks(self) -> List[Dict]:
        """Load tasks from the storage file."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def _save_tasks(self) -> None:
        """Save tasks to the storage file."""
        with open(self.storage_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, title: str, description: str = "", priority: str = "medium") -> Dict:
        """Add a new task."""
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "priority": priority.lower(),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.tasks.append(task)
        self._save_tasks()
        return task
    
    def update_task(self, task_id: int, **kwargs) -> Optional[Dict]:
        """Update a task by ID."""
        for task in self.tasks:
            if task["id"] == task_id:
                for key, value in kwargs.items():
                    if key in task:
                        task[key] = value
                self._save_tasks()
                return task
        return None
    
    def mark_complete(self, task_id: int) -> Optional[Dict]:
        """Mark a task as complete."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                self._save_tasks()
                return task
        return None
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                self.tasks.pop(i)
                self._save_tasks()
                return True
        return False
    
    def list_tasks(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Dict]:
        """List tasks with optional filtering."""
        filtered = self.tasks
        
        if status:
            filtered = [t for t in filtered if t["status"] == status.lower()]
        if priority:
            filtered = [t for t in filtered if t["priority"] == priority.lower()]
        
        return sorted(filtered, key=lambda t: t["id"])
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get a specific task by ID."""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def display_task(self, task: Dict) -> str:
        """Format a task for display."""
        status_symbol = "✓" if task["status"] == "completed" else "○"
        priority_symbol = {"high": "!", "medium": "-", "low": "•"}.get(task["priority"], "-")
        
        return (
            f"{status_symbol} [{priority_symbol}] Task #{task['id']}: {task['title']}\n"
            f"   Status: {task['status']} | Priority: {task['priority']}\n"
            f"   Description: {task['description'] or '(none)'}\n"
            f"   Created: {task['created_at']}"
        )


def main():
    """Main CLI interface for the task tracker."""
    tracker = TaskTracker()
    
    while True:
        print("\n=== Task Tracker ===")
        print("1. Add task")
        print("2. List tasks")
        print("3. Mark complete")
        print("4. Update task")
        print("5. Delete task")
        print("6. View task")
        print("7. Exit")
        
        choice = input("\nSelect an option (1-7): ").strip()
        
        if choice == "1":
            title = input("Task title: ").strip()
            description = input("Description (optional): ").strip()
            priority = input("Priority (high/medium/low) [medium]: ").strip() or "medium"
            
            task = tracker.add_task(title, description, priority)
            print(f"\n✓ Task added (ID: {task['id']})")
        
        elif choice == "2":
            status_filter = input("Filter by status (pending/completed/all) [all]: ").strip() or "all"
            priority_filter = input("Filter by priority (high/medium/low/all) [all]: ").strip() or "all"
            
            status = None if status_filter == "all" else status_filter
            priority = None if priority_filter == "all" else priority_filter
            
            tasks = tracker.list_tasks(status, priority)
            
            if tasks:
                print(f"\n=== Tasks ({len(tasks)}) ===")
                for task in tasks:
                    print(tracker.display_task(task))
            else:
                print("\nNo tasks found.")
        
        elif choice == "3":
            task_id = input("Task ID to mark complete: ").strip()
            try:
                task = tracker.mark_complete(int(task_id))
                if task:
                    print(f"\n✓ Task #{task_id} marked as completed")
                else:
                    print(f"\n✗ Task #{task_id} not found")
            except ValueError:
                print("\n✗ Invalid task ID")
        
        elif choice == "4":
            task_id = input("Task ID to update: ").strip()
            try:
                task = tracker.get_task(int(task_id))
                if task:
                    print(f"\nCurrent task: {tracker.display_task(task)}")
                    new_title = input("New title (leave blank to keep): ").strip()
                    new_desc = input("New description (leave blank to keep): ").strip()
                    new_priority = input("New priority (leave blank to keep): ").strip()
                    
                    updates = {}
                    if new_title:
                        updates["title"] = new_title
                    if new_desc:
                        updates["description"] = new_desc
                    if new_priority:
                        updates["priority"] = new_priority
                    
                    if updates:
                        tracker.update_task(int(task_id), **updates)
                        print("\n✓ Task updated")
                    else:
                        print("\n- No changes made")
                else:
                    print(f"\n✗ Task #{task_id} not found")
            except ValueError:
                print("\n✗ Invalid task ID")
        
        elif choice == "5":
            task_id = input("Task ID to delete: ").strip()
            try:
                if tracker.delete_task(int(task_id)):
                    print(f"\n✓ Task #{task_id} deleted")
                else:
                    print(f"\n✗ Task #{task_id} not found")
            except ValueError:
                print("\n✗ Invalid task ID")
        
        elif choice == "6":
            task_id = input("Task ID to view: ").strip()
            try:
                task = tracker.get_task(int(task_id))
                if task:
                    print(f"\n{tracker.display_task(task)}")
                else:
                    print(f"\n✗ Task #{task_id} not found")
            except ValueError:
                print("\n✗ Invalid task ID")
        
        elif choice == "7":
            print("Goodbye!")
            break
        
        else:
            print("\n✗ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
