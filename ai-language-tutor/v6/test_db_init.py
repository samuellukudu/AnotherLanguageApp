#!/usr/bin/env python3
"""
Database Initialization Test Script
Tests the database initialization system
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.db_init import db_initializer

async def test_database_initialization():
    """Test the database initialization system"""
    
    print("🗄️  AI Language Tutor v6 - Database Initialization Test")
    print("=" * 60)
    
    # Test 1: Check current database status
    print("=== Test 1: Current Database Status ===")
    health_check = await db_initializer.check_database_health()
    
    print(f"Database exists: {'✅' if health_check['database_exists'] else '❌'}")
    print(f"Database accessible: {'✅' if health_check['database_accessible'] else '❌'}")
    print(f"Schema loaded: {'✅' if health_check['schema_loaded'] else '❌'}")
    print(f"Tables exist: {'✅' if health_check['tables_exist'] else '❌'}")
    print(f"Views exist: {'✅' if health_check['views_exist'] else '❌'}")
    print(f"Can write: {'✅' if health_check['can_write'] else '❌'}")
    
    if health_check['record_count']:
        print(f"Record counts: {health_check['record_count']}")
    
    if health_check['errors']:
        print(f"Errors: {health_check['errors']}")
    
    # Test 2: Initialize database
    print("\n=== Test 2: Database Initialization ===")
    init_result = await db_initializer.initialize_database()
    
    print(f"Initialization success: {'✅' if init_result['success'] else '❌'}")
    print(f"Action taken: {init_result['action_taken']}")
    
    if init_result['errors']:
        print(f"Errors: {init_result['errors']}")
    
    # Test 3: Final health check
    print("\n=== Test 3: Final Health Check ===")
    final_health = await db_initializer.check_database_health()
    
    all_good = (
        final_health['database_exists'] and
        final_health['schema_loaded'] and
        final_health['can_write']
    )
    
    print(f"Overall status: {'✅ HEALTHY' if all_good else '❌ UNHEALTHY'}")
    print(f"Database path: {db_initializer.db_path}")
    print(f"Schema path: {db_initializer.schema_path}")
    
    if final_health['record_count']:
        print(f"Final record counts: {final_health['record_count']}")
    
    # Test 4: Database file info
    print("\n=== Test 4: Database File Information ===")
    if os.path.exists(db_initializer.db_path):
        file_size = os.path.getsize(db_initializer.db_path)
        print(f"Database file size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"Database file path: {os.path.abspath(db_initializer.db_path)}")
    else:
        print("❌ Database file does not exist")
    
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 Database initialization test PASSED!")
        print("Your database is ready for use.")
        print("\nNext steps:")
        print("1. Run: uvicorn backend.main:app --reload")
        print("2. Test: curl http://localhost:8000/health")
    else:
        print("❌ Database initialization test FAILED!")
        print("Check the errors above and fix any issues.")
    
    return all_good

async def test_database_repair():
    """Test database repair functionality"""
    print("\n" + "=" * 60)
    print("🔧 Testing Database Repair Functionality")
    print("=" * 60)
    
    repair_result = await db_initializer.repair_database()
    
    print(f"Repair success: {'✅' if repair_result['success'] else '❌'}")
    print(f"Repairs attempted: {repair_result['repairs_attempted']}")
    
    if repair_result['errors']:
        print(f"Repair errors: {repair_result['errors']}")
    
    return repair_result['success']

async def main():
    """Run all database tests"""
    try:
        # Test basic initialization
        init_success = await test_database_initialization()
        
        # If initialization failed, try repair
        if not init_success:
            print("\nInitialization failed, testing repair...")
            repair_success = await test_database_repair()
            
            if repair_success:
                print("Repair successful, re-testing initialization...")
                init_success = await test_database_initialization()
        
        return init_success
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 