import os
import asyncio
import dspy
from typing import Literal, List, Union
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
import sqlite3
import uuid
import sys
import json

load_dotenv()
lm = dspy.LM(f"openai/{os.getenv('MODEL')}", api_key=os.getenv("API_KEY"), api_base=os.getenv("BASE_URL"))
dspy.configure(lm=lm)

class LanguageMetadata(BaseModel):
    native_language: str = Field(description="Native language of the user")
    target_language: str = Field(description="Target language the user wants to learn")
    proficiency: Literal["beginner", "intermediate", "advanced"] = Field(description="Proficiency level of the user")
    title: str = Field(description="Brief title summarizing the learning context, in the native language")
    description: str = Field(description="Catchy, short description of the learning journey (10-15 words max), in the native language")
    
    @field_validator('description')
    @classmethod
    def validate_description_length(cls, v):
        word_count = len(v.split())
        if word_count > 15:
            raise ValueError('Description must be 15 words or less')
        return v

class ExtractMetadata(dspy.Signature):
    """
    Analyze user input and infer their native language, target language, proficiency level, 
    and generate a contextual title and description for their language learning journey.
    Use the language of the input as fallback for native language if unsure.
    Generate title and description in the user's native language.
    """
    query: str = dspy.InputField(desc="User input to analyze")
    metadata: LanguageMetadata = dspy.OutputField(desc="Extracted language learning metadata with title and description in native language")

class SubTopic(BaseModel):
    sub_topic: str = Field(description="Clear and practical lesson title in native language")
    keywords: List[str] = Field(description="1-3 high-level categories describing the lesson focus in native language", min_length=1, max_length=3)
    description: str = Field(description="One sentence explaining what the learner will achieve after completing the lesson, in native language")
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords_length(cls, v):
        if len(v) < 1 or len(v) > 3:
            raise ValueError('Keywords must contain 1-3 items')
        return v

class Curriculum(BaseModel):
    lesson_topic: str = Field(description="Overall learning theme in native language")
    sub_topics: List[SubTopic] = Field(description="List of exactly 5 sub-topics", min_length=5, max_length=5)
    
    @field_validator('sub_topics')
    @classmethod
    def validate_subtopics_count(cls, v):
        if len(v) != 5:
            raise ValueError('Curriculum must contain exactly 5 sub-topics')
        return v

class GenerateCurriculum(dspy.Signature):
    """
    Generate a personalized language learning curriculum with exactly 5 lessons that progress logically 
    from basic to advanced topics according to proficiency level. Each lesson should have a clear focus 
    and align with practical communication goals. Tailor vocabulary and sub-topics to the user's intended 
    use (work, travel, hobbies, daily life). All outputs must be in the user's native language.
    
    Choose a main theme relevant to the user's motivation for learning the target language.
    Sequence lessons to build from foundational to complex, specialized language use.
    Vary grammar, vocabulary, and communication functions to ensure comprehensive coverage.
    """
    query: str = dspy.InputField(desc="User input describing their learning context")
    native_language: str = dspy.InputField(desc="Native language of the user")
    target_language: str = dspy.InputField(desc="Target language the user wants to learn")
    proficiency_level: str = dspy.InputField(desc="Proficiency level: beginner, intermediate, or advanced")
    curriculum: Curriculum = dspy.OutputField(
         desc="Structured curriculum with lesson_topic and exactly 5 sub_topics, each with title, keywords, and description in native language"
     )

# Exercise System Models
class Exercise(BaseModel):
    sentence: str = Field(description="Fully contextualized sentence in target language containing one blank (___)")
    answer: str = Field(description="Single correct fill-in word/phrase in target language")
    choices: List[str] = Field(description="List of four total options in RANDOMIZED order (correct answer NOT always first), all in target language", min_length=4, max_length=4)
    explanation: str = Field(description="Concise 1-2 sentence rationale written ENTIRELY in the native language (no target language words) explaining why the correct answer fits")
    
    @field_validator('choices')
    @classmethod
    def validate_choices_count(cls, v):
        if len(v) != 4:
            raise ValueError('Choices must contain exactly 4 options')
        return v
    
    @field_validator('sentence')
    @classmethod
    def validate_sentence_has_blank(cls, v):
        if '___' not in v:
            raise ValueError('Sentence must contain exactly one blank (___)')
        if v.count('___') != 1:
            raise ValueError('Sentence must contain exactly one blank (___)')
        return v

