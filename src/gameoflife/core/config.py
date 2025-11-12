"""Configuration management for Game of Life."""
from pathlib import Path
import platformdirs

#class Taskpriority used to establish the different priority levels
class TaskPriority:
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def all(cls):
        """Return all priority levels."""
        return [cls.LOW, cls.MEDIUM, cls.HIGH, cls.CRITICAL]

#clas TaskStatus used to establish the different priority levels of a task
class TaskStatus:
    """Task status states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    FAILED = "failed"

    @classmethod
    def all(cls):
        """Return all status states."""
        return [cls.PENDING, cls.IN_PROGRESS, cls.COMPLETED, cls.OVERDUE, cls.FAILED]


class Task:
    """Base task class."""
    #We have set taskpriority set to medium and taskstatus set to pending for this class as default parameter values
    def __init__(self, title, priority=TaskPriority.MEDIUM, status=TaskStatus.PENDING,
                 due_date=None, description=""):
        self.id = None
        self.title = title
        self.priority = priority
        self.status = status
        self.due_date = due_date
        self.description = description
        # self.created_at = None
        # self.completed_at = None

    def is_completed(self):
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED

    def is_overdue(self):
        """Check if task is overdue."""
        return self.status == TaskStatus.OVERDUE

    def mark_completed(self):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED

    def mark_failed(self):
        """Mark task as failed."""
        self.status = TaskStatus.FAILED


class XPConfig:
    """Experience points configuration."""

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

        if base_penalties is None:
            self.base_penalties = {
                TaskPriority.LOW: 15,
                TaskPriority.MEDIUM: 38,
                TaskPriority.HIGH: 75,
                TaskPriority.CRITICAL: 150
            }
        else:
            self.base_penalties = base_penalties

        if early_bonus_thresholds is None:
            self.early_bonus_thresholds = [
                {"days_early": 7, "bonus_pct": 50},
                {"days_early": 3, "bonus_pct": 25},
                {"hours_early": 24, "bonus_pct": 10}
            ]
        else:
            self.early_bonus_thresholds = early_bonus_thresholds


class RankConfig:
    """Rank configuration."""

    def __init__(self, name, xp_min):
        self.name = name
        self.xp_min = xp_min

def get_rank_for_xp(self, xp):
    """Get rank based on XP."""
    for rank in reversed(self.ranks):
        if xp >= rank.xp_min:
            return rank.name
    return self.ranks[0].name

class Config:
    """Main application configuration."""

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