"""
Gamification Engine for the Phishing Defense System
Manages interactive games, user progress, and behavioral analytics

PHASE 1 PILOT STUDY CHANGES (see ## PHASE1 comments):
  1. submit_answer() — records submitted_at timestamp + time_taken_ms per answer
  2. _load_game_data() — expanded to 10 scenarios (was 5) to support assessment
  3. get_assessment_questions() — NEW: fixed 10-question set for pre/post test
  4. _get_game_challenges() — uses fixed order for assessment, random for free play
  5. submit_answer() — normalises 'whaling' answer to 'phishing' for assessment
  6. _complete_game() — records end_time correctly before calling achievements
  7. Hints expanded to cover all 10 assessment scenarios
"""

import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import random

from src.utils.config import Config

logger = logging.getLogger(__name__)


@dataclass
class GameSession:
    """Represents a game session"""
    game_id: str
    user_id: str
    game_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    score: int = 0
    answers: List[Dict] = field(default_factory=list)   # ## PHASE1: was None — caused NoneType errors
    completed: bool = False


@dataclass
class Achievement:
    """Represents a user achievement"""
    achievement_id: str
    name: str
    description: str
    icon: str
    points: int
    unlocked_at: Optional[datetime] = None


class GameEngine:
    """Main game engine for managing gamification elements"""

    def __init__(self):
        self.config = Config()
        self.active_sessions: Dict[str, GameSession] = {}
        self.user_progress: Dict[str, Dict] = {}
        self.achievements: Dict[str, Achievement] = self._load_achievements()
        self.game_data = self._load_game_data()

    # ── Achievements ─────────────────────────────────────────────────────────

    def _load_achievements(self) -> Dict[str, Achievement]:
        """Load predefined achievements"""
        return {
            "first_game": Achievement(
                "first_game", "First Steps",
                "Complete your first security game", "🎯", 10
            ),
            "perfect_score": Achievement(
                "perfect_score", "Perfect Score",
                "Get 100% on any game", "⭐", 25
            ),
            "streak_5": Achievement(
                "streak_5", "Hot Streak",
                "Win 5 games in a row", "🔥", 50
            ),
            "detection_master": Achievement(
                "detection_master", "Detection Master",
                "Correctly identify 50 phishing attempts", "🛡️", 100
            ),
            "speed_demon": Achievement(
                "speed_demon", "Speed Demon",
                "Complete a game in under 30 seconds", "⚡", 30
            )
        }

    # ── Game Data ─────────────────────────────────────────────────────────────

    def _load_game_data(self) -> Dict[str, List[Dict]]:
        """
        Load game scenarios and challenges.
        ## PHASE1: Expanded from 5 to 10 scenarios so get_assessment_questions()
        can return a full 10-question fixed set for pre/post test.
        """
        return {
            "phishing_challenge": [
                # ── existing scenarios ────────────────────────────────────────
                {
                    "id": "phish_001",
                    "type": "email",
                    "content": {
                        "subject": "URGENT: Your account has been suspended",
                        "sender": "security@paypa1.com",
                        "body": "Dear valued customer, your account has been suspended "
                                "due to suspicious activity. Click here to verify your "
                                "identity immediately: http://paypa1-verify.com/login",
                        "timestamp": "2026-01-15 10:30:00"
                    },
                    "correct_answer": "phishing",
                    "explanation": (
                        "Phishing indicators: 1) Urgency creates pressure, "
                        "2) Sender domain is misspelled (paypa1 instead of paypal), "
                        "3) Suspicious link asks for login credentials."
                    ),
                    "difficulty": "easy"
                },
                {
                    "id": "phish_002",
                    "type": "email",
                    "content": {
                        "subject": "Invoice #INV-2024-001 attached",
                        "sender": "billing@microsoft-support.com",
                        "body": "Please find attached invoice for your recent purchase. "
                                "If you have any questions, please contact us immediately.",
                        "timestamp": "2026-01-15 14:22:00"
                    },
                    "correct_answer": "phishing",
                    "explanation": (
                        "Phishing indicators: 1) microsoft-support.com is not microsoft.com, "
                        "2) Generic billing reference with no order number, "
                        "3) Urgency without specific details."
                    ),
                    "difficulty": "medium"
                },
                {
                    "id": "legit_001",
                    "type": "email",
                    "content": {
                        "subject": "Your order #12345 has shipped",
                        "sender": "noreply@amazon.com",
                        "body": "Your recent order has been shipped and is expected to "
                                "arrive on January 20th. Track your package: "
                                "https://amazon.com/track/12345",
                        "timestamp": "2026-01-15 09:15:00"
                    },
                    "correct_answer": "legitimate",
                    "explanation": (
                        "Legitimate because: 1) Official amazon.com domain, "
                        "2) Specific order number provided, "
                        "3) No urgent action required, tracking link uses official domain."
                    ),
                    "difficulty": "easy"
                },
                # ── ## PHASE1: NEW scenarios ──────────────────────────────────
                {
                    "id": "phish_003",
                    "type": "email",
                    "content": {
                        "subject": "Your Netflix account will be suspended",
                        "sender": "billing@netf1ix-support.com",
                        "body": "We were unable to process your payment. Update your "
                                "billing info within 24 hours to avoid suspension: "
                                "http://netf1ix-account.com/update",
                        "timestamp": "2026-02-10 08:15:00"
                    },
                    "correct_answer": "phishing",
                    "explanation": (
                        "Phishing indicators: 1) Domain uses digit '1' instead of letter 'l' "
                        "(netf1ix vs netflix) — classic homograph attack, "
                        "2) 24-hour deadline creates urgency, "
                        "3) Link does not go to netflix.com."
                    ),
                    "difficulty": "medium"
                },
                {
                    "id": "legit_002",
                    "type": "email",
                    "content": {
                        "subject": "Your GitHub pull request was merged",
                        "sender": "noreply@github.com",
                        "body": "Your pull request #247 'Fix login bug' in "
                                "akshat/phishing-defense was merged by admin. "
                                "View it at https://github.com/akshat/phishing-defense/pull/247",
                        "timestamp": "2026-02-10 11:30:00"
                    },
                    "correct_answer": "legitimate",
                    "explanation": (
                        "Legitimate because: 1) Official github.com sender and link domain, "
                        "2) Specific pull request number and title, "
                        "3) No credentials requested, no urgency."
                    ),
                    "difficulty": "easy"
                },
                {
                    "id": "phish_004",
                    "type": "email",
                    "content": {
                        "subject": "Action Required: Verify your SBI account",
                        "sender": "support@sbi-online-secure.net",
                        "body": "Dear Customer, your account has been flagged for unusual "
                                "activity. Login immediately to avoid account freeze: "
                                "http://sbi-secure-login.net/verify",
                        "timestamp": "2026-02-11 09:45:00"
                    },
                    "correct_answer": "phishing",
                    "explanation": (
                        "Phishing indicators: 1) SBI's real domain is onlinesbi.sbi — "
                        ".net domains are never used by SBI, "
                        "2) 'Account freeze' threat creates fear, "
                        "3) Link uses a spoofed domain unrelated to SBI."
                    ),
                    "difficulty": "medium"
                },
                {
                    "id": "legit_003",
                    "type": "email",
                    "content": {
                        "subject": "Zoom meeting recording available",
                        "sender": "no-reply@zoom.us",
                        "body": "The recording of your Feb 10 team meeting is now available. "
                                "View it at: https://zoom.us/rec/share/ABC123XYZ. "
                                "This link will expire in 30 days.",
                        "timestamp": "2026-02-10 16:00:00"
                    },
                    "correct_answer": "legitimate",
                    "explanation": (
                        "Legitimate because: 1) Official zoom.us sender and link domain, "
                        "2) Specific meeting reference, "
                        "3) No login credentials requested, expiry is normal Zoom behaviour."
                    ),
                    "difficulty": "easy"
                },
            ],
            "whaling_challenge": [
                {
                    "id": "whale_001",
                    "type": "email",
                    "content": {
                        "subject": "Confidential: Company Acquisition",
                        "sender": "ceo@company-acquisition.com",
                        "body": "As CEO, I need you to wire $50,000 immediately for a "
                                "confidential business opportunity. This is urgent and "
                                "confidential. Reply only to this email.",
                        "timestamp": "2026-01-15 16:45:00"
                    },
                    "correct_answer": "phishing",       # ## PHASE1: was "whaling" — normalised
                    "explanation": (
                        "Whaling / BEC attack: 1) Claims to be from CEO but uses external domain, "
                        "2) Requests large wire transfer with no verification process, "
                        "3) Emphasises secrecy to prevent the target from consulting colleagues."
                    ),
                    "difficulty": "hard"
                },
                # ── ## PHASE1: NEW whaling scenario ──────────────────────────
                {
                    "id": "whale_002",
                    "type": "email",
                    "content": {
                        "subject": "HR: Urgent payroll update needed",
                        "sender": "hr-payroll@company-hrportal.com",
                        "body": "We are updating payroll records before month-end. "
                                "Please reply with your bank account number and IFSC code "
                                "to ensure salary is credited correctly. Deadline: today 5 PM.",
                        "timestamp": "2026-03-01 14:00:00"
                    },
                    "correct_answer": "phishing",
                    "explanation": (
                        "Spear phishing / payroll fraud: 1) HR will never ask for bank details "
                        "via email — this information is already on file, "
                        "2) Artificial deadline prevents careful thinking, "
                        "3) External domain (company-hrportal.com) is not your organisation's domain."
                    ),
                    "difficulty": "hard"
                },
            ],
            "url_analysis": [
                {
                    "id": "url_001",
                    "type": "url",
                    "content": {
                        "url": "https://www.paypa1-secure.com/login",
                        "display_text": "PayPal Secure Login"
                    },
                    "correct_answer": "phishing",
                    "explanation": (
                        "Phishing URL: 1) Domain uses digit '1' instead of letter 'l' "
                        "(paypa1 vs paypal), "
                        "2) Real PayPal always uses paypal.com — never a hyphenated variant."
                    ),
                    "difficulty": "easy"
                },
                # ── ## PHASE1: NEW URL scenarios ─────────────────────────────
                {
                    "id": "url_002",
                    "type": "url",
                    "content": {
                        "url": "http://www.amazon-security-alert.com/signin",
                        "display_text": "Amazon Sign In"
                    },
                    "correct_answer": "phishing",
                    "explanation": (
                        "Phishing URL: 1) amazon-security-alert.com is not amazon.com — "
                        "Amazon only uses amazon.com (or country variants like amazon.in), "
                        "2) Uses HTTP not HTTPS, "
                        "3) Subdomain structure with 'security-alert' is a common scare tactic."
                    ),
                    "difficulty": "easy"
                },
                {
                    "id": "url_003",
                    "type": "url",
                    "content": {
                        "url": "https://www.google.com/accounts/signin?continue=mail",
                        "display_text": "Google Account Sign In"
                    },
                    "correct_answer": "legitimate",
                    "explanation": (
                        "Legitimate URL: 1) Domain is exactly google.com — no misspellings, "
                        "2) Uses HTTPS, "
                        "3) /accounts/signin is Google's real authentication path, "
                        "4) continue= parameter is standard Google OAuth behaviour."
                    ),
                    "difficulty": "medium"
                },
            ]
        }

    # ── Public API ────────────────────────────────────────────────────────────

    def start_game(self, user_id: str, game_type: str) -> Dict[str, Any]:
        """Start a new game session"""
        try:
            if not self._can_start_game(user_id):
                return {"error": "Daily game limit reached"}

            game_id = str(uuid.uuid4())
            session = GameSession(
                game_id=game_id,
                user_id=user_id,
                game_type=game_type,
                start_time=datetime.now()
                # answers defaults to [] via field(default_factory=list)
            )

            self.active_sessions[game_id] = session
            challenges = self._get_game_challenges(game_type)

            return {
                "game_id":    game_id,
                "game_type":  game_type,
                "challenges": challenges,
                "start_time": session.start_time.isoformat(),
                "max_score":  len(challenges) * self.config.get(
                    "gamification.points_per_correct_answer", 10)
            }

        except Exception as e:
            logger.error(f"Error starting game: {str(e)}")
            return {"error": "Failed to start game"}

    def submit_answer(self, game_id: str, user_id: str, answer: Dict) -> Dict[str, Any]:
        """
        Submit an answer for a game challenge.
        ## PHASE1: Records submitted_at and time_taken_ms on every answer
        so behavior_analyzer has real timing data.
        """
        try:
            if game_id not in self.active_sessions:
                return {"error": "Invalid game session"}

            session = self.active_sessions[game_id]
            if session.user_id != user_id:
                return {"error": "Unauthorized"}

            challenge_id = answer.get("challenge_id")
            user_answer  = answer.get("answer")

            # ## PHASE1: Normalise 'whaling' to 'phishing' for scoring purposes.
            # All whaling scenarios now use correct_answer="phishing" in game_data,
            # but if client sends "whaling" we treat it as correct for whaling questions.
            correct_answer = self._get_correct_answer(challenge_id)
            if correct_answer == "phishing" and user_answer == "whaling":
                user_answer = "phishing"

            is_correct   = user_answer == correct_answer
            points_earned = (
                self.config.get("gamification.points_per_correct_answer", 10)
                if is_correct else 0
            )

            # ## PHASE1: Stamp each answer with server-side timestamp and
            # client-supplied time_taken_ms (milliseconds user spent on this question).
            stamped_answer = {
                **answer,
                "user_answer":   user_answer,
                "correct":       is_correct,
                "points_earned": points_earned,
                "submitted_at":  datetime.now().isoformat(),
                "time_taken_ms": answer.get("time_taken_ms", 0)
            }
            session.answers.append(stamped_answer)
            session.score += points_earned

            # Check completion — use stored challenge count, not a fresh random sample
            total_challenges = self._get_total_challenges(session.game_type)
            if len(session.answers) >= total_challenges:
                session.completed = True
                session.end_time  = datetime.now()   # ## PHASE1: was set AFTER _complete_game
                self._complete_game(session)

            return {
                "correct":        is_correct,
                "points_earned":  points_earned,
                "total_score":    session.score,
                "explanation":    self._get_explanation(challenge_id),
                "game_completed": session.completed
            }

        except Exception as e:
            logger.error(f"Error submitting answer: {str(e)}")
            return {"error": "Failed to submit answer"}

    # ## PHASE1: NEW METHOD ───────────────────────────────────────────────────

    def get_assessment_questions(self) -> List[Dict]:
        """
        Return a FIXED ordered list of 10 questions for the pilot study
        pre-test (Session 1) and post-test (Session 2).

        Rules:
        - Same 10 questions, same order, both sessions (required for paired t-test).
        - Do NOT call random.sample on this list.
        - Covers email phishing (easy + medium), whaling/BEC (hard), and URL analysis.
        - correct_answer is always 'phishing' or 'legitimate' (never 'whaling')
          so the assessment scoring is binary and consistent.
        """
        fixed_ids = [
            "phish_001",   # Q1  — email, easy   (misspelled domain)
            "legit_001",   # Q2  — email, easy   (real Amazon)
            "url_001",     # Q3  — url,   easy   (paypa1)
            "phish_002",   # Q4  — email, medium (fake Microsoft support)
            "legit_002",   # Q5  — email, easy   (real GitHub)
            "phish_003",   # Q6  — email, medium (Netflix homograph)
            "url_002",     # Q7  — url,   easy   (amazon-security-alert)
            "whale_001",   # Q8  — email, hard   (CEO wire transfer)
            "legit_003",   # Q9  — email, easy   (real Zoom)
            "phish_004",   # Q10 — email, medium (fake SBI)
        ]

        # Build lookup from all game data
        all_questions: Dict[str, Dict] = {}
        for scenarios in self.game_data.values():
            for q in scenarios:
                all_questions[q["id"]] = q

        ordered = []
        for qid in fixed_ids:
            if qid in all_questions:
                ordered.append(all_questions[qid])
            else:
                logger.warning(f"Assessment question {qid} not found in game_data")

        return ordered

    # ── Progress & Achievements ───────────────────────────────────────────────

    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's learning progress"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                "total_points":  0,
                "games_played":  0,
                "games_won":     0,
                "current_streak": 0,
                "best_streak":   0,
                "achievements":  [],
                "level":         "beginner",
                "daily_games":   {}
            }

        progress = self.user_progress[user_id].copy()
        progress["level"]            = self._calculate_level(progress["total_points"])
        progress["next_level_points"] = self._get_next_level_points(progress["level"])
        return progress

    def get_user_achievements(self, user_id: str) -> List[Dict]:
        """Get user's unlocked achievements"""
        if user_id not in self.user_progress:
            return []
        return self.user_progress[user_id].get("achievements", [])

    def get_available_games(self, user_id: str) -> List[Dict]:
        """Get available games for user"""
        progress = self.get_user_progress(user_id)
        level    = progress["level"]

        available = [
            {
                "id":             "phishing_challenge",
                "name":           "Phishing Detection Challenge",
                "description":    "Learn to identify phishing emails",
                "difficulty":     "Easy",
                "estimated_time": "5-10 minutes",
                "points_possible": 70
            }
        ]

        if level in ["intermediate", "expert", "master"]:
            available.append({
                "id":             "whaling_challenge",
                "name":           "Whaling Attack Detection",
                "description":    "Advanced: Detect CEO fraud and business email compromise",
                "difficulty":     "Hard",
                "estimated_time": "10-15 minutes",
                "points_possible": 100
            })

        if level in ["expert", "master"]:
            available.append({
                "id":             "url_analysis",
                "name":           "URL Analysis Expert",
                "description":    "Master URL-based phishing detection",
                "difficulty":     "Expert",
                "estimated_time": "8-12 minutes",
                "points_possible": 75
            })

        return available

    def get_active_games_count(self) -> int:
        """Get count of active game sessions"""
        return len(self.active_sessions)

    def process_real_time_action(self, user_id: str, action_type: str,
                                  action_data: Dict) -> Dict:
        """Process real-time game actions"""
        try:
            if action_type == "hint_request":
                return self._provide_hint(action_data.get("challenge_id"))
            elif action_type == "time_update":
                return self._update_timer(
                    action_data.get("game_id"),
                    action_data.get("time_remaining")
                )
            else:
                return {"error": "Unknown action type"}
        except Exception as e:
            logger.error(f"Error processing real-time action: {str(e)}")
            return {"error": "Action failed"}

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _can_start_game(self, user_id: str) -> bool:
        """Check if user can start a new game"""
        today       = datetime.now().date()
        daily_games = self.user_progress.get(user_id, {}).get("daily_games", {})
        if str(today) not in daily_games:
            return True
        max_daily = self.config.get("gamification.max_daily_games", 10)
        return daily_games[str(today)] < max_daily

    def _get_game_challenges(self, game_type: str) -> List[Dict]:
        """
        Get challenges for free-play games (randomised order).
        ## PHASE1: Assessment uses get_assessment_questions() instead — do NOT
        call this method for pre/post test routes.
        """
        challenges = self.game_data.get(game_type, [])
        return random.sample(challenges, min(len(challenges), 5))

    def _get_total_challenges(self, game_type: str) -> int:
        """
        ## PHASE1: Returns total challenges for a game type without re-sampling.
        Used in submit_answer() to detect completion reliably.
        """
        if game_type in ("pre_assessment", "post_assessment"):
            return len(self.get_assessment_questions())
        return min(len(self.game_data.get(game_type, [])), 5)

    def _get_correct_answer(self, challenge_id: str) -> str:
        """Get correct answer for a challenge"""
        for scenarios in self.game_data.values():
            for challenge in scenarios:
                if challenge["id"] == challenge_id:
                    return challenge["correct_answer"]
        return "unknown"

    def _get_explanation(self, challenge_id: str) -> str:
        """Get explanation for a challenge"""
        for scenarios in self.game_data.values():
            for challenge in scenarios:
                if challenge["id"] == challenge_id:
                    return challenge["explanation"]
        return "No explanation available"

    def _complete_game(self, session: GameSession):
        """Complete a game session and update user progress"""
        user_id = session.user_id

        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                "total_points":   0,
                "games_played":   0,
                "games_won":      0,
                "current_streak": 0,
                "best_streak":    0,
                "achievements":   [],
                "daily_games":    {}
            }

        progress = self.user_progress[user_id]
        progress["total_points"] += session.score
        progress["games_played"] += 1

        points_per_q = self.config.get("gamification.points_per_correct_answer", 10)
        max_possible = len(session.answers) * points_per_q

        if max_possible > 0 and session.score >= max_possible * 0.8:
            progress["games_won"]      += 1
            progress["current_streak"] += 1
            progress["best_streak"]     = max(
                progress["best_streak"], progress["current_streak"]
            )
        else:
            progress["current_streak"] = 0

        today = datetime.now().date()
        progress["daily_games"].setdefault(str(today), 0)
        progress["daily_games"][str(today)] += 1

        # ## PHASE1: end_time is already set before _complete_game is called
        self._check_achievements(user_id, session)
        self._cleanup_old_records(progress)

    def _check_achievements(self, user_id: str, session: GameSession):
        """Check and award achievements"""
        progress     = self.user_progress[user_id]
        unlocked_ids = [a["id"] for a in progress["achievements"]]

        if progress["games_played"] == 1 and "first_game" not in unlocked_ids:
            self._award_achievement(user_id, "first_game")

        points_per_q = self.config.get("gamification.points_per_correct_answer", 10)
        max_possible = len(session.answers) * points_per_q
        if max_possible > 0 and session.score == max_possible \
                and "perfect_score" not in unlocked_ids:
            self._award_achievement(user_id, "perfect_score")

        if progress["current_streak"] >= 5 and "streak_5" not in unlocked_ids:
            self._award_achievement(user_id, "streak_5")

        if session.end_time and session.start_time:
            duration = (session.end_time - session.start_time).total_seconds()
            if duration <= 30 and "speed_demon" not in unlocked_ids:
                self._award_achievement(user_id, "speed_demon")

    def _award_achievement(self, user_id: str, achievement_id: str):
        """Award an achievement to a user"""
        if achievement_id not in self.achievements:
            return
        achievement             = self.achievements[achievement_id]
        achievement.unlocked_at = datetime.now()
        self.user_progress[user_id]["achievements"].append({
            "id":          achievement_id,
            "name":        achievement.name,
            "description": achievement.description,
            "icon":        achievement.icon,
            "points":      achievement.points,
            "unlocked_at": achievement.unlocked_at.isoformat()
        })
        self.user_progress[user_id]["total_points"] += achievement.points

    def _calculate_level(self, total_points: int) -> str:
        """Calculate user level based on total points"""
        t = self.config.get("gamification.achievement_thresholds", {})
        if total_points >= t.get("master", 500):
            return "master"
        elif total_points >= t.get("expert", 300):
            return "expert"
        elif total_points >= t.get("intermediate", 150):
            return "intermediate"
        return "beginner"

    def _get_next_level_points(self, current_level: str) -> int:
        """Get points needed for next level"""
        t = self.config.get("gamification.achievement_thresholds", {})
        return {
            "beginner":     t.get("intermediate", 150),
            "intermediate": t.get("expert", 300),
            "expert":       t.get("master", 500),
            "master":       0
        }.get(current_level, 0)

    def _cleanup_old_records(self, progress: Dict):
        """Remove daily game records older than 30 days"""
        cutoff      = datetime.now().date() - timedelta(days=30)
        daily_games = progress.get("daily_games", {})
        stale = [
            d for d in daily_games
            if self._parse_date(d) < cutoff
        ]
        for key in stale:
            del daily_games[key]

    def _parse_date(self, date_str: str):
        """Safely parse date string, return epoch on failure"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return datetime(1970, 1, 1).date()

    # ## PHASE1: Hints expanded to cover all 10 assessment questions ──────────

    def _provide_hint(self, challenge_id: str) -> Dict:
        """Provide a hint for a challenge (costs 5 points)"""
        hints = {
            "phish_001": "Look very carefully at the sender's email address — "
                         "compare each character with the real company name.",
            "phish_002": "Is 'microsoft-support.com' the same as 'microsoft.com'?",
            "phish_003": "Look at every character in the domain name. "
                         "Is that the letter 'l' or the digit '1'?",
            "phish_004": "What is SBI's real website domain? "
                         "Check whether .net is normal for a major Indian bank.",
            "legit_001": "Check: does the link actually go to amazon.com?",
            "legit_002": "Check: does the link go to github.com?",
            "legit_003": "Check: does the link go to zoom.us?",
            "whale_001": "Why would a CEO use a personal/external email for "
                         "a company wire transfer? What verification exists?",
            "whale_002": "Would HR really ask for your bank details by email "
                         "if they already process your salary every month?",
            "url_001":   "Compare the domain character by character with 'paypal.com'. "
                         "Is every letter exactly right?",
            "url_002":   "Amazon's real domain is amazon.com. "
                         "Is 'amazon-security-alert.com' the same thing?",
            "url_003":   "What is Google's real domain? Does this URL match it exactly?"
        }
        return {
            "hint": hints.get(challenge_id, "Look for suspicious patterns in the "
                                             "sender, domain, links, and urgency language."),
            "cost": 5
        }

    def _update_timer(self, game_id: str, time_remaining: int) -> Dict:
        """Update game timer"""
        if game_id in self.active_sessions:
            return {"time_remaining": time_remaining}
        return {"error": "Invalid game session"}
