import datetime
from pathlib import Path
import platformdirs

#class Taskpriority used to establish the different priority levels
class TaskPriority:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


#clas TaskStatus used to establish the different priority levels of a task
class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    FAILED = "failed"


class Task:
    #We have set taskpriority set to medium and taskstatus set to pending for this class as default parameter values
    def __init__(self, title, priority=TaskPriority.MEDIUM, status=TaskStatus.PENDING,
                 due_date=None, description=""):
    
        self.id = id
        self.title = title
        self.priority = priority
        self.status = status
        self.due_date = due_date
        self.description = description
        self.created_at = datetime.datetime.now() # --- UPDATED: Added default creation time
        self.completed_at = None


    def mark_completed(self):
        #marks the task as completed if it is completed
        self.status = TaskStatus.COMPLETED


class XPConfig:
    def __init__(self, base_rewards=None, base_penalties=None,
                 early_bonus_thresholds=None, xp_floor=0):
        self.xp_floor = xp_floor

        if base_rewards is None:
            self.base_rewards = {
                TaskPriority.LOW: 10,
                TaskPriority.MEDIUM: 25,
                TaskPriority.HIGH: 50,
                TaskPriority.CRITICAL: 100
            }
        else:
            #otherwise it not None, base reward is set to itself
            self.base_rewards = base_rewards

        if early_bonus_thresholds is None:
            self.early_bonus_thresholds = [
                {"days_early": 7, "bonus_pct": 50},
                {"days_early": 3, "bonus_pct": 25},
                {"hours_early": 24, "bonus_pct": 10}
            ]
        else:
            self.early_bonus_thresholds = early_bonus_thresholds


class RankConfig:

    def __init__(self, name, xp_min):
        self.name = name
        self.xp_min = xp_min


class Config:

    def __init__(self, xp_per_level=200, ranks=None, xp_config=None, db_path=None):
        self.xp_per_level = xp_per_level

        if ranks is None:
            self.ranks = [
                #Rank names, LOL
                RankConfig("Procrastinator", 0),
                RankConfig("Dabbler", 200),
                RankConfig("Doer", 600),
                RankConfig("Achiever", 1200),
                RankConfig("Champion", 2000),
                RankConfig("Master", 3000),
                RankConfig("Legend", 5000)
            ]
        else:
            self.ranks = ranks

        if xp_config is None:
            self.xp_config = XPConfig()
        else:
            self.xp_config = xp_config

        if db_path is None:
            data_dir = Path(platformdirs.user_data_dir("GameOfLife"))
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = data_dir / "gamelife.db"
        else:
            self.db_path = db_path


# Global configuration instance
config = Config()