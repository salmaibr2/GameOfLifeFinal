import datetime
from config import *
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.created_at = datetime.datetime.now()

    def __repr__(self):
        return f"User(username={self.username}, email={self.email}, created_at={self.created_at})"

class Achievement:
    def __init__(self, name: str, description: str, date_earned: datetime.date):
        self.name = name
        self.description = description
        self.date_earned = date_earned

    def __repr__(self):
        return f"Achievement(name={self.name}, description={self.description}, date_earned={self.date_earned})"     
    
class FirstTaskCompleted(Achievement):
    def __init__(self):
        super().__init__(
            name="First Task Completed",
            description="Awarded for completing your first task.",
            date_earned=datetime.date.today()
            xp_reward=25
        )

class TaskStreakAchievement(Achievement):
    def __init__(self, streak_length: int):
        super().__init__(
            name="Task Streak",
            description=f"Awarded for completing {streak_length} tasks in a row.",
            date_earned=datetime.date.today()
            xp_reward=streak_length * 10
        )
        self.early_bonus_thresholds = {
                TaskPriority.LOW: 2,
                TaskPriority.MEDIUM: 4,
                TaskPriority.HIGH: 6,
                TaskPriority.CRITICAL: 8
            }


