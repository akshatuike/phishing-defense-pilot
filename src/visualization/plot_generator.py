"""
Plot Generator for Phishing Defense System
Generates comprehensive visualizations for system analytics and user insights
"""

import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as sp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


class PlotGenerator:
    """Generates various plots and visualizations for the phishing defense system"""
    
    def __init__(self, user_manager, behavior_analyzer):
        self.user_manager = user_manager
        self.behavior_analyzer = behavior_analyzer
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
    
    def get_system_overview_dashboard(self) -> Dict[str, go.Figure]:
        """Generate comprehensive system overview dashboard"""
        plots = {}
        
        # 1. Detection Statistics Over Time
        plots['detection_timeline'] = self._create_detection_timeline()
        
        # 2. User Activity Heatmap
        plots['user_activity_heatmap'] = self._create_user_activity_heatmap()
        
        # 3. Threat Distribution Pie Chart
        plots['threat_distribution'] = self._create_threat_distribution()
        
        # 4. System Performance Metrics
        plots['performance_metrics'] = self._create_performance_metrics()
        
        # 5. User Engagement Funnel
        plots['engagement_funnel'] = self._create_engagement_funnel()
        
        return plots
    
    def get_user_progress_plots(self, user_id: str) -> Dict[str, go.Figure]:
        """Generate user-specific progress and learning plots"""
        plots = {}
        
        # 1. Learning Progress Over Time
        plots['learning_progress'] = self._create_learning_progress(user_id)
        
        # 2. Game Performance Radar Chart
        plots['game_performance'] = self._create_game_performance_radar(user_id)
        
        # 3. Achievement Progress
        plots['achievement_progress'] = self._create_achievement_progress(user_id)
        
        # 4. Detection Accuracy Trends
        plots['detection_accuracy'] = self._create_detection_accuracy_trends(user_id)
        
        # 5. Behavioral Risk Profile
        plots['risk_profile'] = self._create_risk_profile(user_id)
        
        return plots
    
    def get_behavioral_analytics_plots(self) -> Dict[str, go.Figure]:
        """Generate behavioral analytics and insights plots"""
        plots = {}
        
        # 1. User Behavior Clusters
        plots['behavior_clusters'] = self._create_behavior_clusters()
        
        # 2. Response Time Analysis
        plots['response_time_analysis'] = self._create_response_time_analysis()
        
        # 3. Learning Pattern Analysis
        plots['learning_patterns'] = self._create_learning_patterns()
        
        # 4. Risk Factor Correlation
        plots['risk_correlation'] = self._create_risk_correlation()
        
        # 5. Behavioral Anomalies
        plots['behavioral_anomalies'] = self._create_behavioral_anomalies()
        
        return plots
    
    def get_model_performance_plots(self) -> Dict[str, go.Figure]:
        """Generate model performance and accuracy plots"""
        plots = {}
        
        # 1. Model Accuracy Comparison
        plots['model_accuracy'] = self._create_model_accuracy_comparison()
        
        # 2. Confusion Matrix
        plots['confusion_matrix'] = self._create_confusion_matrix()
        
        # 3. ROC Curves
        plots['roc_curves'] = self._create_roc_curves()
        
        # 4. Feature Importance
        plots['feature_importance'] = self._create_feature_importance()
        
        # 5. Prediction Confidence Distribution
        plots['confidence_distribution'] = self._create_confidence_distribution()
        
        return plots
    
    def _create_detection_timeline(self) -> go.Figure:
        """Create timeline of detection events"""
        # Simulate detection data over time
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        phishing_detected = np.random.poisson(5, len(dates))
        whaling_detected = np.random.poisson(2, len(dates))
        false_positives = np.random.poisson(1, len(dates))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=phishing_detected,
            mode='lines+markers',
            name='Phishing Detected',
            line=dict(color=self.color_scheme['danger'], width=2),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=whaling_detected,
            mode='lines+markers',
            name='Whaling Detected',
            line=dict(color=self.color_scheme['warning'], width=2),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=false_positives,
            mode='lines+markers',
            name='False Positives',
            line=dict(color=self.color_scheme['info'], width=2),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title='Detection Events Timeline',
            xaxis_title='Date',
            yaxis_title='Number of Detections',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def _create_user_activity_heatmap(self) -> go.Figure:
        """Create user activity heatmap by hour and day"""
        # Simulate user activity data
        hours = list(range(24))
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Generate activity matrix
        activity_matrix = np.random.randint(0, 100, size=(len(days), len(hours)))
        
        fig = go.Figure(data=go.Heatmap(
            z=activity_matrix,
            x=hours,
            y=days,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Activity Level')
        ))
        
        fig.update_layout(
            title='User Activity Heatmap',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            template='plotly_white'
        )
        
        return fig
    
    def _create_threat_distribution(self) -> go.Figure:
        """Create pie chart of threat types distribution"""
        threat_types = ['Phishing', 'Whaling', 'Spear Phishing', 'Vishing', 'Smishing']
        threat_counts = [45, 20, 15, 12, 8]
        
        fig = go.Figure(data=[go.Pie(
            labels=threat_types,
            values=threat_counts,
            hole=0.4,
            marker_colors=[self.color_scheme['danger'], self.color_scheme['warning'], 
                          self.color_scheme['info'], self.color_scheme['secondary'], 
                          self.color_scheme['primary']]
        )])
        
        fig.update_layout(
            title='Threat Type Distribution',
            template='plotly_white'
        )
        
        return fig
    
    def _create_performance_metrics(self) -> go.Figure:
        """Create performance metrics dashboard"""
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Response Time (ms)']
        values = [94.2, 92.8, 95.1, 93.9, 150]
        targets = [95.0, 90.0, 90.0, 90.0, 200]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=metrics,
            y=values,
            name='Current Performance',
            marker_color=self.color_scheme['primary']
        ))
        
        fig.add_trace(go.Bar(
            x=metrics,
            y=targets,
            name='Target Performance',
            marker_color=self.color_scheme['light'],
            opacity=0.7
        ))
        
        fig.update_layout(
            title='System Performance Metrics',
            yaxis_title='Score/Value',
            barmode='group',
            template='plotly_white'
        )
        
        return fig
    
    def _create_engagement_funnel(self) -> go.Figure:
        """Create user engagement funnel"""
        stages = ['Registered Users', 'Active Users', 'Game Players', 'Achievement Earners', 'Power Users']
        counts = [1000, 750, 500, 300, 150]
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=counts,
            textinfo="value+percent initial"
        ))
        
        fig.update_layout(
            title='User Engagement Funnel',
            template='plotly_white'
        )
        
        return fig
    
    def _create_learning_progress(self, user_id: str) -> go.Figure:
        """Create learning progress over time for specific user"""
        # Simulate learning progress data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
        knowledge_score = np.cumsum(np.random.normal(5, 2, len(dates)))
        knowledge_score = np.clip(knowledge_score, 0, 100)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=knowledge_score,
            mode='lines+markers',
            name='Knowledge Score',
            line=dict(color=self.color_scheme['success'], width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f'Learning Progress - User {user_id}',
            xaxis_title='Date',
            yaxis_title='Knowledge Score (%)',
            template='plotly_white'
        )
        
        return fig
    
    def _create_game_performance_radar(self, user_id: str) -> go.Figure:
        """Create radar chart of game performance"""
        categories = ['Speed', 'Accuracy', 'Strategy', 'Awareness', 'Response Time']
        user_scores = [85, 92, 78, 88, 76]
        avg_scores = [70, 75, 65, 72, 68]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=user_scores,
            theta=categories,
            fill='toself',
            name=f'User {user_id}',
            line_color=self.color_scheme['primary']
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=avg_scores,
            theta=categories,
            fill='toself',
            name='Average User',
            line_color=self.color_scheme['secondary']
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title=f'Game Performance Radar - User {user_id}',
            template='plotly_white'
        )
        
        return fig
    
    def _create_achievement_progress(self, user_id: str) -> go.Figure:
        """Create achievement progress visualization"""
        achievements = ['First Detection', 'Speed Demon', 'Accuracy Master', 'Learning Champion', 'Security Expert']
        progress = [100, 75, 60, 40, 20]
        
        fig = go.Figure(data=go.Bar(
            x=achievements,
            y=progress,
            marker_color=[self.color_scheme['success'] if p == 100 else self.color_scheme['primary'] for p in progress]
        ))
        
        fig.update_layout(
            title=f'Achievement Progress - User {user_id}',
            yaxis_title='Progress (%)',
            template='plotly_white'
        )
        
        return fig
    
    def _create_detection_accuracy_trends(self, user_id: str) -> go.Figure:
        """Create detection accuracy trends for user"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
        accuracy = np.clip(np.random.normal(85, 10, len(dates)), 0, 100)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=accuracy,
            mode='lines+markers',
            name='Detection Accuracy',
            line=dict(color=self.color_scheme['success'], width=2),
            marker=dict(size=6)
        ))
        
        fig.add_hline(y=90, line_dash="dash", line_color=self.color_scheme['warning'],
                     annotation_text="Target Accuracy")
        
        fig.update_layout(
            title=f'Detection Accuracy Trends - User {user_id}',
            xaxis_title='Date',
            yaxis_title='Accuracy (%)',
            template='plotly_white'
        )
        
        return fig
    
    def _create_risk_profile(self, user_id: str) -> go.Figure:
        """Create user risk profile visualization"""
        risk_factors = ['Click Rate', 'Response Time', 'Suspicion Level', 'Learning Curve', 'Alert Dismissal']
        risk_scores = [65, 45, 80, 30, 55]
        
        fig = go.Figure(data=go.Bar(
            x=risk_factors,
            y=risk_scores,
            marker_color=[self.color_scheme['danger'] if score > 70 else 
                         self.color_scheme['warning'] if score > 50 else 
                         self.color_scheme['success'] for score in risk_scores]
        ))
        
        fig.update_layout(
            title=f'Risk Profile - User {user_id}',
            yaxis_title='Risk Score',
            template='plotly_white'
        )
        
        return fig
    
    def _create_behavior_clusters(self) -> go.Figure:
        """Create user behavior clustering visualization"""
        # Simulate user behavior data
        np.random.seed(42)
        n_users = 100
        
        # Generate 3 clusters of users
        cluster1 = np.random.multivariate_normal([0.3, 0.7], [[0.1, 0], [0, 0.1]], n_users//3)
        cluster2 = np.random.multivariate_normal([0.7, 0.3], [[0.1, 0], [0, 0.1]], n_users//3)
        cluster3 = np.random.multivariate_normal([0.5, 0.5], [[0.1, 0], [0, 0.1]], n_users//3)
        
        all_data = np.vstack([cluster1, cluster2, cluster3])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=cluster1[:, 0],
            y=cluster1[:, 1],
            mode='markers',
            name='High Risk',
            marker=dict(color=self.color_scheme['danger'], size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=cluster2[:, 0],
            y=cluster2[:, 1],
            mode='markers',
            name='Medium Risk',
            marker=dict(color=self.color_scheme['warning'], size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=cluster3[:, 0],
            y=cluster3[:, 1],
            mode='markers',
            name='Low Risk',
            marker=dict(color=self.color_scheme['success'], size=8)
        ))
        
        fig.update_layout(
            title='User Behavior Clusters',
            xaxis_title='Response Time (normalized)',
            yaxis_title='Accuracy (normalized)',
            template='plotly_white'
        )
        
        return fig
    
    def _create_response_time_analysis(self) -> go.Figure:
        """Create response time analysis"""
        response_times = np.random.exponential(2, 1000)
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=response_times,
            nbinsx=30,
            marker_color=self.color_scheme['primary'],
            opacity=0.7
        ))
        
        fig.update_layout(
            title='Response Time Distribution',
            xaxis_title='Response Time (seconds)',
            yaxis_title='Frequency',
            template='plotly_white'
        )
        
        return fig
    
    def _create_learning_patterns(self) -> go.Figure:
        """Create learning pattern analysis"""
        sessions = list(range(1, 21))
        learning_curves = {
            'Fast Learners': [20, 35, 45, 55, 65, 75, 82, 87, 90, 92, 94, 95, 96, 97, 98, 98, 99, 99, 99, 99],
            'Average Learners': [15, 25, 35, 45, 55, 65, 72, 78, 83, 87, 90, 92, 94, 95, 96, 97, 97, 98, 98, 98],
            'Slow Learners': [10, 18, 25, 32, 40, 48, 55, 62, 68, 74, 79, 83, 86, 89, 91, 93, 94, 95, 96, 96]
        }
        
        fig = go.Figure()
        
        for pattern, curve in learning_curves.items():
            fig.add_trace(go.Scatter(
                x=sessions,
                y=curve,
                mode='lines+markers',
                name=pattern,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title='Learning Pattern Analysis',
            xaxis_title='Training Sessions',
            yaxis_title='Performance Score (%)',
            template='plotly_white'
        )
        
        return fig
    
    def _create_risk_correlation(self) -> go.Figure:
        """Create risk factor correlation matrix"""
        risk_factors = ['Age', 'Experience', 'Training Hours', 'Alert Sensitivity', 'Response Time']
        
        # Simulate correlation matrix
        np.random.seed(42)
        corr_matrix = np.random.uniform(-0.8, 0.8, (len(risk_factors), len(risk_factors)))
        np.fill_diagonal(corr_matrix, 1.0)
        corr_matrix = (corr_matrix + corr_matrix.T) / 2  # Make symmetric
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=risk_factors,
            y=risk_factors,
            colorscale='RdBu',
            zmid=0,
            showscale=True,
            colorbar=dict(title='Correlation')
        ))
        
        fig.update_layout(
            title='Risk Factor Correlations',
            template='plotly_white'
        )
        
        return fig
    
    def _create_behavioral_anomalies(self) -> go.Figure:
        """Create behavioral anomalies detection"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        normal_activity = np.random.normal(50, 10, len(dates))
        
        # Add some anomalies
        anomalies = normal_activity.copy()
        anomaly_indices = np.random.choice(len(dates), 10, replace=False)
        anomalies[anomaly_indices] = np.random.uniform(80, 100, len(anomaly_indices))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=normal_activity,
            mode='lines',
            name='Normal Activity',
            line=dict(color=self.color_scheme['primary'])
        ))
        
        fig.add_trace(go.Scatter(
            x=dates[anomaly_indices],
            y=anomalies[anomaly_indices],
            mode='markers',
            name='Anomalies',
            marker=dict(color=self.color_scheme['danger'], size=10, symbol='x')
        ))
        
        fig.update_layout(
            title='Behavioral Anomaly Detection',
            xaxis_title='Date',
            yaxis_title='Activity Level',
            template='plotly_white'
        )
        
        return fig
    
    def _create_model_accuracy_comparison(self) -> go.Figure:
        """Create model accuracy comparison"""
        models = ['BERT', 'ResNet', 'DenseNet', 'Ensemble']
        accuracy = [89.2, 85.7, 87.3, 94.2]
        precision = [87.1, 83.2, 85.9, 92.8]
        recall = [91.3, 88.1, 89.7, 95.1]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Accuracy',
            x=models,
            y=accuracy,
            marker_color=self.color_scheme['primary']
        ))
        
        fig.add_trace(go.Bar(
            name='Precision',
            x=models,
            y=precision,
            marker_color=self.color_scheme['success']
        ))
        
        fig.add_trace(go.Bar(
            name='Recall',
            x=models,
            y=recall,
            marker_color=self.color_scheme['warning']
        ))
        
        fig.update_layout(
            title='Model Performance Comparison',
            yaxis_title='Score (%)',
            barmode='group',
            template='plotly_white'
        )
        
        return fig
    
    def _create_confusion_matrix(self) -> go.Figure:
        """Create confusion matrix visualization"""
        # Simulate confusion matrix data
        cm = np.array([[850, 50], [30, 70]])
        
        fig = go.Figure(data=go.Heatmap(
            z=cm,
            x=['Predicted Negative', 'Predicted Positive'],
            y=['Actual Negative', 'Actual Positive'],
            text=cm,
            texttemplate="%{text}",
            textfont={"size": 16},
            colorscale='Blues',
            showscale=True
        ))
        
        fig.update_layout(
            title='Confusion Matrix',
            template='plotly_white'
        )
        
        return fig
    
    def _create_roc_curves(self) -> go.Figure:
        """Create ROC curves for different models"""
        # Simulate ROC curve data
        fpr = np.linspace(0, 1, 100)
        tpr_bert = 1 - (1 - fpr) ** 2
        tpr_resnet = 1 - (1 - fpr) ** 1.5
        tpr_ensemble = 1 - (1 - fpr) ** 3
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=fpr,
            y=tpr_bert,
            mode='lines',
            name='BERT (AUC=0.89)',
            line=dict(color=self.color_scheme['primary'])
        ))
        
        fig.add_trace(go.Scatter(
            x=fpr,
            y=tpr_resnet,
            mode='lines',
            name='ResNet (AUC=0.85)',
            line=dict(color=self.color_scheme['secondary'])
        ))
        
        fig.add_trace(go.Scatter(
            x=fpr,
            y=tpr_ensemble,
            mode='lines',
            name='Ensemble (AUC=0.94)',
            line=dict(color=self.color_scheme['success'])
        ))
        
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode='lines',
            name='Random',
            line=dict(color='gray', dash='dash')
        ))
        
        fig.update_layout(
            title='ROC Curves',
            xaxis_title='False Positive Rate',
            yaxis_title='True Positive Rate',
            template='plotly_white'
        )
        
        return fig
    
    def _create_feature_importance(self) -> go.Figure:
        """Create feature importance visualization"""
        features = ['URL Length', 'Domain Age', 'SSL Certificate', 'Suspicious Keywords', 
                   'Sender Reputation', 'Content Similarity', 'Time of Day', 'User Behavior']
        importance = [0.15, 0.12, 0.18, 0.22, 0.10, 0.08, 0.05, 0.10]
        
        fig = go.Figure(data=go.Bar(
            x=importance,
            y=features,
            orientation='h',
            marker_color=self.color_scheme['primary']
        ))
        
        fig.update_layout(
            title='Feature Importance',
            xaxis_title='Importance Score',
            template='plotly_white'
        )
        
        return fig
    
    def _create_confidence_distribution(self) -> go.Figure:
        """Create prediction confidence distribution"""
        # Simulate confidence scores
        confidence_scores = np.random.beta(2, 5, 1000) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=confidence_scores,
            nbinsx=30,
            marker_color=self.color_scheme['primary'],
            opacity=0.7
        ))
        
        fig.update_layout(
            title='Prediction Confidence Distribution',
            xaxis_title='Confidence Score (%)',
            yaxis_title='Frequency',
            template='plotly_white'
        )
        
        return fig
    
    def export_plots_to_html(self, plots: Dict[str, go.Figure], filename: str):
        """Export plots to HTML file"""
        with open(filename, 'w') as f:
            f.write('<html><head><title>Phishing Defense Analytics</title></head><body>')
            f.write('<h1>Phishing Defense System Analytics Dashboard</h1>')
            
            for plot_name, fig in plots.items():
                f.write(f'<h2>{plot_name.replace("_", " ").title()}</h2>')
                f.write(fig.to_html(full_html=False))
                f.write('<hr>')
            
            f.write('</body></html>')
    
    def get_all_plots(self) -> Dict[str, Dict[str, go.Figure]]:
        """Generate all available plots"""
        all_plots = {
            'system_overview': self.get_system_overview_dashboard(),
            'behavioral_analytics': self.get_behavioral_analytics_plots(),
            'model_performance': self.get_model_performance_plots()
        }
        
        # Add user-specific plots for demo user
        demo_user_id = "demo_user"
        all_plots['user_progress'] = self.get_user_progress_plots(demo_user_id)
        
        return all_plots
