"""
Interactive Dashboard for Phishing Defense System
Provides web-based visualization and analytics interface
"""

import dash
from dash import dcc, html, Input, Output, callback_context
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import json

from .plot_generator import PlotGenerator


class PhishingDefenseDashboard:
    """Interactive dashboard for phishing defense system analytics"""
    
    def __init__(self, user_manager, behavior_analyzer):
        self.user_manager = user_manager
        self.behavior_analyzer = behavior_analyzer
        self.plot_generator = PlotGenerator(user_manager, behavior_analyzer)
        
        # Initialize Dash app
        self.app = dash.Dash(__name__, 
                            external_stylesheets=[
                                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
                            ])
        
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Setup the dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1([
                    html.I(className="fas fa-shield-alt"),
                    " Phishing Defense Analytics Dashboard"
                ], className="dashboard-header"),
                html.P("Comprehensive analytics and insights for intelligent phishing and whaling defense", 
                       className="dashboard-subtitle")
            ], className="header-section"),
            
            # Navigation Tabs
            dcc.Tabs([
                # System Overview Tab
                dcc.Tab(label='System Overview', children=[
                    html.Div([
                        # Key Metrics Cards
                        html.Div([
                            self._create_metric_card("Total Users", "1,247", "fas fa-users", "success"),
                            self._create_metric_card("Active Detections", "156", "fas fa-search", "primary"),
                            self._create_metric_card("System Accuracy", "94.2%", "fas fa-chart-line", "info"),
                            self._create_metric_card("Threats Blocked", "1,089", "fas fa-ban", "danger")
                        ], className="metrics-row"),
                        
                        # Main Charts
                        html.Div([
                            html.Div([
                                dcc.Graph(id='detection-timeline', style={'height': '400px'})
                            ], className="chart-container"),
                            html.Div([
                                dcc.Graph(id='threat-distribution', style={'height': '400px'})
                            ], className="chart-container")
                        ], className="charts-row"),
                        
                        html.Div([
                            html.Div([
                                dcc.Graph(id='user-activity-heatmap', style={'height': '400px'})
                            ], className="chart-container"),
                            html.Div([
                                dcc.Graph(id='performance-metrics', style={'height': '400px'})
                            ], className="chart-container")
                        ], className="charts-row"),
                        
                        html.Div([
                            dcc.Graph(id='engagement-funnel', style={'height': '400px'})
                        ], className="full-width-chart")
                    ])
                ]),
                
                # User Progress Tab
                dcc.Tab(label='User Progress', children=[
                    html.Div([
                        # User Selection
                        html.Div([
                            html.Label("Select User:"),
                            dcc.Dropdown(
                                id='user-selector',
                                options=[
                                    {'label': 'Demo User', 'value': 'demo_user'},
                                    {'label': 'Admin User', 'value': 'admin'},
                                    {'label': 'Test User 1', 'value': 'test_user_1'},
                                    {'label': 'Test User 2', 'value': 'test_user_2'}
                                ],
                                value='demo_user',
                                className="user-dropdown"
                            )
                        ], className="user-selection"),
                        
                        # User Progress Charts
                        html.Div([
                            html.Div([
                                dcc.Graph(id='learning-progress', style={'height': '400px'})
                            ], className="chart-container"),
                            html.Div([
                                dcc.Graph(id='game-performance', style={'height': '400px'})
                            ], className="chart-container")
                        ], className="charts-row"),
                        
                        html.Div([
                            html.Div([
                                dcc.Graph(id='achievement-progress', style={'height': '400px'})
                            ], className="chart-container"),
                            html.Div([
                                dcc.Graph(id='detection-accuracy', style={'height': '400px'})
                            ], className="chart-container")
                        ], className="charts-row"),
                        
                        html.Div([
                            dcc.Graph(id='risk-profile', style={'height': '400px'})
                        ], className="full-width-chart")
                    ])
                ]),
                
                # Behavioral Analytics Tab
                dcc.Tab(label='Behavioral Analytics', children=[
                    html.Div([
                        html.Div([
                            html.Div([
                                dcc.Graph(id='behavior-clusters', style={'height': '400px'})
                            ], className="chart-container"),
                            html.Div([
                                dcc.Graph(id='response-time-analysis', style={'height': '400px'})
                            ], className="chart-container")
                        ], className="charts-row"),
                        
                        html.Div([
                            html.Div([
                                dcc.Graph(id='learning-patterns', style={'height': '400px'})
                            ], className="chart-container"),
                            html.Div([
                                dcc.Graph(id='risk-correlation', style={'height': '400px'})
                            ], className="chart-container")
                        ], className="charts-row"),
                        
                        html.Div([
                            dcc.Graph(id='behavioral-anomalies', style={'height': '400px'})
                        ], className="full-width-chart")
                    ])
                ]),
                
                # Model Performance Tab
                dcc.Tab(label='Model Performance', children=[
                    html.Div([
                        html.Div([
                            html.Div([
                                dcc.Graph(id='model-accuracy', style={'height': '400px'})
                            ], className="chart-container"),
                            html.Div([
                                dcc.Graph(id='confusion-matrix', style={'height': '400px'})
                            ], className="chart-container")
                        ], className="charts-row"),
                        
                        html.Div([
                            html.Div([
                                dcc.Graph(id='roc-curves', style={'height': '400px'})
                            ], className="chart-container"),
                            html.Div([
                                dcc.Graph(id='feature-importance', style={'height': '400px'})
                            ], className="chart-container")
                        ], className="charts-row"),
                        
                        html.Div([
                            dcc.Graph(id='confidence-distribution', style={'height': '400px'})
                        ], className="full-width-chart")
                    ])
                ]),
                
                # Real-time Analytics Tab
                dcc.Tab(label='Real-time Analytics', children=[
                    html.Div([
                        html.Div([
                            html.H3("Live System Monitoring"),
                            html.P("Real-time data updates every 30 seconds")
                        ], className="realtime-header"),
                        
                        html.Div([
                            self._create_metric_card("Active Sessions", "23", "fas fa-users", "primary"),
                            self._create_metric_card("Detections Today", "45", "fas fa-search", "success"),
                            self._create_metric_card("Avg Response Time", "1.2s", "fas fa-clock", "info"),
                            self._create_metric_card("System Load", "67%", "fas fa-server", "warning")
                        ], className="metrics-row"),
                        
                        html.Div([
                            dcc.Graph(id='realtime-detections', style={'height': '400px'}),
                            dcc.Interval(
                                id='interval-component',
                                interval=30*1000,  # 30 seconds
                                n_intervals=0
                            )
                        ], className="full-width-chart")
                    ])
                ])
            ], className="dashboard-tabs"),
            
            # Footer
            html.Div([
                html.P([
                    "Phishing Defense System v1.0 | ",
                    html.A("Documentation", href="#", className="footer-link"),
                    " | ",
                    html.A("Support", href="#", className="footer-link")
                ], className="footer-text")
            ], className="footer-section")
        ], className="dashboard-container")
    
    def _create_metric_card(self, title: str, value: str, icon: str, color: str) -> html.Div:
        """Create a metric card component"""
        return html.Div([
            html.Div([
                html.I(className=icon, style={'color': self._get_color(color)}),
                html.H3(value, className="metric-value"),
                html.P(title, className="metric-title")
            ], className="metric-content")
        ], className="metric-card")
    
    def _get_color(self, color_name: str) -> str:
        """Get color value by name"""
        colors = {
            'primary': '#1f77b4',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8'
        }
        return colors.get(color_name, '#1f77b4')
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        # System Overview Callbacks
        @self.app.callback(
            Output('detection-timeline', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_detection_timeline(n):
            plots = self.plot_generator.get_system_overview_dashboard()
            return plots['detection_timeline']
        
        @self.app.callback(
            Output('threat-distribution', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_threat_distribution(n):
            plots = self.plot_generator.get_system_overview_dashboard()
            return plots['threat_distribution']
        
        @self.app.callback(
            Output('user-activity-heatmap', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_user_activity_heatmap(n):
            plots = self.plot_generator.get_system_overview_dashboard()
            return plots['user_activity_heatmap']
        
        @self.app.callback(
            Output('performance-metrics', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_performance_metrics(n):
            plots = self.plot_generator.get_system_overview_dashboard()
            return plots['performance_metrics']
        
        @self.app.callback(
            Output('engagement-funnel', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_engagement_funnel(n):
            plots = self.plot_generator.get_system_overview_dashboard()
            return plots['engagement_funnel']
        
        # User Progress Callbacks
        @self.app.callback(
            [Output('learning-progress', 'figure'),
             Output('game-performance', 'figure'),
             Output('achievement-progress', 'figure'),
             Output('detection-accuracy', 'figure'),
             Output('risk-profile', 'figure')],
            [Input('user-selector', 'value'),
             Input('interval-component', 'n_intervals')]
        )
        def update_user_progress_plots(user_id, n):
            plots = self.plot_generator.get_user_progress_plots(user_id)
            return (plots['learning_progress'],
                    plots['game_performance'],
                    plots['achievement_progress'],
                    plots['detection_accuracy'],
                    plots['risk_profile'])
        
        # Behavioral Analytics Callbacks
        @self.app.callback(
            Output('behavior-clusters', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_behavior_clusters(n):
            plots = self.plot_generator.get_behavioral_analytics_plots()
            return plots['behavior_clusters']
        
        @self.app.callback(
            Output('response-time-analysis', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_response_time_analysis(n):
            plots = self.plot_generator.get_behavioral_analytics_plots()
            return plots['response_time_analysis']
        
        @self.app.callback(
            Output('learning-patterns', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_learning_patterns(n):
            plots = self.plot_generator.get_behavioral_analytics_plots()
            return plots['learning_patterns']
        
        @self.app.callback(
            Output('risk-correlation', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_risk_correlation(n):
            plots = self.plot_generator.get_behavioral_analytics_plots()
            return plots['risk_correlation']
        
        @self.app.callback(
            Output('behavioral-anomalies', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_behavioral_anomalies(n):
            plots = self.plot_generator.get_behavioral_analytics_plots()
            return plots['behavioral_anomalies']
        
        # Model Performance Callbacks
        @self.app.callback(
            Output('model-accuracy', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_model_accuracy(n):
            plots = self.plot_generator.get_model_performance_plots()
            return plots['model_accuracy']
        
        @self.app.callback(
            Output('confusion-matrix', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_confusion_matrix(n):
            plots = self.plot_generator.get_model_performance_plots()
            return plots['confusion_matrix']
        
        @self.app.callback(
            Output('roc-curves', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_roc_curves(n):
            plots = self.plot_generator.get_model_performance_plots()
            return plots['roc_curves']
        
        @self.app.callback(
            Output('feature-importance', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_feature_importance(n):
            plots = self.plot_generator.get_model_performance_plots()
            return plots['feature_importance']
        
        @self.app.callback(
            Output('confidence-distribution', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_confidence_distribution(n):
            plots = self.plot_generator.get_model_performance_plots()
            return plots['confidence_distribution']
        
        # Real-time Analytics Callback
        @self.app.callback(
            Output('realtime-detections', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_realtime_detections(n):
            # Create real-time detection chart
            now = datetime.now()
            times = [now - timedelta(minutes=i) for i in range(60, 0, -1)]
            detections = np.random.poisson(2, 60)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=detections,
                mode='lines+markers',
                name='Detections',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title='Real-time Detection Events (Last Hour)',
                xaxis_title='Time',
                yaxis_title='Number of Detections',
                template='plotly_white',
                showlegend=False
            )
            
            return fig
    
    def run(self, debug=True, host='0.0.0.0', port=8050):
        """Run the dashboard"""
        self.app.run(debug=debug, host=host, port=port)
    
    def get_app(self):
        """Get the Dash app instance"""
        return self.app
