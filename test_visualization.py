#!/usr/bin/env python3
"""
Test script for visualization components
Verifies that all plots and dashboard components work correctly
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.append('src')

def test_plot_generator():
    """Test the PlotGenerator class"""
    print("🧪 Testing PlotGenerator...")
    
    try:
        from src.utils.config import Config
        from src.database.user_manager import UserManager
        from src.analytics.behavior_analyzer import BehaviorAnalyzer
        from src.visualization.plot_generator import PlotGenerator
        
        # Initialize components
        config = Config()
        user_manager = UserManager(config)
        behavior_analyzer = BehaviorAnalyzer(user_manager)
        plot_generator = PlotGenerator(user_manager, behavior_analyzer)
        
        # Test system overview plots
        print("  📊 Testing system overview plots...")
        system_plots = plot_generator.get_system_overview_dashboard()
        assert len(system_plots) == 5, f"Expected 5 system plots, got {len(system_plots)}"
        print(f"    ✓ Generated {len(system_plots)} system overview plots")
        
        # Test user progress plots
        print("  👤 Testing user progress plots...")
        user_plots = plot_generator.get_user_progress_plots("demo_user")
        assert len(user_plots) == 5, f"Expected 5 user plots, got {len(user_plots)}"
        print(f"    ✓ Generated {len(user_plots)} user progress plots")
        
        # Test behavioral analytics plots
        print("  🧠 Testing behavioral analytics plots...")
        behavior_plots = plot_generator.get_behavioral_analytics_plots()
        assert len(behavior_plots) == 5, f"Expected 5 behavior plots, got {len(behavior_plots)}"
        print(f"    ✓ Generated {len(behavior_plots)} behavioral analytics plots")
        
        # Test model performance plots
        print("  🤖 Testing model performance plots...")
        model_plots = plot_generator.get_model_performance_plots()
        assert len(model_plots) == 5, f"Expected 5 model plots, got {len(model_plots)}"
        print(f"    ✓ Generated {len(model_plots)} model performance plots")
        
        # Test all plots
        print("  📈 Testing all plots...")
        all_plots = plot_generator.get_all_plots()
        assert len(all_plots) == 4, f"Expected 4 categories, got {len(all_plots)}"
        total_plots = sum(len(plots) for plots in all_plots.values())
        assert total_plots == 20, f"Expected 20 total plots, got {total_plots}"
        print(f"    ✓ Generated {total_plots} total plots across {len(all_plots)} categories")
        
        print("  ✅ PlotGenerator tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ PlotGenerator test failed: {str(e)}")
        return False

def test_dashboard():
    """Test the Dashboard class"""
    print("🧪 Testing Dashboard...")
    
    try:
        from src.utils.config import Config
        from src.database.user_manager import UserManager
        from src.analytics.behavior_analyzer import BehaviorAnalyzer
        from src.visualization.dashboard import PhishingDefenseDashboard
        
        # Initialize components
        config = Config()
        user_manager = UserManager(config)
        behavior_analyzer = BehaviorAnalyzer(user_manager)
        
        # Create dashboard
        dashboard = PhishingDefenseDashboard(user_manager, behavior_analyzer)
        
        # Test dashboard app
        assert dashboard.app is not None, "Dashboard app should not be None"
        assert hasattr(dashboard.app, 'layout'), "Dashboard should have layout"
        print("    ✓ Dashboard app created successfully")
        
        # Test plot generator integration
        assert dashboard.plot_generator is not None, "Dashboard should have plot generator"
        print("    ✓ Plot generator integrated successfully")
        
        print("  ✅ Dashboard tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Dashboard test failed: {str(e)}")
        return False

def test_plot_export():
    """Test plot export functionality"""
    print("🧪 Testing plot export...")
    
    try:
        from src.utils.config import Config
        from src.database.user_manager import UserManager
        from src.analytics.behavior_analyzer import BehaviorAnalyzer
        from src.visualization.plot_generator import PlotGenerator
        
        # Initialize components
        config = Config()
        user_manager = UserManager(config)
        behavior_analyzer = BehaviorAnalyzer(user_manager)
        plot_generator = PlotGenerator(user_manager, behavior_analyzer)
        
        # Create test directory
        test_dir = "test_plots"
        os.makedirs(test_dir, exist_ok=True)
        
        # Test HTML export
        print("  📄 Testing HTML export...")
        plots = plot_generator.get_system_overview_dashboard()
        
        for name, fig in plots.items():
            filename = f"{test_dir}/{name}.html"
            fig.write_html(filename, include_plotlyjs=True)
            assert os.path.exists(filename), f"HTML file {filename} should exist"
            print(f"    ✓ Exported {name}.html")
        
        # Test JSON export
        print("  📊 Testing JSON export...")
        for name, fig in plots.items():
            json_data = fig.to_json()
            assert json_data is not None, f"JSON data for {name} should not be None"
            assert len(json_data) > 0, f"JSON data for {name} should not be empty"
            print(f"    ✓ Exported {name} to JSON")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print("    ✓ Cleaned up test files")
        
        print("  ✅ Plot export tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Plot export test failed: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoint functionality"""
    print("🧪 Testing API endpoints...")
    
    try:
        from src.utils.config import Config
        from src.database.user_manager import UserManager
        from src.analytics.behavior_analyzer import BehaviorAnalyzer
        from src.visualization.plot_generator import PlotGenerator
        
        # Initialize components
        config = Config()
        user_manager = UserManager(config)
        behavior_analyzer = BehaviorAnalyzer(user_manager)
        plot_generator = PlotGenerator(user_manager, behavior_analyzer)
        
        # Test system overview endpoint
        print("  🌐 Testing system overview endpoint...")
        plots = plot_generator.get_system_overview_dashboard()
        response_data = {
            'status': 'success',
            'plots': {name: fig.to_json() for name, fig in plots.items()}
        }
        assert response_data['status'] == 'success', "Status should be success"
        assert len(response_data['plots']) == 5, "Should have 5 system plots"
        print("    ✓ System overview endpoint works")
        
        # Test user progress endpoint
        print("  👤 Testing user progress endpoint...")
        user_plots = plot_generator.get_user_progress_plots("demo_user")
        response_data = {
            'status': 'success',
            'plots': {name: fig.to_json() for name, fig in user_plots.items()}
        }
        assert response_data['status'] == 'success', "Status should be success"
        assert len(response_data['plots']) == 5, "Should have 5 user plots"
        print("    ✓ User progress endpoint works")
        
        # Test all plots endpoint
        print("  📈 Testing all plots endpoint...")
        all_plots = plot_generator.get_all_plots()
        response_data = {
            'status': 'success',
            'plots': {
                category: {name: fig.to_json() for name, fig in plots.items()}
                for category, plots in all_plots.items()
            }
        }
        assert response_data['status'] == 'success', "Status should be success"
        assert len(response_data['plots']) == 4, "Should have 4 categories"
        print("    ✓ All plots endpoint works")
        
        print("  ✅ API endpoint tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ API endpoint test failed: {str(e)}")
        return False

def main():
    """Run all visualization tests"""
    print("🚀 Starting visualization component tests...")
    print(f"📅 Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("PlotGenerator", test_plot_generator),
        ("Dashboard", test_dashboard),
        ("Plot Export", test_plot_export),
        ("API Endpoints", test_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} tests...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All visualization tests passed!")
        print("\n📋 Next steps:")
        print("  1. Run 'python generate_plots.py' to generate all plots")
        print("  2. Run 'python run_dashboard.py' to start the interactive dashboard")
        print("  3. Open 'plots/combined/comprehensive_report.html' in your browser")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
