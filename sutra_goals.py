# sutra_goals.py — SQLite-backed goal/task persistence for SutraAgent
import sqlite3
import os
import time

DB_PATH = "/data/data/com.termux/files/home/sutra_life.db"

def _init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT DEFAULT 'GENERAL',
            status TEXT DEFAULT 'PENDING',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def add_goal(text, priority=1):
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, category, status) VALUES (?, 'GOAL', 'PENDING')",
        (text,)
    )
    conn.commit()
    goal_id = cursor.lastrowid
    conn.close()
    return goal_id

def get_pending():
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT task_id, title, created_at FROM tasks WHERE category = 'GOAL' AND status = 'PENDING'"
    )
    rows = cursor.fetchall()
    conn.close()
    
    goals = []
    for r in rows:
        goals.append({
            "id": r[0],
            "text": r[1],
            "status": "pending",
            "priority": 1,
            "created_at": r[2],
            "result": None
        })
    return goals

def list_goals():
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT task_id, title, status, created_at FROM tasks WHERE category = 'GOAL'"
    )
    rows = cursor.fetchall()
    conn.close()
    
    goals = []
    for r in rows:
        goals.append({
            "id": r[0],
            "text": r[1],
            "status": r[2].lower(),
            "priority": 1,
            "created_at": r[3],
            "result": None
        })
    return goals

def mark_done(goal_id, result=""):
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = 'COMPLETED' WHERE task_id = ?",
        (goal_id,)
    )
    conn.commit()
    conn.close()

def mark_failed(goal_id, error=""):
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = 'FAILED' WHERE task_id = ?",
        (goal_id,)
    )
    conn.commit()
    conn.close()

def delete_goal(goal_id):
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE task_id = ?", (goal_id,))
    conn.commit()
    conn.close()

def clear_done():
    _init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM tasks WHERE category = 'GOAL' AND status IN ('COMPLETED', 'FAILED')"
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if not args:
        goals = list_goals()
        if not goals:
            print("No goals stored.")
        else:
            print(f"{'ID':<15} {'STATUS':<10} {'GOAL'}")
            print("-" * 80)
            for g in goals:
                print(f"{g['id']:<15} {g['status']:<10} {g['text'][:60]}")
    elif args[0] == "add":
        text = " ".join(args[1:])
        gid = add_goal(text)
        print(f"Goal added with ID: {gid}")
    elif args[0] == "done":
        mark_done(int(args[1]))
        print(f"Goal {args[1]} marked done.")
    elif args[0] == "delete":
        delete_goal(int(args[1]))
        print(f"Goal {args[1]} deleted.")
    elif args[0] == "clear":
        clear_done()
        print("Cleared all completed/failed goals.")
    elif args[0] == "pending":
        pending = get_pending()
        print(f"{len(pending)} pending goal(s):")
        for g in pending:
            print(f"  [{g['id']}] {g['text']}")