class GenerateExercises(dspy.Signature):
    """
    Generate 5 cloze exercises with realistic scenarios.
    
    RULES:
    - Each sentence: EXACTLY ONE blank (___)
    - Four choices: one correct + three plausible distractors from same word class
    - RANDOMIZE choice order (correct answer should NOT always be first)
    - Context must make only one answer correct
    - Use concrete, specific scenarios (not generic templates)
    - Write ALL explanations in English ONLY (never use Chinese characters or any target language)
    
    COMPLEXITY BY LEVEL:
    - Beginner: High-frequency words, simple grammar
    - Intermediate: Mixed vocabulary, varied tenses
    - Advanced: Domain-specific terms, complex structures
    
    FORMAT: "At the market, she ___ fresh vegetables" ✓
    AVOID: "She ___ vegetables at the ___" ✗
    
    EXPLANATION FORMAT: Write explanations like "The correct answer is 'word' which means 'definition' in English. The other options don't fit the context."
    """
    lesson_content: str = dspy.InputField(desc="Structured lesson or topic description to base exercises on")
    native_language: str = dspy.InputField(desc="Native language for explanations")
    target_language: str = dspy.InputField(desc="Target language for sentences, answers, and choices")
    proficiency_level: str = dspy.InputField(desc="Proficiency level: beginner, intermediate, or advanced")
    exercises: List[Exercise] = dspy.OutputField(desc="List of exactly 5 cloze-style exercises. Each sentence must contain EXACTLY ONE blank (___) and four answer choices. All explanations must be written entirely in the native language.")

# Flashcard System Models
class Flashcard(BaseModel):
    word: str = Field(description="Key word or phrase in target language drawn from the lesson")
    definition: str = Field(description="Learner-friendly explanation in native language")
    example: str = Field(description="Clear, natural sentence in target language demonstrating the word in context with the lesson")

class GenerateFlashcards(dspy.Signature):
    """
    Generate exactly 5 personalized flashcards from lesson-based content to help users learn 
    rapidly. Identify new or useful vocabulary terms and extract contextually relevant, 
    domain-specific language that reflects the lesson's themes and purpose.
    
    Select terms that are novel, useful, and not overly repetitive within the lesson.
    Prioritize vocabulary learners are likely to encounter in real-world usage.
    Adjust complexity based on proficiency: beginner (high-frequency, essential words), 
    intermediate (topic-specific terms, collocations), advanced (nuanced, idiomatic, technical vocab).
    Ensure example sentences are directly related to input content and sound natural.
    """
    lesson_content: str = dspy.InputField(desc="Structured lesson input (text, dialogue, or vocabulary list)")
    native_language: str = dspy.InputField(desc="Native language for definitions")
    target_language: str = dspy.InputField(desc="Target language for vocabulary and examples")
    proficiency_level: str = dspy.InputField(desc="Proficiency level: beginner, intermediate, or advanced")
    flashcards: List[Flashcard] = dspy.OutputField(desc="List of exactly 5 flashcards with word, definition, and contextual example")

# Simulation/Story System Models
class StorySegment(BaseModel):
    speaker: str = Field(description="Named or role-based character label in native language (e.g., 'Narrator', 'Captain Li', 'The Botanist')")
    target_language_text: str = Field(description="Sentence or dialogue line in target language")
    base_language_translation: str = Field(description="Simple, clear translation in native language")

class Story(BaseModel):
    title: str = Field(description="Engaging title in native language")
    setting: str = Field(description="Brief setup paragraph in native language explaining the story's background and relevance")
    content: List[StorySegment] = Field(description="List of exactly 10 story segments", min_length=10, max_length=10)
    
    @field_validator('content')
    @classmethod
    def validate_content_count(cls, v):
        if len(v) != 10:
            raise ValueError('Story must contain exactly 10 segments')
        return v

