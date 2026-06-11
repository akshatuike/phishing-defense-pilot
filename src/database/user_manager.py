"""
User Management and Database Operations
Handles user authentication, profiles, and data persistence
"""

import sqlite3
import logging
import bcrypt
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os

from src.utils.config import Config

logger = logging.getLogger(__name__)

class UserManager:
    """Manages user accounts and database operations"""
    
    def __init__(self):
        self.config = Config()
        self.db_path = "data/phishing_defense.db"
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
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
                
                # User sessions table
                cursor.execute('''
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
                
                # User progress table
                cursor.execute('''
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
                
                # Detection history table
                cursor.execute('''
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
                
                # Game sessions table
                cursor.execute('''
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
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> Dict[str, Any]:
        """Create a new user account"""
        try:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert user
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, role)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, password_hash.decode('utf-8'), role))
                
                user_id = cursor.lastrowid
                
                # Initialize user progress
                cursor.execute('''
                    INSERT INTO user_progress (user_id)
                    VALUES (?)
                ''', (user_id,))
                
                conn.commit()
                
                return {
                    'user_id': user_id,
                    'username': username,
                    'email': email,
                    'role': role,
                    'created_at': datetime.now().isoformat()
                }
                
        except sqlite3.IntegrityError:
            return {'error': 'Username or email already exists'}
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {'error': 'Failed to create user'}
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, password_hash, role, is_active
                    FROM users WHERE username = ?
                ''', (username,))
                
                user_data = cursor.fetchone()
                
                if not user_data:
                    return {'error': 'Invalid credentials'}
                
                user_id, username, email, password_hash, role, is_active = user_data
                
                if not is_active:
                    return {'error': 'Account is deactivated'}
                
                # Verify password
                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    # Update last login
                    cursor.execute('''
                        UPDATE users SET last_login = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (user_id,))
                    
                    conn.commit()
                    
                    return {
                        'user_id': user_id,
                        'username': username,
                        'email': email,
                        'role': role,
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user info
                cursor.execute('''
                    SELECT username, email, role, created_at, last_login, profile_data
                    FROM users WHERE id = ?
                ''', (user_id,))
                
                user_data = cursor.fetchone()
                if not user_data:
                    return {'error': 'User not found'}
                
                username, email, role, created_at, last_login, profile_data = user_data
                
                # Get user progress
                cursor.execute('''
                    SELECT total_points, games_played, games_won, current_streak, 
                           best_streak, level, achievements
                    FROM user_progress WHERE user_id = ?
                ''', (user_id,))
                
                progress_data = cursor.fetchone()
                
                return {
                    'user_id': user_id,
                    'username': username,
                    'email': email,
                    'role': role,
                    'created_at': created_at,
                    'last_login': last_login,
                    'profile_data': json.loads(profile_data) if profile_data else {},
                    'progress': {
                        'total_points': progress_data[0] if progress_data else 0,
                        'games_played': progress_data[1] if progress_data else 0,
                        'games_won': progress_data[2] if progress_data else 0,
                        'current_streak': progress_data[3] if progress_data else 0,
                        'best_streak': progress_data[4] if progress_data else 0,
                        'level': progress_data[5] if progress_data else 'beginner',
                        'achievements': json.loads(progress_data[6]) if progress_data and progress_data[6] else []
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return {'error': 'Failed to get user data'}
    
    def update_user_progress(self, user_id: int, progress_data: Dict[str, Any]):
        """Update user progress"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE user_progress 
                    SET total_points = ?, games_played = ?, games_won = ?,
                        current_streak = ?, best_streak = ?, level = ?,
                        achievements = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (
                    progress_data.get('total_points', 0),
                    progress_data.get('games_played', 0),
                    progress_data.get('games_won', 0),
                    progress_data.get('current_streak', 0),
                    progress_data.get('best_streak', 0),
                    progress_data.get('level', 'beginner'),
                    json.dumps(progress_data.get('achievements', [])),
                    user_id
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating user progress: {str(e)}")
    
    def log_detection(self, user_id: int, content: str, is_phishing: bool, 
                     confidence_score: float, response_time_ms: int):
        """Log detection attempt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO detection_history 
                    (user_id, content, is_phishing, confidence_score, response_time_ms)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, content, is_phishing, confidence_score, response_time_ms))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging detection: {str(e)}")
    
    def log_game_session(self, user_id: int, game_id: str, game_type: str, 
                        score: int = 0, answers: List[Dict] = None, completed: bool = False):
        """Log game session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO game_sessions 
                    (user_id, game_id, game_type, score, answers, completed)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, game_id, game_type, score,
                    json.dumps(answers) if answers else None, completed
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging game session: {str(e)}")
    
    def get_detection_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user's detection history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT content, is_phishing, confidence_score, response_time_ms, timestamp
                    FROM detection_history 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, limit))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'content': row[0],
                        'is_phishing': bool(row[1]),
                        'confidence_score': row[2],
                        'response_time_ms': row[3],
                        'timestamp': row[4]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Error getting detection history: {str(e)}")
            return []
    
    def get_game_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's game history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT game_type, score, completed, start_time, end_time
                    FROM game_sessions 
                    WHERE user_id = ?
                    ORDER BY start_time DESC
                    LIMIT ?
                ''', (user_id, limit))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'game_type': row[0],
                        'score': row[1],
                        'completed': bool(row[2]),
                        'start_time': row[3],
                        'end_time': row[4]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Error getting game history: {str(e)}")
            return []
    
    def get_total_users(self) -> int:
        """Get total number of users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting total users: {str(e)}")
            return 0
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get system-wide user statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total users
                cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
                total_users = cursor.fetchone()[0]
                
                # Active users (logged in last 30 days)
                thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE is_active = 1 AND last_login > ?
                ''', (thirty_days_ago,))
                active_users = cursor.fetchone()[0]
                
                # Total detections
                cursor.execute('SELECT COUNT(*) FROM detection_history')
                total_detections = cursor.fetchone()[0]
                
                # Total games played
                cursor.execute('SELECT COUNT(*) FROM game_sessions')
                total_games = cursor.fetchone()[0]
                
                return {
                    'total_users': total_users,
                    'active_users': active_users,
                    'total_detections': total_detections,
                    'total_games': total_games
                }
                
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {}
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user account (soft delete)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users SET is_active = 0 WHERE id = ?
                ''', (user_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        try:
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users SET password_hash = ? WHERE id = ?
                ''', (password_hash.decode('utf-8'), user_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return False
