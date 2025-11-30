import datetime
from config import *
import database #used for add_task method and complete_tasks

class User:
    def __init__(self, username, email):
        #initialize the users profile data
        self.username = username
        self.email = email
        #automatically sets the creation time stamp to current date and time
        self.created_at = datetime.datetime.now()

    def __repr__(self):
        #we have our object, this just provides a string representation of it
        #if you print user object this is what appears
        return f"User(username={self.username}, email={self.email}, created_at={self.created_at})"


class Achievement:
    def __init__(self, name: str, description: str, date_earned: datetime.date, xp_reward: int = 0):

        self.name = name
        self.description = description #sets our string parameter 'description' that you will see later on in the code
        self.date_earned = date_earned
        self.xp_reward = xp_reward  #default XP reward, default to 0 if it isn't specified

    def __repr__(self):
        #readable summary of achievemnt stuff
        #these __repr__ are optional but used inside of the jupyter notebooks from lecture -> good for debugging
        return f"Achievement(name={self.name}, description={self.description}, date_earned={self.date_earned})"


class FirstTaskCompleted(Achievement):
    #sepcific class used only for a first achievement
    #used to output reward text after first achievement. intended to keep users engaged so they dont have to complete 10 tasks to get a nice message
    #note it inherits the parameters from the Achievement super class
    def __init__(self):
        super().__init__(
            name="First Task Completed",
            description="Awarded for completing your first task.",
            date_earned=datetime.date.today(),
            xp_reward=25
        )


class EarlyBirdAchievement(Achievement):
    #same idea as previous class, used when you complete 10 tasks early
    #note it inherits the parameters from the Achievement super class
    def __init__(self):
        super().__init__(
            name="Early Bird",
            description="Awarded for completing 10 tasks early.",
            date_earned=datetime.date.today(),
            xp_reward=50
        )


class RankUpAchievement(Achievement):
    def __init__(self, rank_name: str):
        super().__init__(
            name=f"Rank Up: {rank_name}",
            description=f"Reached the {rank_name} rank!",
            date_earned=datetime.date.today(),
            xp_reward=50
        )
        self.rank_name = rank_name


