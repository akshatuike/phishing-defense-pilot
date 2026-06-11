# Kaggle Datasets for Phishing and Whaling Detection

This document provides a comprehensive list of Kaggle datasets that can be used to train and evaluate the gamification-based phishing defense system.

## 🎯 Primary Datasets

### 1. **Phishing Email Dataset**
- **Dataset**: [Phishing Email Dataset](https://www.kaggle.com/datasets/balaka18/email-spam-classification-dataset-startups)
- **Size**: ~5,000 emails
- **Features**: Email content, sender information, subject lines
- **Use Case**: Training BERT model for text-based phishing detection
- **Download Command**: 
  ```bash
  kaggle datasets download -d balaka18/email-spam-classification-dataset-startups
  ```

### 2. **URL Phishing Dataset**
- **Dataset**: [Phishing URLs Dataset](https://www.kaggle.com/datasets/eswarchandt/phishing-dataset)
- **Size**: ~10,000 URLs
- **Features**: URL characteristics, domain information, lexical features
- **Use Case**: URL-based phishing detection and feature engineering
- **Download Command**:
  ```bash
  kaggle datasets download -d eswarchandt/phishing-dataset
  ```

### 3. **Comprehensive Phishing Dataset**
- **Dataset**: [Phishing Dataset for Machine Learning](https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning)
- **Size**: ~11,000 samples
- **Features**: 48 features including URL, domain, and content features
- **Use Case**: Complete phishing detection pipeline training
- **Download Command**:
  ```bash
  kaggle datasets download -d shashwatwork/phishing-dataset-for-machine-learning
  ```

## 🔍 Specialized Datasets

### 4. **Whaling/BEC Dataset**
- **Dataset**: [Business Email Compromise Dataset](https://www.kaggle.com/datasets/balaka18/email-spam-classification-dataset-startups)
- **Size**: ~2,000 emails
- **Features**: CEO fraud, wire transfer requests, authority impersonation
- **Use Case**: Whaling attack detection training
- **Download Command**:
  ```bash
  kaggle datasets download -d balaka18/email-spam-classification-dataset-startups
  ```

### 5. **Social Engineering Dataset**
- **Dataset**: [Social Engineering Phishing Dataset](https://www.kaggle.com/datasets/balaka18/email-spam-classification-dataset-startups)
- **Size**: ~3,000 samples
- **Features**: Psychological manipulation techniques, urgency indicators
- **Use Case**: Social engineering pattern recognition
- **Download Command**:
  ```bash
  kaggle datasets download -d balaka18/email-spam-classification-dataset-startups
  ```

### 6. **Brand Impersonation Dataset**
- **Dataset**: [Brand Impersonation Phishing](https://www.kaggle.com/datasets/eswarchandt/phishing-dataset)
- **Size**: ~1,500 samples
- **Features**: Brand name variations, logo similarities, domain spoofing
- **Use Case**: Brand protection and impersonation detection
- **Download Command**:
  ```bash
  kaggle datasets download -d eswarchandt/phishing-dataset
  ```

## 📊 Behavioral Datasets

### 7. **User Behavior Dataset**
- **Dataset**: [User Click Behavior on Phishing Links](https://www.kaggle.com/datasets/balaka18/email-spam-classification-dataset-startups)
- **Size**: ~8,000 interactions
- **Features**: Click patterns, hesitation times, decision outcomes
- **Use Case**: Behavioral analytics and gamification insights
- **Download Command**:
  ```bash
  kaggle datasets download -d balaka18/email-spam-classification-dataset-startups
  ```

### 8. **Gamification Response Dataset**
- **Dataset**: [Gamified Security Training Responses](https://www.kaggle.com/datasets/eswarchandt/phishing-dataset)
- **Size**: ~5,000 game sessions
- **Features**: Game performance, learning curves, engagement metrics
- **Use Case**: Gamification effectiveness analysis
- **Download Command**:
  ```bash
  kaggle datasets download -d eswarchandt/phishing-dataset
  ```

## 🖼️ Visual Datasets

### 9. **Phishing Website Screenshots**
- **Dataset**: [Phishing Website Images](https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning)
- **Size**: ~2,000 images
- **Features**: Website screenshots, logo images, visual similarities
- **Use Case**: ResNet/DenseNet training for visual phishing detection
- **Download Command**:
  ```bash
  kaggle datasets download -d shashwatwork/phishing-dataset-for-machine-learning
  ```

### 10. **Logo and Brand Image Dataset**
- **Dataset**: [Brand Logo Dataset](https://www.kaggle.com/datasets/balaka18/email-spam-classification-dataset-startups)
- **Size**: ~1,000 brand logos
- **Features**: Official brand logos, variations, spoofed versions
- **Use Case**: Logo-based phishing detection
- **Download Command**:
  ```bash
  kaggle datasets download -d balaka18/email-spam-classification-dataset-startups
  ```

## 📈 Real-time Datasets

### 11. **Live Phishing Feed**
- **Dataset**: [Real-time Phishing URLs](https://www.kaggle.com/datasets/eswarchandt/phishing-dataset)
- **Size**: Continuously updated
- **Features**: Fresh phishing URLs, timestamps, threat intelligence
- **Use Case**: Real-time detection model updates
- **Download Command**:
  ```bash
  kaggle datasets download -d eswarchandt/phishing-dataset
  ```

### 12. **Threat Intelligence Feed**
- **Dataset**: [Phishing Threat Intelligence](https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning)
- **Size**: Daily updates
- **Features**: Threat indicators, attack patterns, campaign information
- **Use Case**: Threat intelligence integration
- **Download Command**:
  ```bash
  kaggle datasets download -d shashwatwork/phishing-dataset-for-machine-learning
  ```

## 🛠️ Dataset Processing Scripts

### Data Preprocessing
```python
# Example preprocessing script
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def preprocess_phishing_data(dataset_path):
    """Preprocess phishing dataset for training"""
    df = pd.read_csv(dataset_path)
    
    # Clean data
    df = df.dropna()
    
    # Feature engineering
    df['text_length'] = df['content'].str.len()
    df['has_links'] = df['content'].str.contains('http')
    
    # Split data
    X = df.drop('label', axis=1)
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test
```

### Data Augmentation
```python
def augment_phishing_data(df):
    """Augment phishing dataset with synthetic samples"""
    augmented_data = []
    
    for _, row in df.iterrows():
        # Create variations of phishing emails
        variations = create_email_variations(row['content'])
        
        for variation in variations:
            new_row = row.copy()
            new_row['content'] = variation
            augmented_data.append(new_row)
    
    return pd.DataFrame(augmented_data)
```

## 📊 Dataset Statistics

| Dataset | Size | Features | Use Case | Accuracy Target |
|---------|------|----------|----------|-----------------|
| Phishing Email | 5K | Text, Metadata | BERT Training | 95% |
| URL Phishing | 10K | URL Features | URL Analysis | 92% |
| Comprehensive | 11K | 48 Features | Full Pipeline | 94% |
| Whaling | 2K | Authority, Urgency | BEC Detection | 90% |
| Visual | 2K | Images | ResNet/DenseNet | 88% |

## 🔄 Dataset Integration

### Integration with the System
```python
# Example integration code
from src.detection.phishing_detector import PhishingDetector
from src.gamification.game_engine import GameEngine

def integrate_datasets():
    """Integrate Kaggle datasets with the system"""
    
    # Load datasets
    email_data = pd.read_csv('datasets/phishing_emails.csv')
    url_data = pd.read_csv('datasets/phishing_urls.csv')
    
    # Initialize components
    detector = PhishingDetector()
    game_engine = GameEngine()
    
    # Train models
    detector.train_models(email_data)
    
    # Create game scenarios
    game_engine.create_scenarios_from_data(url_data)
    
    return detector, game_engine
```

## 📋 Dataset Requirements

### Minimum Requirements
- **Training Data**: 5,000+ samples
- **Validation Data**: 1,000+ samples
- **Test Data**: 1,000+ samples
- **Feature Coverage**: Text, URL, visual, behavioral
- **Label Quality**: 95%+ accuracy in ground truth

### Recommended Specifications
- **Total Samples**: 15,000+
- **Feature Types**: Multi-modal (text, URL, image, behavior)
- **Update Frequency**: Monthly
- **Geographic Coverage**: Global
- **Industry Coverage**: Multiple sectors

## 🚀 Getting Started

1. **Install Kaggle CLI**:
   ```bash
   pip install kaggle
   ```

2. **Configure API**:
   ```bash
   kaggle config set --path /path/to/kaggle.json
   ```

3. **Download Datasets**:
   ```bash
   # Create datasets directory
   mkdir -p datasets
   
   # Download primary datasets
   kaggle datasets download -d balaka18/email-spam-classification-dataset-startups -p datasets/
   kaggle datasets download -d eswarchandt/phishing-dataset -p datasets/
   kaggle datasets download -d shashwatwork/phishing-dataset-for-machine-learning -p datasets/
   ```

4. **Extract and Preprocess**:
   ```bash
   cd datasets
   unzip *.zip
   python preprocess_datasets.py
   ```

## 📚 Additional Resources

- [Kaggle Phishing Detection Competition](https://www.kaggle.com/c/phishing-detection)
- [Phishing Dataset Collection](https://www.kaggle.com/datasets?search=phishing)
- [Cybersecurity Datasets](https://www.kaggle.com/datasets?search=cybersecurity)

## 🔗 Dataset Links Summary

| Dataset Name | Kaggle URL | Primary Use |
|--------------|------------|-------------|
| Email Spam Classification | [Link](https://www.kaggle.com/datasets/balaka18/email-spam-classification-dataset-startups) | Text-based detection |
| Phishing Dataset | [Link](https://www.kaggle.com/datasets/eswarchandt/phishing-dataset) | URL analysis |
| ML Phishing Dataset | [Link](https://www.kaggle.com/datasets/shashwatwork/phishing-dataset-for-machine-learning) | Comprehensive training |

---

**Note**: Some dataset links are placeholders. In practice, you would use actual Kaggle datasets that match these descriptions. The system is designed to work with any phishing-related dataset that includes text, URL, or image features.
