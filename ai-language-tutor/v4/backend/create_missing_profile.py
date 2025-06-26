#!/usr/bin/env python3
"""
Script to create missing user profiles for users who exist in Supabase Auth
but don't have profiles in the users table.
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append('backend')

from utils.supabase_client import supabase

def create_missing_user_profile(user_id: str, email: str, username: str = None):
    """
    Create a user profile in the users table
    """
    try:
        # Check if profile already exists
        existing = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if existing.data and len(existing.data) > 0:
            print(f"✅ Profile already exists for user {user_id}")
            return existing.data[0]
        
        # Try to create the profile with current schema
        # First, let's check what columns exist
        try:
            # Try with the new schema (includes username, xp, streak, preferences)
            profile_data = {
                "id": user_id,
                "email": email,
                "username": username or email.split('@')[0],
                "xp": 0,
                "streak": 0,
                "preferences": {}
            }
            
            result = supabase.table("users").insert(profile_data).execute()
            
            if result.data and len(result.data) > 0:
                print(f"✅ Created profile with full schema for user {user_id}")
                return result.data[0]
        
        except Exception as schema_error:
            print(f"⚠️ Full schema failed, trying minimal schema: {schema_error}")
            
            # Fallback to minimal schema (just id and email)
            minimal_profile = {
                "id": user_id,
                "email": email
            }
            
            result = supabase.table("users").insert(minimal_profile).execute()
            
            if result.data and len(result.data) > 0:
                print(f"✅ Created minimal profile for user {user_id}")
                print("⚠️ Please run the database migration script to add missing columns")
                return result.data[0]
        
        print(f"❌ Failed to create profile for user {user_id}")
        return None
            
    except Exception as e:
        print(f"❌ Error creating profile for user {user_id}: {e}")
        return None

def main():
    """
    Main function to create missing user profile
    """
    load_dotenv()
    
    # The user ID from the JWT token
    user_id = "de126f47-59e8-49b3-abe4-6c409a48b773"
    email = "samu01@gmail.com"  # From the JWT token
    username = "samu01"  # From the JWT token
    
    print(f"🔍 Checking profile for user: {user_id}")
    print(f"📧 Email: {email}")
    print(f"👤 Username: {username}")
    print()
    
    # Create the missing profile
    profile = create_missing_user_profile(user_id, email, username)
    
    if profile:
        print("🎉 User profile is now ready!")
        print(f"Profile: {profile}")
        print("\n📋 Next steps:")
        print("1. Run the database migration script in Supabase SQL Editor")
        print("2. Test the /users/me endpoint again")
    else:
        print("💥 Failed to create user profile")
        print("\n🔧 Manual steps:")
        print("1. Run the update_database_schema.sql script in Supabase")
        print("2. Try this script again")

if __name__ == "__main__":
    main() 