class Player:
    def __init__(self, user, xp=0, level=1):
        self.id = None
        self.user = user
        self.xp = xp
        self.level = level
        self.achievements = []
        self.tasks_completed = 0
        self.current_streak = 0
        self.longest_streak = 0
        #below are added after clone repo
        self.tasks_failed = 0
        self.previous_rank = None
        self.tasks_completed_early = 0
        self.critical_tasks_completed = 0




    def add_xp(self, amount):
        self.xp = max(config.xp_config.xp_floor, self.xp + amount)
        self._check_level_up()

    def _check_level_up(self):
        new_level = (self.xp // config.xp_per_level) + 1
        if new_level > self.level:
            self.level = new_level
            return True
        return False

    def get_rank(self):
        for rank in reversed(config.ranks):
            if self.xp >= rank.xp_min:
                return rank.name
        return config.ranks[0].name

    def get_progress_to_next_level(self):
        xp_into_current_level = self.xp % config.xp_per_level
        return (xp_into_current_level / config.xp_per_level) * 100

    def award_achievement(self, achievement):
        self.achievements.append(achievement)
        if hasattr(achievement, 'xp_reward'):
            self.add_xp(achievement.xp_reward)


class XPCalculator:

    def __init__(self, xp_config):
        self.config = xp_config

    def calculate_completion_xp(self, task, completion_time=None):
        base_xp = self.config.base_rewards[task.priority]

        if task.due_date and completion_time:
            bonus = self._calculate_early_bonus(task.due_date, completion_time, base_xp)
            return base_xp + bonus

        return base_xp

    def calculate_failure_penalty(self, task):
        return self.config.base_penalties[task.priority]

    def _calculate_early_bonus(self, due_date, completion_time, base_xp):
        time_early = due_date - completion_time

        for threshold in self.config.early_bonus_thresholds:
            if 'days_early' in threshold and time_early.days >= threshold['days_early']:
                return int(base_xp * threshold['bonus_pct'] / 100)

        return 0


class TaskManager:
    """Manages tasks and coordinates game mechanics."""
    
    def __init__(self, player,user_id, player_id, xp_calculator=None):
        self.player = player
        self.user_id = user_id
        self.player_id = player_id
        self.xp_calculator = xp_calculator or XPCalculator(config.xp_config)
        self.active_tasks = []
        self.completed_tasks = []
        self.failed_tasks = []

    def add_task(self, task):
        """Add a new task."""
        #in this defined function we need to give it the ability to save to DB
        task_id = database.insert_task(task, self.user_id)  #used to save to database
        task.id = task_id  #used to save the users id

        task.created_at = datetime.datetime.now()
        self.active_tasks.append(task)
        return task

    def complete_task(self, task):
        if task not in self.active_tasks:
            raise ValueError("Task not found in active tasks")

        task.mark_completed()
        task.completed_at = datetime.datetime.now()

        #used to update the database
        database.update_task_status(task.id, TaskStatus.COMPLETED, task.completed_at)
        
        # Calculate XP
        xp_earned = self.xp_calculator.calculate_completion_xp(task, task.completed_at)
        xp_result = self.player.add_xp(xp_earned)

        # Update player stats
        self.player.tasks_completed += 1
        self.player.current_streak += 1

        # Track early completion
        if task.priority == TaskPriority.CRITICAL: #TaskPriority from config.py
            self.player.critical_tasks_completed += 1

        # Move task to completed
        self.active_tasks.remove(task)
        self.completed_tasks.append(task)

        # Check for achievements
        new_achievements = self._check_achievements()

        # Check for rank up
        current_rank = self.player.get_rank()
        rank_changed = False
        if self.player.previous_rank != current_rank:
            rank_changed = True
            if self.player.previous_rank is not None:
                self.player.award_achievement(RankUpAchievement(current_rank))
                new_achievements.append(RankUpAchievement(current_rank))
            self.player.previous_rank = current_rank

        #used at the end of the block to save all players stats
        database.update_player_stats(
            self.player_id, self.player.xp, self.player.level,
            self.player.tasks_completed, self.player.tasks_failed,
            self.player.current_streak, self.player.longest_streak,
            self.player.tasks_completed_early, self.player.critical_tasks_completed,
            self.player.previous_rank
            )
        
        return {
            'xp_earned': xp_earned,
            'xp_result': xp_result,
            'new_achievements': new_achievements,
            'rank_changed': rank_changed,
            'new_rank': current_rank if rank_changed else None
        }

    def _check_achievements(self):
        new_achievements = []

        #This is the first task achievement
        if self.player.tasks_completed == 1:
            achievement = FirstTaskCompleted()
            if self.player.award_achievement(achievement):
                new_achievements.append(achievement)

        #The early bird achievement
        if self.player.tasks_completed_early == 10:
            achievement = EarlyBirdAchievement()
            if self.player.award_achievement(achievement):
                new_achievements.append(achievement)

        #To update longest streak
        if self.player.current_streak > self.player.longest_streak:
            self.player.longest_streak = self.player.current_streak

        return new_achievements

    def get_active_tasks(self, sort_by='priority'):
        if sort_by == 'priority':
            priority_order = {
                TaskPriority.CRITICAL: 0,
                TaskPriority.HIGH: 1,
                TaskPriority.MEDIUM: 2,
                TaskPriority.LOW: 3
            }
            return sorted(self.active_tasks, key=lambda t: priority_order[t.priority])
        elif sort_by == 'due_date':
            return sorted(self.active_tasks, key=lambda t: t.due_date if t.due_date else datetime.datetime.max)
        else:
            return self.active_tasks
