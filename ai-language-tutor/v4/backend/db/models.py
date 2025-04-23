from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    role = Column(String(20), nullable=False, server_default="user")

    flashcard_sets = relationship("FlashcardSet", back_populates="user")
    exercise_sets = relationship("ExerciseSet", back_populates="user")
    simulations = relationship("Simulation", back_populates="user")

class FlashcardSet(Base):
    __tablename__ = "flashcard_sets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    query = Column(Text, nullable=False)
    flashcards = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="flashcard_sets")
    generated_flashcards = relationship("GeneratedFlashcard", back_populates="flashcard_set")

class GeneratedFlashcard(Base):
    __tablename__ = "generated_flashcards"
    flashcard_id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("flashcard_sets.id", ondelete="CASCADE"), nullable=False)
    word = Column(Text, nullable=False)
    definition = Column(Text, nullable=False)
    example = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    flashcard_set = relationship("FlashcardSet", back_populates="generated_flashcards")

class ExerciseSet(Base):
    __tablename__ = "exercise_sets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    query = Column(Text, nullable=False)
    exercises = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="exercise_sets")
    generated_exercises = relationship("GeneratedExercise", back_populates="exercise_set")

class GeneratedExercise(Base):
    __tablename__ = "generated_exercises"
    exercise_id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("exercise_sets.id", ondelete="CASCADE"), nullable=False)
    sentence = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    choices = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    exercise_set = relationship("ExerciseSet", back_populates="generated_exercises")

class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    query = Column(Text, nullable=False)
    scenario = Column(Text, nullable=False)
    dialog = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="simulations")

class QueryLog(Base):
    __tablename__ = "query_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    query_type = Column(String(50), nullable=False)
    query = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    user = relationship("User")
