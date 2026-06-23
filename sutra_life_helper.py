#!/usr/bin/env python3
import sys
import os
import sqlite3
import argparse
import subprocess

DB_PATH = "/data/data/com.termux/files/home/sutra_life.db"
YT_DB_PATH = "/data/data/com.termux/files/home/youtube_channels.db"
TTS_BINARY = "/data/data/com.termux/files/usr/bin/termux-tts-speak"

def speak(text):
    print(text)
    if os.path.exists(TTS_BINARY):
        try:
            subprocess.run([TTS_BINARY, text], check=True)
        except Exception as e:
            # Silence speech errors but print them
            print(f"[TTS Error: {e}]", file=sys.stderr)

def init_db():
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

def add_task(title, category="GENERAL"):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, category) VALUES (?, ?)", (title, category))
    conn.commit()
    conn.close()
    speak(f"Task added successfully: {title}")

def list_tasks():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT task_id, title, category FROM tasks WHERE status = 'PENDING'")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        speak("Aapke pass koi pending tasks nahi hain. Sab completed hai!")
        return
        
    speak(f"Aapke pass {len(rows)} pending tasks hain.")
    for row in rows:
        speak(f"Task {row[0]}: {row[1]}")

def complete_task(task_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if task exists and is pending
    cursor.execute("SELECT title FROM tasks WHERE task_id = ? AND status = 'PENDING'", (task_id,))
    row = cursor.fetchone()
    if not row:
        speak(f"Error. Task ID {task_id} ya toh pending nahi hai ya exist nahi karta.")
        conn.close()
        return
        
    cursor.execute("UPDATE tasks SET status = 'COMPLETED' WHERE task_id = ?", (task_id,))
    conn.commit()
    conn.close()
    speak(f"Task completed: {row[0]}")

def get_youtube_status():
    if not os.path.exists(YT_DB_PATH):
        speak("YouTube channels database nahi mila.")
        return
        
    try:
        conn = sqlite3.connect(YT_DB_PATH)
        cursor = conn.cursor()
        
        # Count total channels
        cursor.execute("SELECT COUNT(*) FROM channels")
        channels_count = cursor.fetchone()[0]
        
        # Fetch pending videos count
        cursor.execute("SELECT COUNT(*) FROM video_queue WHERE status = 'PENDING'")
        pending_count = cursor.fetchone()[0]
        
        # Fetch channels with their pending video counts
        cursor.execute("""
            SELECT c.name, COUNT(v.video_id) 
            from channels c 
            LEFT JOIN video_queue v ON c.channel_id = v.channel_id AND v.status = 'PENDING'
            GROUP BY c.channel_id
        """)
        channel_details = cursor.fetchall()
        conn.close()
        
        speak(f"YouTube status check. Aapke pass total {channels_count} channels setup hain.")
        speak(f"Video queue me {pending_count} videos pending hain.")
        
        for name, count in channel_details:
            if count > 0:
                speak(f"Channel {name} me {count} videos pending hain.")
    except Exception as e:
        speak(f"YouTube status fetch karne me error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="SutraLife database helper")
    parser.add_argument("--add", type=str, help="Add a task")
    parser.add_argument("--cat", type=str, default="GENERAL", help="Task category")
    parser.add_argument("--list", action="store_true", help="List tasks")
    parser.add_argument("--complete", type=int, help="Mark task as complete by ID")
    parser.add_argument("--youtube", action="store_true", help="Check YouTube channel queue status")
    parser.add_argument("--speak", type=str, help="Speak a text line")
    
    args = parser.parse_args()
    
    if args.add:
        add_task(args.add, args.cat)
    elif args.list:
        list_tasks()
    elif args.complete:
        complete_task(args.complete)
    elif args.youtube:
        get_youtube_status()
    elif args.speak:
        speak(args.speak)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
