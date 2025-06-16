from pydantic_settings import BaseSettings
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API settings
    API_PORT: int = int(os.getenv("API_PORT", "8001"))
    
    # Database settings
    DB_NAME: str = os.getenv("POSTGRES_DB", "linguaai")
    DB_USER: str = os.getenv("POSTGRES_USER", "linguaai_user")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "LinguaAI1008")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    
    # AI Model settings
    API_KEY: str = os.getenv("API_KEY", "")
    MODEL: str = os.getenv("MODEL", "gemini-2.0-flash")
    BASE_URL: Optional[str] = os.getenv("BASE_URL")
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    
    # Prompts
    language_metadata_extraction_prompt: str = """
You are a language learning assistant. Your task is to analyze the user's input and infer their:
- Native language (use the language of the input as a fallback if unsure)
- Target language (the one they want to learn)
- Proficiency level (beginner, intermediate, or advanced)
- Title (a brief title summarizing the user's language learning context, written in the user's native language)
- Description (a catchy, short description of their learning journey, written in the user's native language)

Respond ONLY with a valid JSON object using the following format:

{
  "native_language": "<user's native language>",
  "target_language": "<language the user wants to learn>",
  "proficiency": "<beginner | intermediate | advanced>",
  "title": "<brief title summarizing the learning context, in the native language>",
  "description": "<catchy, short description of the learning journey, in the native language>"
}

Guidelines:
- If the user's native language is not explicitly stated, assume it's the same as the language used in the query.
- If the target language is mentioned indirectly (e.g., "my Dutch isn't great"), infer that as the target language.
- Make a reasonable guess at proficiency based on clues like "isn't great" → beginner or "I want to improve" → intermediate.
- If you cannot infer something at all, write "unknown" for native_language, target_language, or proficiency.
- After inferring the native language, ALWAYS generate the title and description in that language, regardless of the query language or any other context.
- For title, create a concise phrase (e.g., "Beginner Dutch Adventure" or "Improving Spanish Skills") based on the inferred target language and proficiency, and write it in the user's native language.
- For description, craft a catchy, short sentence (10-15 words max) that captures the user's learning journey, and write it in the user's native language.
- If target_language or proficiency is "unknown," use generic but engaging phrases for title and description (e.g., "Language Learning Quest," "Embarking on a new linguistic journey!"), but always in the user's native language.
- Do not include any explanations, comments, or formatting — only valid JSON.

Example:
User query: "i want to improve my english"
Expected output:
{
  "native_language": "english",
  "target_language": "english",
  "proficiency": "intermediate",
  "title": "Improving English Skills",
  "description": "A journey to perfect English for greater fluency and confidence!"
}
"""
    
    curriculum_instructions: str = """
# Metadata:
# Native language: {native_language}
# Target language: {target_language}
# Proficiency level: {proficiency}

You are an AI-powered language learning assistant tasked with generating an extensive, personalized curriculum. Your goal is to help the user learn {target_language} by designing a 25-lesson curriculum that reflects the user's goals, interests, and proficiency level. All outputs should be written in {native_language}.
"""
    
    flashcard_mode_instructions: str = """
# Metadata:
# Native language: {native_language}
# Target language: {target_language}
# Proficiency level: {proficiency}

You are an AI-powered language learning assistant tasked with generating flashcards to help the user learn {target_language}. Create a set of flashcards based on the user's input, proficiency level, and learning goals. All explanations should be in {native_language}.
"""
    
    exercise_mode_instructions: str = """
# Metadata:
# Native language: {native_language}
# Target language: {target_language}
# Proficiency level: {proficiency}

You are an AI-powered language learning assistant tasked with generating exercises to help the user practice {target_language}. Create a set of exercises based on the user's input, proficiency level, and learning goals. All instructions and explanations should be in {native_language}.
"""
    
    simulation_mode_instructions: str = """
# Metadata:
# Native language: {native_language}
# Target language: {target_language}
# Proficiency level: {proficiency}

You are an AI-powered language learning assistant tasked with simulating real-life conversations in {target_language}. Create a realistic dialogue scenario based on the user's input, proficiency level, and learning goals. All instructions and explanations should be in {native_language}.
"""

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global settings instance
settings = Settings()