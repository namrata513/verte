-- 1. Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    avatar TEXT NOT NULL,
    total_xp INTEGER DEFAULT 0,
    is_guest BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Daily Goals & Streaks
CREATE TABLE IF NOT EXISTS user_progress (
    user_id INTEGER PRIMARY KEY,
    current_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    daily_goal_completed_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Environmental Impact Metrics
CREATE TABLE IF NOT EXISTS user_stats (
    user_id INTEGER PRIMARY KEY,
    total_items_sorted INTEGER DEFAULT 0,
    total_weight_diverted_kg REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Scans & Activity Log
CREATE TABLE IF NOT EXISTS scan_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_name TEXT,
    xp_earned INTEGER DEFAULT 10,
    guessed_category TEXT,
    is_correct BOOLEAN,
    scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for Dashboard Performance
CREATE INDEX IF NOT EXISTS idx_leaderboard ON users(total_xp DESC);
CREATE INDEX IF NOT EXISTS idx_user_activity ON scan_activity(user_id, scanned_at);