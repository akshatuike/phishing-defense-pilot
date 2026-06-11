#!/usr/bin/env python3
"""
Dashboard Runner for Phishing Defense System
Launches the interactive analytics dashboard
"""

import os
import sys
import webbrowser
from threading import Timer

# Add src to path
sys.path.append('src')

from src.utils.config import Config
from src.database.user_manager import UserManager
from src.analytics.behavior_analyzer import BehaviorAnalyzer
from src.visualization.dashboard import PhishingDefenseDashboard


def open_browser():
    """Open browser to dashboard URL"""
    webbrowser.open('http://localhost:8050')


def main():
    """Main function to run the dashboard"""
    try:
        print("🚀 Starting Phishing Defense Analytics Dashboard...")
        
        # Initialize components
        print("📊 Initializing system components...")
        config = Config()
        user_manager = UserManager()
        behavior_analyzer = BehaviorAnalyzer()
        
        # Create dashboard
        print("🌐 Creating dashboard...")
        dashboard = PhishingDefenseDashboard(user_manager, behavior_analyzer)
        
        # Open browser after a short delay
        Timer(2, open_browser).start()
        
        print("✅ Dashboard is starting...")
        print("🌐 Dashboard will be available at: http://localhost:8050")
        print("📱 Press Ctrl+C to stop the dashboard")
        
        # Run the dashboard
        dashboard.run(debug=True, host='0.0.0.0', port=8050)
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
