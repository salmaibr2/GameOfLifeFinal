# Referenced from this youtube video: https://www.youtube.com/watch?v=pd-0G0MigUA

import sqlite3
import datetime
from config import config, Task

#global connection - will be initialized when init_db() is called
conn = None
c = None


def init_db():
    global conn, c

    #connect to database
    conn = sqlite3.connect(config.db_path)
    c = conn.cursor()

    #enable foreign keys b/c sqlite has them off as default
    c.execute("PRAGMA foreign_keys = ON")



    #create users table
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                created_at TEXT NOT NULL
                )""")

    #create players table
    c.execute("""CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                tasks_completed INTEGER DEFAULT 0,
                tasks_failed INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                tasks_completed_early INTEGER DEFAULT 0,
                critical_tasks_completed INTEGER DEFAULT 0,
                previous_rank TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
                )""")


    #Updated create tasks table
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        due_date TEXT,
        description TEXT,
        created_at TEXT,
        completed_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    #create achievements table
    c.execute("""CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                date_earned TEXT NOT NULL,
                xp_reward INTEGER DEFAULT 0,
                FOREIGN KEY (player_id) REFERENCES players(id)
                )""")

    #commit schema changes
    conn.commit()
    print(f"Database initialized at: {config.db_path}")


def insert_user(user):
    """Insert a new user into the database."""
    with conn:
        c.execute("""INSERT INTO users (username, email, created_at) 
                     VALUES (:username, :email, :created_at)""",
                  {'username': user.username,
                   'email': user.email,
                   'created_at': user.created_at.isoformat()})
        return c.lastrowid  #return the new user's ID


def get_user_by_username(username):
    c.execute("SELECT * FROM users WHERE username = :username", {'username': username})
    return c.fetchone()


def get_all_users():
    c.execute("SELECT * FROM users")
    return c.fetchall()


def insert_player(user_id):
    with conn:
        c.execute("""INSERT INTO players (user_id, xp, level, tasks_completed, 
                     tasks_failed, current_streak, longest_streak, 
                     tasks_completed_early, critical_tasks_completed) 
                     VALUES (:user_id, 0, 1, 0, 0, 0, 0, 0, 0)""",
                  {'user_id': user_id})
        return c.lastrowid


def get_player_by_user_id(user_id):
    c.execute("SELECT * FROM players WHERE user_id = :user_id", {'user_id': user_id})
    return c.fetchone()


def update_player_stats(player_id, xp, level, tasks_completed, tasks_failed,
                        current_streak, longest_streak, tasks_completed_early,
                        critical_tasks_completed, previous_rank):
    with conn:
        c.execute("""UPDATE players SET 
                     xp = :xp,
                     level = :level,
                     tasks_completed = :tasks_completed,
                     tasks_failed = :tasks_failed,
                     current_streak = :current_streak,
                     longest_streak = :longest_streak,
                     tasks_completed_early = :tasks_completed_early,
                     critical_tasks_completed = :critical_tasks_completed,
                     previous_rank = :previous_rank
                     WHERE id = :player_id""",
                  {'xp': xp, 'level': level, 'tasks_completed': tasks_completed,
                   'tasks_failed': tasks_failed, 'current_streak': current_streak,
                   'longest_streak': longest_streak,
                   'tasks_completed_early': tasks_completed_early,
                   'critical_tasks_completed': critical_tasks_completed,
                   'previous_rank': previous_rank, 'player_id': player_id})


def insert_task(task, user_id):
    with conn:
        c.execute("""INSERT INTO tasks
            (user_id, title, priority, status, due_date, description, created_at, completed_at)
            VALUES (:user_id, :title, :priority, :status, :due_date, :description, :created_at, :completed_at)""",
            {
                'user_id': user_id,
                'title': task.title,
                'priority': task.priority,
                'status': task.status,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'description': task.description,
                'created_at': datetime.datetime.now().isoformat(),
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            }
        )
        return c.lastrowid


def get_tasks_by_user(user_id, status=None):
    base = "SELECT * FROM tasks WHERE user_id = :user_id"
    params = {'user_id': user_id}
    if status:
        base += " AND status = :status"
        params['status'] = status
    c.execute(base, params)

    rows = c.fetchall()
    tasks = []
    for row in rows:
        # 0 id, 1 user_id, 2 title, 3 priority, 4 status,
        # 5 due_date, 6 description, 7 created_at, 8 completed_at
        task = Task(
            title=row[2],
            priority=row[3],
            status=row[4],
            due_date=datetime.datetime.fromisoformat(row[5]) if row[5] else None,
            description=row[6]
        )
        task.id = row[0]
        task.created_at = datetime.datetime.fromisoformat(row[7]) if row[7] else None
        task.completed_at = datetime.datetime.fromisoformat(row[8]) if row[8] else None
        tasks.append(task)
    return tasks


def update_task_status(task_id, new_status, completed_at=None):
    with conn:
        c.execute("""UPDATE tasks
                     SET status = :status, completed_at = :completed_at
                     WHERE id = :task_id""",
                  {'status': new_status,
                   'completed_at': completed_at.isoformat() if completed_at else None,
                   'task_id': task_id})

