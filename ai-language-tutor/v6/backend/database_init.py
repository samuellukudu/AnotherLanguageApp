#!/usr/bin/env python3
"""
Database initialization script for AI Language Tutor
Run this script to create database tables
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import create_tables, drop_tables
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """Initialize database tables"""
    try:
        logger.info("Creating database tables...")
        await create_tables()
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def reset_database():
    """Reset database (drop and recreate tables)"""
    try:
        logger.info("Dropping existing tables...")
        await drop_tables()
        logger.info("Creating new tables...")
        await create_tables()
        logger.info("Database reset successfully!")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization for AI Language Tutor")
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Reset database (drop and recreate tables)"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        print("⚠️  WARNING: This will delete all existing data!")
        confirm = input("Are you sure you want to reset the database? (yes/no): ")
        if confirm.lower() == "yes":
            asyncio.run(reset_database())
        else:
            print("Database reset cancelled.")
    else:
        asyncio.run(init_database()) 