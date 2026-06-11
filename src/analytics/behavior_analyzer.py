"""
Behavioral Analytics Module
Analyzes user behavior patterns from games and detection attempts
"""

import logging
try:
    import numpy as np
except ImportError:
    np = None
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import json

from src.utils.config import Config

logger = logging.getLogger(__name__)

class BehaviorAnalyzer:
    """Analyzes user behavior patterns for security insights"""
    
    def __init__(self):
        self.config = Config()
        self.user_behaviors = defaultdict(dict)
        self.behavior_patterns = {}
        
    def log_detection_attempt(self, user_id: str, content: str, result: Dict[str, Any]):
        """Log user detection attempt for behavior analysis"""
        try:
            if user_id not in self.user_behaviors:
                self.user_behaviors[user_id] = {
                    'detection_attempts': [],
                    'game_behaviors': [],
                    'response_patterns': [],
                    'risk_profile': {}
                }
            
            behavior_data = {
                'timestamp': datetime.now().isoformat(),
                'content_length': len(content),
                'is_phishing': result.get('is_phishing', False),
                'confidence_score': result.get('confidence_score', 0.0),
                'response_time_ms': result.get('response_time_ms', 0),
                'risk_factors': result.get('risk_factors', []),
                'user_decision': self._infer_user_decision(content, result)
            }
            
            self.user_behaviors[user_id]['detection_attempts'].append(behavior_data)
            
            # Update risk profile
            self._update_risk_profile(user_id, behavior_data)
            
        except Exception as e:
            logger.error(f"Error logging detection attempt: {str(e)}")
    
    def analyze_game_behavior(self, user_id: str, game_id: str, answer: Dict, result: Dict):
        """Analyze user behavior during games"""
        try:
            if user_id not in self.user_behaviors:
                self.user_behaviors[user_id] = {
                    'detection_attempts': [],
                    'game_behaviors': [],
                    'response_patterns': [],
                    'risk_profile': {}
                }
            
            game_behavior = {
                'timestamp': datetime.now().isoformat(),
                'game_id': game_id,
                'answer': answer,
                'correct': result.get('correct', False),
                'points_earned': result.get('points_earned', 0),
                'response_time': self._calculate_response_time(answer),
                'confidence_level': self._analyze_confidence(answer),
                'learning_pattern': self._analyze_learning_pattern(user_id, answer, result)
            }
            
            self.user_behaviors[user_id]['game_behaviors'].append(game_behavior)
            
            # Analyze response patterns
            self._analyze_response_patterns(user_id, game_behavior)
            
        except Exception as e:
            logger.error(f"Error analyzing game behavior: {str(e)}")
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user behavior statistics"""
        try:
            if user_id not in self.user_behaviors:
                return self._get_default_stats()
            
            user_data = self.user_behaviors[user_id]
            
            stats = {
                'detection_stats': self._analyze_detection_stats(user_data['detection_attempts']),
                'game_stats': self._analyze_game_stats(user_data['game_behaviors']),
                'response_patterns': self._analyze_response_patterns_summary(user_data['response_patterns']),
                'risk_profile': user_data.get('risk_profile', {}),
                'learning_progress': self._analyze_learning_progress(user_data['game_behaviors']),
                'behavioral_insights': self._generate_behavioral_insights(user_data)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return self._get_default_stats()
    
    def get_behavioral_insights(self, user_id: str) -> List[str]:
        """Get behavioral insights and recommendations"""
        try:
            if user_id not in self.user_behaviors:
                return ["No behavioral data available"]
            
            user_data = self.user_behaviors[user_id]
            insights = []
            
            # Detection accuracy insights
            detection_stats = self._analyze_detection_stats(user_data['detection_attempts'])
            if detection_stats['accuracy'] < 0.7:
                insights.append("Consider improving phishing detection skills through more training")
            
            # Response time insights
            if detection_stats['avg_response_time'] > 5000:  # 5 seconds
                insights.append("Response times are slow - practice quick decision making")
            
            # Learning pattern insights
            learning_progress = self._analyze_learning_progress(user_data['game_behaviors'])
            if learning_progress['improvement_rate'] < 0.1:
                insights.append("Learning progress is slow - try different game types")
            
            # Risk profile insights
            risk_profile = user_data.get('risk_profile', {})
            if risk_profile.get('high_risk_attempts', 0) > 5:
                insights.append("Multiple high-risk decisions detected - review security practices")
            
            return insights if insights else ["Behavior patterns look good - keep up the good work!"]
            
        except Exception as e:
            logger.error(f"Error getting behavioral insights: {str(e)}")
            return ["Unable to analyze behavior patterns"]
    
    def _infer_user_decision(self, content: str, result: Dict) -> str:
        """Infer user's decision based on content and result"""
        # This is a simplified inference - in practice, you'd have actual user decisions
        if result.get('is_phishing', False):
            return 'correctly_identified_phishing'
        else:
            return 'correctly_identified_legitimate'
    
    def _update_risk_profile(self, user_id: str, behavior_data: Dict):
        """Update user's risk profile"""
        try:
            user_data = self.user_behaviors[user_id]
            risk_profile = user_data.get('risk_profile', {})
            
            # Count high-risk attempts
            if behavior_data.get('confidence_score', 0) > 0.8 and behavior_data.get('is_phishing', False):
                risk_profile['high_risk_attempts'] = risk_profile.get('high_risk_attempts', 0) + 1
            
            # Track response times
            response_times = risk_profile.get('response_times', [])
            response_times.append(behavior_data.get('response_time_ms', 0))
            risk_profile['response_times'] = response_times[-100:]  # Keep last 100
            
            # Calculate average response time
            if response_times:
                risk_profile['avg_response_time'] = np.mean(response_times)
            
            # Track risk factors
            risk_factors = behavior_data.get('risk_factors', [])
            for factor in risk_factors:
                risk_profile['common_risk_factors'] = risk_profile.get('common_risk_factors', {})
                risk_profile['common_risk_factors'][factor] = risk_profile['common_risk_factors'].get(factor, 0) + 1
            
            user_data['risk_profile'] = risk_profile
            
        except Exception as e:
            logger.error(f"Error updating risk profile: {str(e)}")
    
    def _calculate_response_time(self, answer: Dict) -> float:
        """Calculate response time from answer data"""
        # This would be calculated from actual timing data
        return np.random.uniform(1.0, 10.0)  # Placeholder
    
    def _analyze_confidence(self, answer: Dict) -> str:
        """Analyze user's confidence level"""
        # This would analyze hesitation, changes, etc.
        return 'medium'  # Placeholder
    
    def _analyze_learning_pattern(self, user_id: str, answer: Dict, result: Dict) -> Dict:
        """Analyze learning patterns"""
        return {
            'pattern_type': 'consistent',
            'improvement_rate': 0.15,
            'difficulty_preference': 'medium'
        }
    
    def _analyze_response_patterns(self, user_id: str, game_behavior: Dict):
        """Analyze response patterns"""
        try:
            user_data = self.user_behaviors[user_id]
            patterns = user_data.get('response_patterns', [])
            
            pattern = {
                'timestamp': game_behavior['timestamp'],
                'response_time': game_behavior['response_time'],
                'confidence': game_behavior['confidence_level'],
                'correctness': game_behavior['correct']
            }
            
            patterns.append(pattern)
            user_data['response_patterns'] = patterns[-50:]  # Keep last 50
            
        except Exception as e:
            logger.error(f"Error analyzing response patterns: {str(e)}")
    
    def _analyze_detection_stats(self, detection_attempts: List[Dict]) -> Dict[str, Any]:
        """Analyze detection attempt statistics"""
        if not detection_attempts:
            return self._get_default_detection_stats()
        
        try:
            correct_attempts = sum(1 for attempt in detection_attempts 
                                 if attempt.get('user_decision', '').startswith('correctly'))
            
            accuracy = correct_attempts / len(detection_attempts)
            response_times = [attempt.get('response_time_ms', 0) for attempt in detection_attempts]
            
            return {
                'total_attempts': len(detection_attempts),
                'correct_attempts': correct_attempts,
                'accuracy': accuracy,
                'avg_response_time': np.mean(response_times) if response_times else 0,
                'min_response_time': np.min(response_times) if response_times else 0,
                'max_response_time': np.max(response_times) if response_times else 0,
                'phishing_detected': sum(1 for attempt in detection_attempts 
                                       if attempt.get('is_phishing', False)),
                'legitimate_identified': sum(1 for attempt in detection_attempts 
                                           if not attempt.get('is_phishing', False))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing detection stats: {str(e)}")
            return self._get_default_detection_stats()
    
    def _analyze_game_stats(self, game_behaviors: List[Dict]) -> Dict[str, Any]:
        """Analyze game behavior statistics"""
        if not game_behaviors:
            return self._get_default_game_stats()
        
        try:
            correct_answers = sum(1 for behavior in game_behaviors 
                                if behavior.get('correct', False))
            
            total_points = sum(behavior.get('points_earned', 0) for behavior in game_behaviors)
            response_times = [behavior.get('response_time', 0) for behavior in game_behaviors]
            
            return {
                'total_games': len(game_behaviors),
                'correct_answers': correct_answers,
                'accuracy': correct_answers / len(game_behaviors),
                'total_points': total_points,
                'avg_points_per_game': total_points / len(game_behaviors),
                'avg_response_time': np.mean(response_times) if response_times else 0,
                'learning_improvement': self._calculate_learning_improvement(game_behaviors)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing game stats: {str(e)}")
            return self._get_default_game_stats()
    
    def _analyze_response_patterns_summary(self, response_patterns: List[Dict]) -> Dict[str, Any]:
        """Analyze response patterns summary"""
        if not response_patterns:
            return self._get_default_response_patterns()
        
        try:
            response_times = [pattern.get('response_time', 0) for pattern in response_patterns]
            confidence_levels = [pattern.get('confidence', 'medium') for pattern in response_patterns]
            
            return {
                'avg_response_time': np.mean(response_times) if response_times else 0,
                'response_time_trend': self._calculate_trend(response_times),
                'confidence_distribution': self._calculate_confidence_distribution(confidence_levels),
                'consistency_score': self._calculate_consistency_score(response_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing response patterns: {str(e)}")
            return self._get_default_response_patterns()
    
    def _analyze_learning_progress(self, game_behaviors: List[Dict]) -> Dict[str, Any]:
        """Analyze learning progress over time"""
        if not game_behaviors:
            return self._get_default_learning_progress()
        
        try:
            # Sort by timestamp
            sorted_behaviors = sorted(game_behaviors, key=lambda x: x.get('timestamp', ''))
            
            # Calculate improvement rate
            if len(sorted_behaviors) >= 2:
                recent_accuracy = sum(1 for behavior in sorted_behaviors[-5:] 
                                    if behavior.get('correct', False)) / min(5, len(sorted_behaviors))
                early_accuracy = sum(1 for behavior in sorted_behaviors[:5] 
                                   if behavior.get('correct', False)) / min(5, len(sorted_behaviors))
                improvement_rate = recent_accuracy - early_accuracy
            else:
                improvement_rate = 0.0
            
            return {
                'improvement_rate': improvement_rate,
                'learning_curve': self._calculate_learning_curve(sorted_behaviors),
                'difficulty_preference': self._analyze_difficulty_preference(sorted_behaviors),
                'retention_rate': self._calculate_retention_rate(sorted_behaviors)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing learning progress: {str(e)}")
            return self._get_default_learning_progress()
    
    def _generate_behavioral_insights(self, user_data: Dict) -> List[str]:
        """Generate behavioral insights"""
        insights = []
        
        # Add insights based on patterns
        detection_stats = self._analyze_detection_stats(user_data['detection_attempts'])
        game_stats = self._analyze_game_stats(user_data['game_behaviors'])
        
        if detection_stats['accuracy'] > 0.9:
            insights.append("Excellent phishing detection skills")
        
        if game_stats['learning_improvement'] > 0.2:
            insights.append("Strong learning progress observed")
        
        if detection_stats['avg_response_time'] < 2000:
            insights.append("Fast decision-making skills")
        
        return insights
    
    def _calculate_learning_improvement(self, game_behaviors: List[Dict]) -> float:
        """Calculate learning improvement rate"""
        if len(game_behaviors) < 2:
            return 0.0
        
        # Simple improvement calculation
        return 0.15  # Placeholder
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend in values"""
        if len(values) < 2:
            return 'stable'
        
        # Simple trend calculation
        return 'improving'  # Placeholder
    
    def _calculate_confidence_distribution(self, confidence_levels: List[str]) -> Dict[str, int]:
        """Calculate confidence level distribution"""
        distribution = defaultdict(int)
        for level in confidence_levels:
            distribution[level] += 1
        return dict(distribution)
    
    def _calculate_consistency_score(self, response_patterns: List[Dict]) -> float:
        """Calculate consistency score"""
        if len(response_patterns) < 2:
            return 1.0
        
        # Simple consistency calculation
        return 0.8  # Placeholder
    
    def _calculate_learning_curve(self, sorted_behaviors: List[Dict]) -> str:
        """Calculate learning curve type"""
        return 'steady'  # Placeholder
    
    def _analyze_difficulty_preference(self, sorted_behaviors: List[Dict]) -> str:
        """Analyze difficulty preference"""
        return 'medium'  # Placeholder
    
    def _calculate_retention_rate(self, sorted_behaviors: List[Dict]) -> float:
        """Calculate knowledge retention rate"""
        return 0.85  # Placeholder
    
    def _get_default_stats(self) -> Dict[str, Any]:
        """Get default statistics"""
        return {
            'detection_stats': self._get_default_detection_stats(),
            'game_stats': self._get_default_game_stats(),
            'response_patterns': self._get_default_response_patterns(),
            'risk_profile': {},
            'learning_progress': self._get_default_learning_progress(),
            'behavioral_insights': ["No behavioral data available"]
        }
    
    def _get_default_detection_stats(self) -> Dict[str, Any]:
        """Get default detection statistics"""
        return {
            'total_attempts': 0,
            'correct_attempts': 0,
            'accuracy': 0.0,
            'avg_response_time': 0.0,
            'min_response_time': 0.0,
            'max_response_time': 0.0,
            'phishing_detected': 0,
            'legitimate_identified': 0
        }
    
    def _get_default_game_stats(self) -> Dict[str, Any]:
        """Get default game statistics"""
        return {
            'total_games': 0,
            'correct_answers': 0,
            'accuracy': 0.0,
            'total_points': 0,
            'avg_points_per_game': 0.0,
            'avg_response_time': 0.0,
            'learning_improvement': 0.0
        }
    
    def _get_default_response_patterns(self) -> Dict[str, Any]:
        """Get default response patterns"""
        return {
            'avg_response_time': 0.0,
            'response_time_trend': 'stable',
            'confidence_distribution': {},
            'consistency_score': 1.0
        }
    
    def _get_default_learning_progress(self) -> Dict[str, Any]:
        """Get default learning progress"""
        return {
            'improvement_rate': 0.0,
            'learning_curve': 'stable',
            'difficulty_preference': 'medium',
            'retention_rate': 1.0
        }
