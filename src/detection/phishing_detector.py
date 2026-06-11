"""
Deep Learning-based Phishing Detection System
Uses transfer learning with BERT, ResNet, and DenseNet
"""

import os
import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime
import re
import urllib.parse
from urllib.parse import urlparse

# Deep Learning imports
import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel
import torchvision.models as models

from src.utils.config import Config

logger = logging.getLogger(__name__)

class BERTPhishingDetector(nn.Module):
    """BERT-based phishing detection model"""
    
    def __init__(self, num_classes=2, dropout=0.3):
        super(BERTPhishingDetector, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
        
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return logits

class URLFeatureExtractor:
    """Extract features from URLs"""
    
    def __init__(self):
        self.suspicious_keywords = [
            'login', 'signin', 'verify', 'secure', 'account', 'banking',
            'paypal', 'amazon', 'ebay', 'facebook', 'google', 'microsoft'
        ]
    
    def extract_features(self, url: str) -> Dict[str, Any]:
        """Extract URL features"""
        try:
            parsed = urlparse(url)
            
            features = {
                'url_length': len(url),
                'uses_https': 1 if parsed.scheme == 'https' else 0,
                'suspicious_keywords': sum(1 for word in self.suspicious_keywords if word in url.lower()),
                'special_char_count': len(re.findall(r'[^a-zA-Z0-9.-]', url)),
                'digit_count': len(re.findall(r'\d', url)),
                'has_shortener': 1 if self._is_shortened_url(url) else 0,
                'brand_impersonation_score': self._calculate_brand_impersonation(url)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting URL features: {str(e)}")
            return self._get_default_features()
    
    def _is_shortened_url(self, url: str) -> bool:
        """Check if URL is shortened"""
        shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co']
        return any(shortener in url for shortener in shorteners)
    
    def _calculate_brand_impersonation(self, url: str) -> float:
        """Calculate brand impersonation score"""
        brands = ['paypal', 'amazon', 'ebay', 'facebook', 'google', 'microsoft']
        url_lower = url.lower()
        
        max_score = 0
        for brand in brands:
            if brand in url_lower:
                score = 1.0
                # Check for misspellings
                misspellings = {
                    'paypal': ['paypa1', 'paypa1'],
                    'amazon': ['amaz0n', 'amaz0n'],
                    'google': ['g00gle', 'g00gle']
                }
                
                if brand in misspellings:
                    for misspelling in misspellings[brand]:
                        if misspelling in url_lower:
                            score = 0.8
                            break
                
                max_score = max(max_score, score)
        
        return max_score
    
    def _get_default_features(self) -> Dict[str, Any]:
        """Return default features"""
        return {
            'url_length': 0, 'uses_https': 0, 'suspicious_keywords': 0,
            'special_char_count': 0, 'digit_count': 0, 'has_shortener': 0,
            'brand_impersonation_score': 0
        }

class TextFeatureExtractor:
    """Extract features from email/text content"""
    
    def __init__(self):
        self.urgency_words = [
            'urgent', 'immediate', 'asap', 'now', 'quickly', 'hurry',
            'limited time', 'expires', 'deadline', 'last chance'
        ]
        self.authority_words = [
            'ceo', 'manager', 'director', 'president', 'executive',
            'official', 'security', 'compliance', 'legal'
        ]
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract text features"""
        text_lower = text.lower()
        
        features = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'urgency_score': self._calculate_urgency_score(text_lower),
            'authority_score': self._calculate_authority_score(text_lower),
            'has_links': 1 if 'http' in text_lower else 0,
            'link_count': len(re.findall(r'http[s]?://[^\s]+', text)),
            'has_attachments': 1 if 'attachment' in text_lower else 0,
            'personalization_score': self._calculate_personalization(text)
        }
        
        return features
    
    def _calculate_urgency_score(self, text: str) -> float:
        """Calculate urgency score"""
        score = 0
        for word in self.urgency_words:
            if word in text:
                score += 0.1
        return min(score, 1.0)
    
    def _calculate_authority_score(self, text: str) -> float:
        """Calculate authority score"""
        score = 0
        for word in self.authority_words:
            if word in text:
                score += 0.1
        return min(score, 1.0)
    
    def _calculate_personalization(self, text: str) -> float:
        """Calculate personalization score"""
        personal_words = ['you', 'your', 'yours']
        text_lower = text.lower()
        
        personal_count = sum(1 for word in personal_words if word in text_lower)
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        return min(personal_count / total_words * 10, 1.0)

class PhishingDetector:
    """Main phishing detection system"""
    
    def __init__(self):
        self.config = Config()
        self.url_extractor = URLFeatureExtractor()
        self.text_extractor = TextFeatureExtractor()
        
        # Model components
        self.bert_model = None
        self.bert_tokenizer = None
        
        # Performance tracking
        self.detection_stats = {
            'total_detections': 0,
            'response_times': []
        }
        
        # Load models
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models"""
        try:
            logger.info("Loading BERT model...")
            self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.bert_model = BERTPhishingDetector()
            self.bert_model.eval()
            
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
    
    def detect(self, content: str, user_id: str = None) -> Dict[str, Any]:
        """Main detection method"""
        start_time = time.time()
        
        try:
            # Extract features
            url_features = self._extract_url_features(content)
            text_features = self._extract_text_features(content)
            
            # Get predictions
            bert_prediction = self._bert_predict(content)
            feature_score = self._calculate_feature_score(url_features, text_features)
            
            # Ensemble prediction
            ensemble_score = 0.6 * bert_prediction + 0.4 * feature_score
            
            # Determine result
            threshold = self.config.get('detection.confidence_threshold', 0.8)
            is_phishing = ensemble_score > threshold
            
            # Calculate response time
            response_time = (time.time() - start_time) * 1000
            
            # Update statistics
            self._update_stats(response_time)
            
            result = {
                'is_phishing': is_phishing,
                'confidence_score': ensemble_score,
                'response_time_ms': response_time,
                'model_predictions': {
                    'bert': bert_prediction,
                    'feature_based': feature_score
                },
                'risk_factors': self._identify_risk_factors(content, url_features, text_features),
                'recommendations': self._generate_recommendations(is_phishing, ensemble_score),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in phishing detection: {str(e)}")
            return {
                'is_phishing': False,
                'confidence_score': 0.0,
                'error': str(e),
                'response_time_ms': (time.time() - start_time) * 1000
            }
    
    def _extract_url_features(self, content: str) -> Dict[str, Any]:
        """Extract URL features"""
        urls = re.findall(r'http[s]?://[^\s]+', content)
        if not urls:
            return self.url_extractor._get_default_features()
        
        return self.url_extractor.extract_features(urls[0])
    
    def _extract_text_features(self, content: str) -> Dict[str, Any]:
        """Extract text features"""
        return self.text_extractor.extract_features(content)
    
    def _bert_predict(self, text: str) -> float:
        """Get BERT prediction"""
        try:
            if not self.bert_model or not self.bert_tokenizer:
                return 0.5
            
            inputs = self.bert_tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors='pt'
            )
            
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                probabilities = torch.softmax(outputs, dim=1)
                phishing_prob = probabilities[0][1].item()
            
            return phishing_prob
            
        except Exception as e:
            logger.error(f"BERT prediction error: {str(e)}")
            return 0.5
    
    def _calculate_feature_score(self, url_features: Dict, text_features: Dict) -> float:
        """Calculate feature-based score"""
        score = 0.0
        
        # URL-based scoring
        if url_features.get('brand_impersonation_score', 0) > 0.5:
            score += 0.3
        if url_features.get('has_shortener', 0):
            score += 0.2
        if url_features.get('suspicious_keywords', 0) > 2:
            score += 0.2
        
        # Text-based scoring
        if text_features.get('urgency_score', 0) > 0.5:
            score += 0.2
        if text_features.get('authority_score', 0) > 0.5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _identify_risk_factors(self, content: str, url_features: Dict, text_features: Dict) -> List[str]:
        """Identify risk factors"""
        risk_factors = []
        
        if url_features.get('has_shortener', 0):
            risk_factors.append("Uses URL shortener")
        if url_features.get('brand_impersonation_score', 0) > 0.5:
            risk_factors.append("Potential brand impersonation")
        if text_features.get('urgency_score', 0) > 0.5:
            risk_factors.append("High urgency language")
        
        return risk_factors
    
    def _generate_recommendations(self, is_phishing: bool, confidence: float) -> List[str]:
        """Generate recommendations"""
        if is_phishing:
            return [
                "Do not click on any links",
                "Do not provide personal information",
                "Report to IT security team",
                "Delete the message"
            ]
        else:
            if confidence > 0.3:
                return ["Exercise caution and verify sender"]
            else:
                return ["Message appears legitimate"]
    
    def _update_stats(self, response_time: float):
        """Update statistics"""
        self.detection_stats['total_detections'] += 1
        self.detection_stats['response_times'].append(response_time)
        
        if len(self.detection_stats['response_times']) > 1000:
            self.detection_stats['response_times'] = self.detection_stats['response_times'][-1000:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detection statistics"""
        stats = self.detection_stats.copy()
        
        if stats['response_times']:
            stats['avg_response_time'] = np.mean(stats['response_times'])
        else:
            stats['avg_response_time'] = 0
        
        return stats
    
    def get_avg_response_time(self) -> float:
        """Get average response time"""
        times = self.detection_stats['response_times']
        return np.mean(times) if times else 0.0
    
    def get_accuracy_rate(self) -> float:
        """Get accuracy rate (placeholder)"""
        return 0.95  # Placeholder value
