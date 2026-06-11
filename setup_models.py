#!/usr/bin/env python3
"""
Setup script for downloading and preparing models
"""

import os
import logging
from transformers import BertTokenizer, BertModel
import torch
import torchvision.models as models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_models():
    """Download and setup required models"""
    try:
        logger.info("Setting up models directory...")
        os.makedirs("models", exist_ok=True)
        
        logger.info("Downloading BERT model...")
        # Download BERT tokenizer and model
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        model = BertModel.from_pretrained('bert-base-uncased')
        
        # Save models
        tokenizer.save_pretrained("models/bert-base-uncased")
        model.save_pretrained("models/bert-base-uncased")
        
        logger.info("Downloading ResNet model...")
        # Download ResNet
        resnet = models.resnet50(pretrained=True)
        torch.save(resnet.state_dict(), "models/resnet50.pth")
        
        logger.info("Downloading DenseNet model...")
        # Download DenseNet
        densenet = models.densenet121(pretrained=True)
        torch.save(densenet.state_dict(), "models/densenet121.pth")
        
        logger.info("All models downloaded successfully!")
        
    except Exception as e:
        logger.error(f"Error setting up models: {str(e)}")
        raise

if __name__ == "__main__":
    setup_models()
