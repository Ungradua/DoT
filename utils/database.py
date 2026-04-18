import sqlite3
import os
import random
import time

# Ensure /data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), '../../data')
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, 'dot.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Create users table if it doesn't exist
with get_connection() as conn:
    conn.execute('PRAGMA journal_mode = WAL;')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            discord_id   TEXT PRIMARY KEY,
            roblox_id    TEXT NOT NULL,
            roblox_username TEXT NOT NULL,
            discord_role TEXT NOT NULL,
            service_number TEXT NOT NULL UNIQUE,
            avatar_url   TEXT NOT NULL,
            created_at   INTEGER NOT NULL,
            updated_at   INTEGER NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            officer_id   TEXT NOT NULL,
            officer_svc  TEXT NOT NULL,
            violator_id  TEXT NOT NULL,
            violation_type TEXT NOT NULL,
            proof_link   TEXT,
            punishment   TEXT,
            staff_id     TEXT,
            created_at   INTEGER NOT NULL
        )
    ''')

def get_user(discord_id: str):
    with get_connection() as conn:
        cursor = conn.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
        return cursor.fetchone()

def create_user(data: dict):
    now = int(time.time())
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO users (discord_id, roblox_id, roblox_username, discord_role, service_number, avatar_url, created_at, updated_at)
            VALUES (:discord_id, :roblox_id, :roblox_username, :discord_role, :service_number, :avatar_url, :created_at, :updated_at)
        ''', {**data, 'created_at': now, 'updated_at': now})

def add_violation(data: dict):
    now = int(time.time())
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO violations (officer_id, officer_svc, violator_id, violation_type, proof_link, punishment, staff_id, created_at)
            VALUES (:officer_id, :officer_svc, :violator_id, :violation_type, :proof_link, :punishment, :staff_id, :created_at)
        ''', {**data, 'created_at': now})

def get_violations(violator_id: str):
    with get_connection() as conn:
        cursor = conn.execute('SELECT * FROM violations WHERE violator_id = ? ORDER BY created_at DESC', (violator_id,))
        return cursor.fetchall()

def update_user_role(discord_id: str, new_role: str):
    now = int(time.time())
    with get_connection() as conn:
        conn.execute('''
            UPDATE users SET discord_role = ?, updated_at = ? WHERE discord_id = ?
        ''', (new_role, now, discord_id))

def generate_service_number() -> str | None:
    with get_connection() as conn:
        rows = conn.execute('SELECT service_number FROM users').fetchall()
        taken = {row['service_number'] for row in rows}
    
    available = []
    for i in range(1, 1000):
        padded = str(i).zfill(3)
        if padded not in taken:
            available.append(padded)
            
    if not available:
        return None
        
    return random.choice(available)
