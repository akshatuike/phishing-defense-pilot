#!/usr/bin/env python3
"""
Test script for the Gamification-Based Phishing Defense System
"""

import sys
import os
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import Config
from src.gamification.game_engine import GameEngine
from src.detection.phishing_detector import PhishingDetector
from src.database.user_manager import UserManager
from src.analytics.behavior_analyzer import BehaviorAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config():
    """Test configuration management"""
    logger.info("Testing configuration...")
    
    config = Config()
    
    # Test basic config access
    db_url = config.get('database.url')
    assert db_url is not None, "Database URL should be configured"
    
    # Test model paths
    model_path = config.get_model_path('bert-base-uncased')
    assert 'models' in model_path, "Model path should include models directory"
    
    logger.info("✅ Configuration test passed")

def test_game_engine():
    """Test gamification engine"""
    logger.info("Testing game engine...")
    
    game_engine = GameEngine()
    
    # Test game data loading
    assert len(game_engine.game_data) > 0, "Game data should be loaded"
    
    # Test available games
    games = game_engine.get_available_games("test_user")
    assert len(games) > 0, "Should have available games"
    
    # Test game session creation
    session = game_engine.start_game("test_user", "phishing_challenge")
    assert 'game_id' in session, "Game session should have game_id"
    
    logger.info("✅ Game engine test passed")

def test_phishing_detector():
    """Test phishing detection"""
    logger.info("Testing phishing detector...")
    
    detector = PhishingDetector()
    
    # Test phishing detection
    test_content = "URGENT: Your account has been suspended. Click here to verify: http://paypa1-verify.com"
    result = detector.detect(test_content, "test_user")
    
    assert 'is_phishing' in result, "Detection result should include is_phishing"
    assert 'confidence_score' in result, "Detection result should include confidence_score"
    
    logger.info("✅ Phishing detector test passed")

def test_user_manager():
    """Test user management"""
    logger.info("Testing user manager...")
    
    user_manager = UserManager()
    
    # Test user creation
    user_result = user_manager.create_user(
        username="test_user",
        email="test@example.com",
        password="test123"
    )
    
    if 'error' not in user_result:
        user_id = user_result['user_id']
        
        # Test user data retrieval
        user_data = user_manager.get_user_data(user_id)
        assert 'username' in user_data, "User data should include username"
        
        logger.info("✅ User manager test passed")
    else:
        logger.warning("⚠️ User creation failed (may already exist)")

def test_behavior_analyzer():
    """Test behavioral analytics"""
    logger.info("Testing behavior analyzer...")
    
    analyzer = BehaviorAnalyzer()
    
    # Test behavior logging
    test_result = {
        'is_phishing': True,
        'confidence_score': 0.85,
        'response_time_ms': 1500,
        'risk_factors': ['URL shortener', 'Urgency language']
    }
    
    analyzer.log_detection_attempt("test_user", "Test content", test_result)
    
    # Test stats retrieval
    stats = analyzer.get_user_stats("test_user")
    assert 'detection_stats' in stats, "Stats should include detection_stats"
    
    logger.info("✅ Behavior analyzer test passed")

def test_integration():
    """Test system integration"""
    logger.info("Testing system integration...")
    
    # Initialize all components
    config = Config()
    game_engine = GameEngine()
    detector = PhishingDetector()
    user_manager = UserManager()
    analyzer = BehaviorAnalyzer()
    
    # Test end-to-end workflow
    user_id = "integration_test_user"
    
    # 1. Start a game
    game_session = game_engine.start_game(user_id, "phishing_challenge")
    
    # 2. Detect phishing
    test_content = "Your PayPal account needs verification: http://paypa1-secure.com"
    detection_result = detector.detect(test_content, user_id)
    
    # 3. Log behavior
    analyzer.log_detection_attempt(user_id, test_content, detection_result)
    
    # 4. Get user progress
    progress = game_engine.get_user_progress(user_id)
    
    # 5. Get behavioral insights
    insights = analyzer.get_behavioral_insights(user_id)
    
    assert len(insights) > 0, "Should have behavioral insights"
    
    logger.info("✅ Integration test passed")

def main():
    """Run all tests"""
    logger.info("🚀 Starting Gamification-Based Phishing Defense System Tests")
    
    try:
        test_config()
        test_game_engine()
        test_phishing_detector()
        test_user_manager()
        test_behavior_analyzer()
        test_integration()
        
        logger.info("🎉 All tests passed! System is working correctly.")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
