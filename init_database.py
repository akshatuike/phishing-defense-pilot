#!/usr/bin/env python3
"""
Database initialization script
"""

import os
import logging
from src.database.user_manager import UserManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with sample data"""
    try:
        logger.info("Initializing database...")
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
        
        # Initialize user manager
        user_manager = UserManager()
        
        # Create sample admin user
        admin_result = user_manager.create_user(
            username="admin",
            email="admin@phishing-defense.com",
            password="admin123",
            role="admin"
        )
        
        if 'error' not in admin_result:
            logger.info("Admin user created successfully")
        else:
            logger.warning(f"Admin user creation: {admin_result['error']}")
        
        # Create sample regular user
        user_result = user_manager.create_user(
            username="demo_user",
            email="demo@example.com",
            password="demo123",
            role="user"
        )
        
        if 'error' not in user_result:
            logger.info("Demo user created successfully")
        else:
            logger.warning(f"Demo user creation: {user_result['error']}")
        
        logger.info("Database initialization completed!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()
