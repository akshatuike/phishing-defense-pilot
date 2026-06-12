"""
User Management and Database Operations — PostgreSQL version
Handles user authentication, profiles, and data persistence

## PHASE1 / POSTGRES MIGRATION:
- Replaced sqlite3 with psycopg2
- AUTOINCREMENT -> SERIAL
- ? placeholders -> %s
- BOOLEAN handling is native in Postgres (no 0/1 conversion needed)
- Connection uses DATABASE_URL environment variable (set by Render)
- Falls back to SQLite locally if DATABASE_URL is not set (for local dev)
"""

import os
import logging
import bcrypt
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from src.utils.config import Config

logger = logging.getLogger(__name__)

# Detect environment: Postgres on Render, SQLite for local dev
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    import psycopg2
    import psycopg2.extras
    USE_POSTGRES = True
else:
    import sqlite3
    USE_POSTGRES = False


class UserManager:
    """Manages user accounts and database operations.
    Uses PostgreSQL if DATABASE_URL env var is set, else local SQLite."""

    def __init__(self):
        self.config = Config()
        self.db_path = "data/phishing_defense.db"   # used only for SQLite fallback
        self.use_postgres = USE_POSTGRES
        self.init_database()

    # ── Connection helper ────────────────────────────────────────────────────

    def _get_conn(self):
        if self.use_postgres:
            # Render's DATABASE_URL sometimes starts with postgres:// — psycopg2 wants postgresql://
            url = DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return psycopg2.connect(url)
        else:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            return sqlite3.connect(self.db_path)

    def _ph(self, n=1):
        """Return correct placeholder string(s) for the active DB."""
        ph = "%s" if self.use_postgres else "?"
        return ph if n == 1 else ", ".join([ph] * n)

    # ── Schema ────────────────────────────────────────────────────────────────

    def init_database(self):
        """Initialize database and create tables (Postgres or SQLite)"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()

            if self.use_postgres:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        role TEXT DEFAULT 'user',
                        profile_data TEXT
                    )
                ''')

                cur.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        session_token TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                ''')

                cur.execute('''
                    CREATE TABLE IF NOT EXISTS user_progress (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        total_points INTEGER DEFAULT 0,
                        games_played INTEGER DEFAULT 0,
                        games_won INTEGER DEFAULT 0,
                        current_streak INTEGER DEFAULT 0,
                        best_streak INTEGER DEFAULT 0,
                        level TEXT DEFAULT 'beginner',
                        achievements TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cur.execute('''
                    CREATE TABLE IF NOT EXISTS detection_history (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        content TEXT,
                        is_phishing BOOLEAN,
                        confidence_score REAL,
                        response_time_ms INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cur.execute('''
                    CREATE TABLE IF NOT EXISTS game_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        game_id TEXT UNIQUE NOT NULL,
                        game_type TEXT NOT NULL,
                        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP,
                        score INTEGER DEFAULT 0,
                        answers TEXT,
                        completed BOOLEAN DEFAULT FALSE
                    )
                ''')

            else:
                # SQLite schema (local dev fallback) — original syntax
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        role TEXT DEFAULT 'user',
                        profile_data TEXT
                    )
                ''')
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        session_token TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS user_progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        total_points INTEGER DEFAULT 0,
                        games_played INTEGER DEFAULT 0,
                        games_won INTEGER DEFAULT 0,
                        current_streak INTEGER DEFAULT 0,
                        best_streak INTEGER DEFAULT 0,
                        level TEXT DEFAULT 'beginner',
                        achievements TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS detection_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        content TEXT,
                        is_phishing BOOLEAN,
                        confidence_score REAL,
                        response_time_ms INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS game_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        game_id TEXT UNIQUE NOT NULL,
                        game_type TEXT NOT NULL,
                        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP,
                        score INTEGER DEFAULT 0,
                        answers TEXT,
                        completed BOOLEAN DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')

            conn.commit()
            cur.close()
            conn.close()
            logger.info(
                f"Database initialized successfully "
                f"({'PostgreSQL' if self.use_postgres else 'SQLite'})"
            )

        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    # ── User Management ──────────────────────────────────────────────────────

    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> Dict[str, Any]:
        """Create a new user account"""
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            conn = self._get_conn()
            cur = conn.cursor()

            if self.use_postgres:
                cur.execute(
                    "INSERT INTO users (username, email, password_hash, role) "
                    "VALUES (%s, %s, %s, %s) RETURNING id",
                    (username, email, password_hash.decode('utf-8'), role)
                )
                user_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO user_progress (user_id) VALUES (%s)",
                    (user_id,)
                )
            else:
                cur.execute(
                    "INSERT INTO users (username, email, password_hash, role) "
                    "VALUES (?, ?, ?, ?)",
                    (username, email, password_hash.decode('utf-8'), role)
                )
                user_id = cur.lastrowid
                cur.execute("INSERT INTO user_progress (user_id) VALUES (?)", (user_id,))

            conn.commit()
            cur.close()
            conn.close()

            return {
                'user_id':    user_id,
                'username':   username,
                'email':      email,
                'role':       role,
                'created_at': datetime.now().isoformat()
            }

        except (psycopg2.errors.UniqueViolation if USE_POSTGRES else Exception) as e:
            if self.use_postgres and 'duplicate key' in str(e).lower():
                return {'error': 'Username or email already exists'}
            if not self.use_postgres and isinstance(e, sqlite3.IntegrityError):
                return {'error': 'Username or email already exists'}
            logger.error(f"Error creating user: {str(e)}")
            return {'error': 'Failed to create user'}
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {'error': 'Failed to create user'}

    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph()

            cur.execute(
                f"SELECT id, username, email, password_hash, role, is_active "
                f"FROM users WHERE username = {ph}",
                (username,)
            )
            row = cur.fetchone()
            cur.close()
            conn.close()

            if not row:
                return {'error': 'Invalid credentials'}

            user_id, uname, email, password_hash, role, is_active = row

            if not is_active:
                return {'error': 'Account is deactivated'}

            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                conn = self._get_conn()
                cur = conn.cursor()
                cur.execute(
                    f"UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = {ph}",
                    (user_id,)
                )
                conn.commit()
                cur.close()
                conn.close()

                return {
                    'user_id':       user_id,
                    'username':      uname,
                    'email':         email,
                    'role':          role,
                    'authenticated': True
                }
            else:
                return {'error': 'Invalid credentials'}

        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return {'error': 'Authentication failed'}

    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get user profile and progress data"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph()

            cur.execute(
                f"SELECT username, email, role, created_at, last_login, profile_data "
                f"FROM users WHERE id = {ph}",
                (user_id,)
            )
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {'error': 'User not found'}

            username, email, role, created_at, last_login, profile_data = row

            cur.execute(
                f"SELECT total_points, games_played, games_won, current_streak, "
                f"best_streak, level, achievements FROM user_progress WHERE user_id = {ph}",
                (user_id,)
            )
            progress_row = cur.fetchone()
            cur.close()
            conn.close()

            return {
                'user_id':     user_id,
                'username':    username,
                'email':       email,
                'role':        role,
                'created_at':  str(created_at),
                'last_login':  str(last_login) if last_login else None,
                'profile_data': json.loads(profile_data) if profile_data else {},
                'progress': {
                    'total_points':   progress_row[0] if progress_row else 0,
                    'games_played':   progress_row[1] if progress_row else 0,
                    'games_won':      progress_row[2] if progress_row else 0,
                    'current_streak': progress_row[3] if progress_row else 0,
                    'best_streak':    progress_row[4] if progress_row else 0,
                    'level':          progress_row[5] if progress_row else 'beginner',
                    'achievements':   json.loads(progress_row[6]) if progress_row and progress_row[6] else []
                }
            }

        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return {'error': 'Failed to get user data'}

    def update_user_progress(self, user_id: int, progress_data: Dict[str, Any]):
        """Update user progress"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph()

            cur.execute(
                f"UPDATE user_progress SET total_points={ph}, games_played={ph}, "
                f"games_won={ph}, current_streak={ph}, best_streak={ph}, level={ph}, "
                f"achievements={ph}, last_updated=CURRENT_TIMESTAMP WHERE user_id={ph}",
                (
                    progress_data.get('total_points', 0),
                    progress_data.get('games_played', 0),
                    progress_data.get('games_won', 0),
                    progress_data.get('current_streak', 0),
                    progress_data.get('best_streak', 0),
                    progress_data.get('level', 'beginner'),
                    json.dumps(progress_data.get('achievements', [])),
                    user_id
                )
            )
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating user progress: {str(e)}")

    def log_detection(self, user_id: int, content: str, is_phishing: bool,
                       confidence_score: float, response_time_ms: int):
        """Log detection attempt"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph(5)

            cur.execute(
                f"INSERT INTO detection_history "
                f"(user_id, content, is_phishing, confidence_score, response_time_ms) "
                f"VALUES ({ph})",
                (user_id, content, is_phishing, confidence_score, response_time_ms)
            )
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error logging detection: {str(e)}")

    def log_game_session(self, user_id: int, game_id: str, game_type: str,
                          score: int = 0, answers: List[Dict] = None, completed: bool = False):
        """Log game session"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph(6)

            cur.execute(
                f"INSERT INTO game_sessions "
                f"(user_id, game_id, game_type, score, answers, completed) "
                f"VALUES ({ph})",
                (
                    user_id, game_id, game_type, score,
                    json.dumps(answers) if answers else None, completed
                )
            )
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            logger.error(f"Error logging game session: {str(e)}")

    def get_detection_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's detection history"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph(2)

            cur.execute(
                f"SELECT content, is_phishing, confidence_score, response_time_ms, timestamp "
                f"FROM detection_history WHERE user_id = {self._ph()} "
                f"ORDER BY timestamp DESC LIMIT {self._ph()}",
                (user_id, limit)
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()

            return [
                {
                    'content':          r[0],
                    'is_phishing':      bool(r[1]),
                    'confidence_score': r[2],
                    'response_time_ms': r[3],
                    'timestamp':        str(r[4])
                }
                for r in rows
            ]

        except Exception as e:
            logger.error(f"Error getting detection history: {str(e)}")
            return []

    def get_game_history(self, user_id, limit: int = 20) -> List[Dict]:
        """Get user's game history. user_id may be int (postgres) or str username."""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph()

            # Resolve username -> id if needed
            resolved_id = user_id
            if isinstance(user_id, str):
                cur.execute(f"SELECT id FROM users WHERE username = {ph}", (user_id,))
                row = cur.fetchone()
                resolved_id = row[0] if row else None

            if resolved_id is None:
                cur.close()
                conn.close()
                return []

            cur.execute(
                f"SELECT game_type, score, completed, start_time, end_time, answers "
                f"FROM game_sessions WHERE user_id = {ph} "
                f"ORDER BY start_time DESC LIMIT {self._ph()}",
                (resolved_id, limit)
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()

            return [
                {
                    'game_type': r[0],
                    'score':     r[1],
                    'completed': bool(r[2]),
                    'start_time': str(r[3]),
                    'end_time':   str(r[4]) if r[4] else None,
                    'answers':    json.loads(r[5]) if r[5] else []
                }
                for r in rows
            ]

        except Exception as e:
            logger.error(f"Error getting game history: {str(e)}")
            return []

    def get_total_users(self) -> int:
        """Get total number of users"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE" if self.use_postgres
                        else "SELECT COUNT(*) FROM users WHERE is_active = 1")
            n = cur.fetchone()[0]
            cur.close()
            conn.close()
            return n
        except Exception as e:
            logger.error(f"Error getting total users: {str(e)}")
            return 0

    def get_user_stats(self) -> Dict[str, Any]:
        """Get system-wide user statistics"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()

            active_clause = "TRUE" if self.use_postgres else "1"

            cur.execute(f"SELECT COUNT(*) FROM users WHERE is_active = {active_clause}")
            total_users = cur.fetchone()[0]

            thirty_days_ago = datetime.now() - timedelta(days=30)
            ph = self._ph()
            cur.execute(
                f"SELECT COUNT(*) FROM users WHERE is_active = {active_clause} "
                f"AND last_login > {ph}",
                (thirty_days_ago,)
            )
            active_users = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM detection_history")
            total_detections = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM game_sessions")
            total_games = cur.fetchone()[0]

            cur.close()
            conn.close()

            return {
                'total_users':      total_users,
                'active_users':     active_users,
                'total_detections': total_detections,
                'total_games':      total_games
            }

        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {}

    def delete_user(self, user_id: int) -> bool:
        """Soft-delete user account"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph()
            active_val = "FALSE" if self.use_postgres else "0"
            cur.execute(f"UPDATE users SET is_active = {active_val} WHERE id = {ph}", (user_id,))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False

    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        try:
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph()
            cur.execute(f"UPDATE users SET password_hash = {ph} WHERE id = {ph}",
                        (password_hash.decode('utf-8'), user_id))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return False

    # ── PILOT-SPECIFIC: profile_data helpers ─────────────────────────────────

    def get_profile_data(self, user_id: int) -> Dict[str, Any]:
        """Get profile_data JSON for a user (used by pilot routes)"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph()
            cur.execute(f"SELECT profile_data FROM users WHERE id = {ph}", (user_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row and row[0]:
                return json.loads(row[0])
            return {}
        except Exception as e:
            logger.error(f"Error getting profile data: {str(e)}")
            return {}

    def update_profile_data(self, user_id: int, profile: Dict[str, Any]):
        """Update profile_data JSON for a user (used by pilot routes)"""
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            ph = self._ph()
            cur.execute(
                f"UPDATE users SET profile_data = {ph} WHERE id = {ph}",
                (json.dumps(profile), user_id)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error updating profile data: {str(e)}")

    def get_all_participants(self) -> List[Dict]:
        """
        Get all participant data with pre/post test scores joined.
        Used by /admin/export_pilot route.
        """
        try:
            conn = self._get_conn()
            cur = conn.cursor()

            cur.execute("""
                SELECT u.id, u.username, u.profile_data
                FROM users u
                WHERE u.role = 'participant'
                ORDER BY u.id
            """)
            users = cur.fetchall()

            result = []
            ph = self._ph()
            for uid, uname, profile_raw in users:
                profile = json.loads(profile_raw) if profile_raw else {}

                cur.execute(
                    f"SELECT score, answers FROM game_sessions "
                    f"WHERE user_id={ph} AND game_type='pre_assessment' "
                    f"ORDER BY start_time DESC LIMIT 1", (uid,)
                )
                pre = cur.fetchone()

                cur.execute(
                    f"SELECT score, answers FROM game_sessions "
                    f"WHERE user_id={ph} AND game_type='post_assessment' "
                    f"ORDER BY start_time DESC LIMIT 1", (uid,)
                )
                post = cur.fetchone()

                result.append({
                    'user_id':  uid,
                    'username': uname,
                    'profile':  profile,
                    'pre_score':  pre[0] if pre else None,
                    'pre_answers': json.loads(pre[1]) if pre and pre[1] else None,
                    'post_score': post[0] if post else None,
                    'post_answers': json.loads(post[1]) if post and post[1] else None,
                })

            cur.close()
            conn.close()
            return result

        except Exception as e:
            logger.error(f"Error getting all participants: {str(e)}")
            return []