class GenerateStory(dspy.Signature):
    """
    Generate short, engaging stories or dialogues to make language learning enjoyable, memorable, 
    and relevant. Stories must reflect the user's interests, profession, or hobbies, and align 
    with their learning level.
    
    Personalize characters, setting, and vocabulary based on the specified topic or domain.
    Make stories both educational and entertaining with natural-sounding language.
    Match complexity to proficiency: beginner (simple grammar, short sentences, high-frequency vocab), 
    intermediate (natural flow, basic narrative devices, challenging vocab), 
    advanced (complex structures, idiomatic expressions, domain-specific language).
    
    Make stories fun, dramatic, or surprising to increase engagement while avoiding clichés.
    Vary tone and structure depending on theme (suspenseful for mystery, humorous for slice-of-life).
    Provide clear translations to aid comprehension.
    """
    topic_or_domain: str = dspy.InputField(desc="User-provided lesson topic, theme, or domain of interest")
    native_language: str = dspy.InputField(desc="Native language for explanations, setup, and translations")
    target_language: str = dspy.InputField(desc="Target language for dialogue and narration")
    proficiency_level: str = dspy.InputField(desc="Proficiency level: beginner, intermediate, or advanced")
    story: Story = dspy.OutputField(desc="Complete story with title, setting, and exactly 10 segments with speaker, target language text, and translation")

# Test the complete language learning system
query = "looking for a job as a structural engineer in Berlin"

# Extract metadata
metadata_module = dspy.Predict(ExtractMetadata)
metadata_result = metadata_module(query=query)
print("=== METADATA ===")
print(f"Native Language: {metadata_result.metadata.native_language}")
print(f"Target Language: {metadata_result.metadata.target_language}")
print(f"Proficiency: {metadata_result.metadata.proficiency}")
print(f"Title: {metadata_result.metadata.title}")
print(f"Description: {metadata_result.metadata.description}")

# Generate curriculum
curriculum_module = dspy.Predict(GenerateCurriculum)
curriculum = curriculum_module(
    query=query, 
    native_language=metadata_result.metadata.native_language, 
    target_language=metadata_result.metadata.target_language, 
    proficiency_level=metadata_result.metadata.proficiency
)
print("\n=== CURRICULUM ===")
print(f"Lesson Topic: {curriculum.curriculum.lesson_topic}")
print("\nSub-topics:")
for i, sub_topic in enumerate(curriculum.curriculum.sub_topics, 1):
    print(f"  {i}. {sub_topic.sub_topic}")
    print(f"     Keywords: {', '.join(sub_topic.keywords)}")
    print(f"     Description: {sub_topic.description}")
    print()

lesson = curriculum.curriculum.sub_topics[3]

exercise_module = dspy.Predict(GenerateExercises)
exercises = exercise_module(
    lesson_content=lesson.sub_topic,
    native_language=metadata_result.metadata.native_language,
    target_language=metadata_result.metadata.target_language,
    proficiency_level=metadata_result.metadata.proficiency
)
print("=== EXERCISES ===")
for i, exercise in enumerate(exercises.exercises, 1):
    print(f"Exercise {i}:")
    print(f"  Sentence: {exercise.sentence}")
    print(f"  Answer: {exercise.answer}")
    print(f"  Choices: {', '.join(exercise.choices)}")
    print(f"  Explanation: {exercise.explanation}")
    print()

# Generate flashcards
flashcard_module = dspy.Predict(GenerateFlashcards)
flashcards = flashcard_module(
    lesson_content=lesson.sub_topic,
    native_language=metadata_result.metadata.native_language,
    target_language=metadata_result.metadata.target_language,
    proficiency_level=metadata_result.metadata.proficiency
)
print("=== FLASHCARDS ===")
for i, flashcard in enumerate(flashcards.flashcards, 1):
    print(f"Flashcard {i}:")
    print(f"  Word: {flashcard.word}")
    print(f"  Definition: {flashcard.definition}")
    print(f"  Example: {flashcard.example}")
    print()

# Generate story
story_module = dspy.Predict(GenerateStory)
story = story_module(
    topic_or_domain="greetings and introductions in Beijing",
    native_language=metadata_result.metadata.native_language,
    target_language=metadata_result.metadata.target_language,
    proficiency_level=metadata_result.metadata.proficiency
)
print("=== STORY ===")
print(f"Title: {story.story.title}")
print(f"Setting: {story.story.setting}")
print("\nContent:")
for i, segment in enumerate(story.story.content, 1):
    print(f"  {i}. {segment.speaker}: {segment.target_language_text}")
    print(f"     Translation: {segment.base_language_translation}")
    print()

# async def main():
#     module = dspy.Predict(Metadata)
#     query = "trip to beijing"
#     output = await module.acall(query=query)
#     print(output)

# asyncio.run(main())
    
# predict = dspy.Predict("question->answer")

# async def main():
#     # Use acall() for async execution
#     output = await predict.acall(question="why did a chicken cross the kitchen?")
#     print(output)


# asyncio.run(main())