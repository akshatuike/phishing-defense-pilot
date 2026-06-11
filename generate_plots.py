#!/usr/bin/env python3
"""
Plot Generation Script for Phishing Defense System
Generates and exports all visualizations to HTML files
"""

import os
import sys
import json
from datetime import datetime
import pandas as pd
import numpy as np

# Add src to path
sys.path.append('src')

from src.utils.config import Config
from src.database.user_manager import UserManager
from src.analytics.behavior_analyzer import BehaviorAnalyzer
from src.visualization.plot_generator import PlotGenerator
from src.visualization.dashboard import PhishingDefenseDashboard


def create_output_directories():
    """Create output directories for plots"""
    directories = [
        'plots',
        'plots/system_overview',
        'plots/user_progress',
        'plots/behavioral_analytics',
        'plots/model_performance',
        'plots/combined'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def generate_all_plots():
    """Generate all plots and export them"""
    print("🚀 Starting plot generation for Phishing Defense System...")
    
    # Initialize components
    print("📊 Initializing system components...")
    config = Config()
    user_manager = UserManager()
    behavior_analyzer = BehaviorAnalyzer()
    plot_generator = PlotGenerator(user_manager, behavior_analyzer)
    
    # Create output directories
    create_output_directories()
    
    # Generate all plots
    print("📈 Generating all plots...")
    all_plots = plot_generator.get_all_plots()
    
    # Export individual plot categories
    for category, plots in all_plots.items():
        print(f"\n📊 Exporting {category} plots...")
        category_dir = f"plots/{category}"
        
        for plot_name, fig in plots.items():
            filename = f"{category_dir}/{plot_name}.html"
            fig.write_html(filename, include_plotlyjs=True)
            print(f"  ✓ Exported: {plot_name}")
    
    # Create combined dashboard
    print("\n🌐 Creating combined dashboard...")
    dashboard = PhishingDefenseDashboard(user_manager, behavior_analyzer)
    
    # Export combined HTML with all plots
    print("📄 Creating comprehensive HTML report...")
    create_comprehensive_report(all_plots)
    
    print("\n✅ Plot generation completed successfully!")
    print("\n📁 Generated files:")
    print("  - plots/system_overview/ - System overview visualizations")
    print("  - plots/user_progress/ - User progress and learning plots")
    print("  - plots/behavioral_analytics/ - Behavioral analysis plots")
    print("  - plots/model_performance/ - Model performance metrics")
    print("  - plots/combined/comprehensive_report.html - Complete dashboard")
    
    return all_plots


def create_comprehensive_report(all_plots):
    """Create a comprehensive HTML report with all plots"""

    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Phishing Defense System - Comprehensive Analytics Report</title>

<style>
body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #333;
}}

.container {{
    max-width: 1400px;
    margin: 0 auto;
    background: white;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}}

.header {{
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
    padding: 2rem;
    text-align: center;
}}

.header h1 {{
    margin: 0;
    font-size: 2.5rem;
}}

.content {{
    padding: 2rem;
}}

.section {{
    margin-bottom: 3rem;
}}

.plot-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
    gap: 2rem;
}}

.plot-container {{
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1rem;
}}
</style>
</head>

<body>
<div class="container">
<div class="header">
<h1>🛡️ Phishing Defense System</h1>
<p>Generated on: __TIMESTAMP__</p>
</div>

<div class="content">
"""

    # Replace timestamp safely
    html_content = html_content.replace("__TIMESTAMP__", timestamp)

    category_titles = {
        'system_overview': '🌐 System Overview',
        'user_progress': '👤 User Progress & Learning',
        'behavioral_analytics': '🧠 Behavioral Analytics',
        'model_performance': '🤖 Model Performance'
    }

    for category, plots in all_plots.items():
        if category in category_titles:

            html_content += f"""
<div class="section">
<h2>{category_titles[category]}</h2>
<div class="plot-grid">
"""

            for plot_name, fig in plots.items():
                plot_title = plot_name.replace('_', ' ').title()

                html_content += f"""
<div class="plot-container">
<h3>{plot_title}</h3>
{fig.to_html(full_html=False, include_plotlyjs=False)}
</div>
"""

            html_content += """
</div>
</div>
"""

    html_content += """
</div>
</div>
</body>
</html>
"""

    with open('plots/combined/comprehensive_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("✓ Exported: comprehensive_report.html")
