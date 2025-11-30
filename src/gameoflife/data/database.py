import sqlite3
import datetime
from config import *
from game import *

class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()    

    def create_tables(self):
        cursor = self.conn.cursor()
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                created_at DATETIME NOT NULL
            )
        """)
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                due_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
            
        # Achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                date_earned DATE NOT NULL,
                xp_reward INTEGER DEFAULT 0,
                metadata TEXT,
                FOREIGN KEY (player_id) REFERENCES players (id),
                UNIQUE(player_id, name)
            )
        """)
        
        # XP History table (for tracking XP changes over time)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS xp_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                xp_change INTEGER NOT NULL,
                reason TEXT NOT NULL,
                task_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (id),
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_user_status 
            ON tasks (user_id, status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_due_date 
            ON tasks (due_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_achievements_player 
            ON achievements (player_id)
        """)


    self.conn.commit()

def create_user(self, username, email):
    """Create a new user and player profile."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        # Create user
        cursor.execute("""
            INSERT INTO users (username, email, created_at)
            VALUES (?, ?, ?)
        """, (username, email, datetime.datetime.now()))
        
        user_id = cursor.lastrowid
        
        # Create player profile
        cursor.execute("""
            INSERT INTO players (user_id)
            VALUES (?)
        """, (user_id,))
        
        return user_id

def get_user_by_username(self, username):
    """Get user by username."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            user = User(row['username'], row['email'])
            user.created_at = datetime.datetime.fromisoformat(row['created_at'])
            return user, row['id']
        return None, None

def get_user_by_id(self, user_id):
    """Get user by ID."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            user = User(row['username'], row['email'])
            user.created_at = datetime.datetime.fromisoformat(row['created_at'])
            return user
        return None

# ============= PLAYER OPERATIONS =============

def get_player(self, user_id):
    """Get player data by user_id."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get user
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            return None
        
        user = User(user_row['username'], user_row['email'])
        user.created_at = datetime.datetime.fromisoformat(user_row['created_at'])
        
        # Get player data
        cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
        player_row = cursor.fetchone()
        
        if not player_row:
            return None
        
        # Create player object
        player = Player(user, xp=player_row['xp'], level=player_row['level'])
        player.tasks_completed = player_row['tasks_completed']
        player.tasks_failed = player_row['tasks_failed']
        player.current_streak = player_row['current_streak']
        player.longest_streak = player_row['longest_streak']
        player.tasks_completed_early = player_row['tasks_completed_early']
        player.tasks_completed_at_night = player_row['tasks_completed_at_night']
        player.critical_tasks_completed = player_row['critical_tasks_completed']
        player.perfect_days = player_row['perfect_days']
        player.previous_rank = player_row['previous_rank']
        
        # Load achievements
        cursor.execute("""
            SELECT * FROM achievements WHERE player_id = ?
        """, (player_row['id'],))
        
        for ach_row in cursor.fetchall():
            achievement = Achievement(
                name=ach_row['name'],
                description=ach_row['description'],
                date_earned=datetime.date.fromisoformat(ach_row['date_earned']),
                xp_reward=ach_row['xp_reward']
            )
            player.achievements.append(achievement)
        
        return player, player_row['id']

def save_player(self, user_id, player):
    """Save player data."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        # Get player_id
        cursor.execute("SELECT id FROM players WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"No player found for user_id {user_id}")
        
        player_id = row['id']
        
        # Update player data
        cursor.execute("""
            UPDATE players SET
                xp = ?,
                level = ?,
                tasks_completed = ?,
                tasks_failed = ?,
                current_streak = ?,
                longest_streak = ?,
                tasks_completed_early = ?,
                tasks_completed_at_night = ?,
                critical_tasks_completed = ?,
                perfect_days = ?,
                previous_rank = ?
            WHERE user_id = ?
        """, (
            player.xp,
            player.level,
            player.tasks_completed,
            player.tasks_failed,
            player.current_streak,
            player.longest_streak,
            player.tasks_completed_early,
            player.tasks_completed_at_night,
            player.critical_tasks_completed,
            player.perfect_days,
            player.previous_rank,
            user_id
        ))

# ============= TASK OPERATIONS =============

def create_task(self, user_id, task):
    """Create a new task."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (
                user_id, title, description, priority, status, 
                due_date, created_at, estimated_duration
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            task.title,
            task.description,
            task.priority,
            task.status,
            task.due_date,
            task.created_at,
            getattr(task, 'estimated_duration', None)
        ))
        
        task_id = cursor.lastrowid
        return task_id

def get_task(self, task_id):
    """Get a task by ID."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_task(row), row['user_id']
        return None, None

def get_user_tasks(self, user_id, status=None):
    """Get all tasks for a user, optionally filtered by status."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE user_id = ? AND status = ?
                ORDER BY due_date
            """, (user_id, status))
        else:
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE user_id = ?
                ORDER BY due_date
            """, (user_id,))
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append(self._row_to_task(row))
        
        return tasks

def update_task(self, task_id, task):
    """Update a task."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks SET
                title = ?,
                description = ?,
                priority = ?,
                status = ?,
                due_date = ?,
                completed_at = ?
            WHERE id = ?
        """, (
            task.title,
            task.description,
            task.priority,
            task.status,
            task.due_date,
            task.completed_at,
            task_id
        ))

def delete_task(self, task_id):
    """Delete a task."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

def _row_to_task(self, row):
    """Convert database row to Task object."""
    task = Task(
        title=row['title'],
        priority=row['priority'],
        status=row['status'],
        due_date=datetime.datetime.fromisoformat(row['due_date']) if row['due_date'] else None,
        description=row['description'] or ""
    )
    task.created_at = datetime.datetime.fromisoformat(row['created_at']) if row['created_at'] else None
    task.completed_at = datetime.datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None
    
    if row['estimated_duration']:
        task.estimated_duration = row['estimated_duration']
    
    return task

# ============= ACHIEVEMENT OPERATIONS =============

def save_achievement(self, player_id, achievement):
    """Save an achievement."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO achievements (
                    player_id, name, description, date_earned, xp_reward
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                player_id,
                achievement.name,
                achievement.description,
                achievement.date_earned,
                achievement.xp_reward
            ))
            return True
        except sqlite3.IntegrityError:
            # Achievement already exists for this player
            return False

# ============= XP HISTORY OPERATIONS =============

def log_xp_change(self, player_id, xp_change, reason, task_id=None):
    """Log an XP change to history."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO xp_history (player_id, xp_change, reason, task_id)
            VALUES (?, ?, ?, ?)
        """, (player_id, xp_change, reason, task_id))

def get_xp_history(self, player_id, limit=50):
    """Get XP history for a player."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM xp_history
            WHERE player_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (player_id, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'xp_change': row['xp_change'],
                'reason': row['reason'],
                'timestamp': row['timestamp']
            })
        
        return history

# ============= STATISTICS =============

def get_leaderboard(self, limit=10):
    """Get top players by XP."""
    with self.get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.username, p.xp, p.level, p.tasks_completed
            FROM players p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.xp DESC
            LIMIT ?
        """, (limit,))
        
        leaderboard = []
        for row in cursor.fetchall():
            leaderboard.append({
                'username': row['username'],
                'xp': row['xp'],
                'level': row['level'],
                'tasks_completed': row['tasks_completed']
            })
        
        return leaderboard