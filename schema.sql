CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    done BOOLEAN DEFAULT 0,
    priority INTEGER DEFAULT 0,
    due_date DATE,
    start_date DATE,
    end_date DATE,
    is_recurring BOOLEAN DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE recurrence (
    task_id INTEGER,
    day INTEGER,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE  -- Delete recurrence if task is deleted
);
