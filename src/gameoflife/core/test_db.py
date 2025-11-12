"""Test script to verify database functionality."""
import database
from game import User, Player, Achievement
from config import Task, TaskPriority, TaskStatus
import datetime

#initialize the database
database.init_db()

#create new user
user = User("test_agian", "test@example.com")
user_id = database.insert_user(user)
print(f"Created user with ID: {user_id}")

#create player for the user
player_id = database.insert_player(user_id)
print(f"Created player with ID: {player_id}")

#create and save  task
task = Task("Complete homework", TaskPriority.HIGH, TaskStatus.PENDING,
            due_date=datetime.datetime.now() + datetime.timedelta(days=3),
            description="Finish the Python project")
task_id = database.insert_task(task, user_id)
print(f"Created task with ID: {task_id}")

# Load tasks back from database
loaded_tasks = database.get_tasks_by_user(user_id)
print(f"\nLoaded {len(loaded_tasks)} task(s):")
for t in loaded_tasks:
    print(f"  - {t.title} (ID: {t.id}, Priority: {t.priority})")

# Update player stats
database.update_player_stats(player_id, xp=100, level=2, tasks_completed=5,
                             tasks_failed=0, current_streak=3, longest_streak=3,
                             tasks_completed_early=1, critical_tasks_completed=0,
                             previous_rank="Procrastinator")

# Load player back
player_data = database.get_player_by_user_id(user_id)
print(f"\nPlayer stats: XP={player_data[2]}, Level={player_data[3]}")

database.close_db()
print("\nDatabase test complete!")