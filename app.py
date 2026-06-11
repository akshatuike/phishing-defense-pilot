#!/usr/bin/env python3
"""
Main application entry point for the Gamification-Based Phishing Defense System
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
from datetime import datetime

# Import our custom modules
from src.gamification.game_engine import GameEngine
from src.detection.phishing_detector import PhishingDetector
from src.database.user_manager import UserManager
from src.analytics.behavior_analyzer import BehaviorAnalyzer
from src.utils.config import Config
from src.visualization.plot_generator import PlotGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'

# Enable CORS
CORS(app)

# Initialize SocketIO for real-time features
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize core components
config = Config()
user_manager = UserManager()
game_engine = GameEngine()
phishing_detector = PhishingDetector()
behavior_analyzer = BehaviorAnalyzer()
plot_generator = PlotGenerator(user_manager, behavior_analyzer)

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Simple authentication using UserManager
        user = user_manager.authenticate_user(username, password)

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard with gamification elements"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_data = user_manager.get_user_data(user_id)
    game_progress = game_engine.get_user_progress(user_id)
    
    return render_template('dashboard.html', 
                         user_data=user_data, 
                         game_progress=game_progress)

@app.route('/games')
def games():
    """Gamification interface"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    available_games = game_engine.get_available_games(user_id)
    
    return render_template('games.html', games=available_games)

@app.route('/api/detect', methods=['POST'])
def detect_phishing():
    """API endpoint for phishing detection"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        user_id = session.get('user_id', 'anonymous')
        
        # Perform detection
        result = phishing_detector.detect(content, user_id)
        
        # Log user behavior
        behavior_analyzer.log_detection_attempt(user_id, content, result)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in phishing detection: {str(e)}")
        return jsonify({'error': 'Detection failed'}), 500

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new game session"""
    try:
        data = request.get_json()
        game_type = data.get('game_type', 'phishing_challenge')
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        game_session = game_engine.start_game(user_id, game_type)
        return jsonify(game_session)
    
    except Exception as e:
        logger.error(f"Error starting game: {str(e)}")
        return jsonify({'error': 'Failed to start game'}), 500

@app.route('/api/game/submit', methods=['POST'])
def submit_game_answer():
    """Submit game answer and get feedback"""
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        answer = data.get('answer')
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        result = game_engine.submit_answer(game_id, user_id, answer)
        
        # Analyze behavior
        behavior_analyzer.analyze_game_behavior(user_id, game_id, answer, result)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error submitting game answer: {str(e)}")
        return jsonify({'error': 'Failed to submit answer'}), 500

@app.route('/api/user/progress')
def get_user_progress():
    """Get user's learning progress and achievements"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        progress = game_engine.get_user_progress(user_id)
        achievements = game_engine.get_user_achievements(user_id)
        behavior_stats = behavior_analyzer.get_user_stats(user_id)
        
        return jsonify({
            'progress': progress,
            'achievements': achievements,
            'behavior_stats': behavior_stats
        })
    
    except Exception as e:
        logger.error(f"Error getting user progress: {str(e)}")
        return jsonify({'error': 'Failed to get progress'}), 500

@app.route('/api/admin/stats')
def admin_stats():
    """Admin endpoint for system statistics"""
    try:
        # Check if user is admin (implement proper admin check)
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        stats = {
            'total_users': user_manager.get_total_users(),
            'active_games': game_engine.get_active_games_count(),
            'detection_stats': phishing_detector.get_stats(),
            'system_performance': {
                'avg_response_time': phishing_detector.get_avg_response_time(),
                'accuracy_rate': phishing_detector.get_accuracy_rate()
            }
        }
        
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        return jsonify({'error': 'Failed to get stats'}), 500

@app.route('/api/visualizations/system-overview')
def system_overview_plots():
    """API endpoint for system overview visualizations"""
    try:
        plots = plot_generator.get_system_overview_dashboard()
        return jsonify({
            'status': 'success',
            'plots': {name: fig.to_json() for name, fig in plots.items()}
        })
    except Exception as e:
        logger.error(f"Error generating system overview plots: {str(e)}")
        return jsonify({'error': 'Failed to generate plots'}), 500

@app.route('/api/visualizations/user-progress/<user_id>')
def user_progress_plots(user_id):
    """API endpoint for user progress visualizations"""
    try:
        plots = plot_generator.get_user_progress_plots(user_id)
        return jsonify({
            'status': 'success',
            'plots': {name: fig.to_json() for name, fig in plots.items()}
        })
    except Exception as e:
        logger.error(f"Error generating user progress plots: {str(e)}")
        return jsonify({'error': 'Failed to generate plots'}), 500

@app.route('/api/visualizations/behavioral-analytics')
def behavioral_analytics_plots():
    """API endpoint for behavioral analytics visualizations"""
    try:
        plots = plot_generator.get_behavioral_analytics_plots()
        return jsonify({
            'status': 'success',
            'plots': {name: fig.to_json() for name, fig in plots.items()}
        })
    except Exception as e:
        logger.error(f"Error generating behavioral analytics plots: {str(e)}")
        return jsonify({'error': 'Failed to generate plots'}), 500

@app.route('/api/visualizations/model-performance')
def model_performance_plots():
    """API endpoint for model performance visualizations"""
    try:
        plots = plot_generator.get_model_performance_plots()
        return jsonify({
            'status': 'success',
            'plots': {name: fig.to_json() for name, fig in plots.items()}
        })
    except Exception as e:
        logger.error(f"Error generating model performance plots: {str(e)}")
        return jsonify({'error': 'Failed to generate plots'}), 500

@app.route('/api/visualizations/all')
def all_plots():
    """API endpoint for all visualizations"""
    try:
        all_plots = plot_generator.get_all_plots()
        return jsonify({
            'status': 'success',
            'plots': {
                category: {name: fig.to_json() for name, fig in plots.items()}
                for category, plots in all_plots.items()
            }
        })
    except Exception as e:
        logger.error(f"Error generating all plots: {str(e)}")
        return jsonify({'error': 'Failed to generate plots'}), 500

@app.route('/dashboard/analytics')
def analytics_dashboard():
    """Analytics dashboard page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    return render_template('analytics_dashboard.html', user_id=user_id)

# SocketIO events for real-time features
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('game_action')
def handle_game_action(data):
    """Handle real-time game actions"""
    try:
        user_id = session.get('user_id')
        action_type = data.get('action_type')
        action_data = data.get('action_data')
        
        # Process game action
        result = game_engine.process_real_time_action(user_id, action_type, action_data)
        
        # Emit result back to client
        emit('game_update', result)
        
    except Exception as e:
        logger.error(f"Error handling game action: {str(e)}")
        emit('error', {'message': 'Action failed'})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

def create_app():
    """Application factory for testing"""
    return app

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Initialize database
    user_manager.init_database()
    
    # Load pre-trained models
    phishing_detector.load_models()
    
    logger.info("Starting Gamification-Based Phishing Defense System...")
    
    # Run the application
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
