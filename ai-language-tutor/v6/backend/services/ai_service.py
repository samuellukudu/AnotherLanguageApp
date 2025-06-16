from openai import AsyncOpenAI
import os
from typing import Union, List, Dict, Literal, AsyncIterator, Optional
from pydantic import BaseModel
import logging
import json

from backend.core.config import settings
from backend.core.exceptions import AIServiceException, ValidationException
from backend.services.base_service import BaseService

logger = logging.getLogger(__name__)

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class AIService(BaseService):
    """Service for handling AI model interactions"""
    
    def __init__(self):
        super().__init__()
        self.client = AsyncOpenAI(
            base_url=settings.BASE_URL,
            api_key=settings.API_KEY,
        )
        logger.info("AI Service initialized")
    
    @staticmethod
    def flatten_messages(messages: List[Message]) -> str:
        """Flattens a list of chat messages into a single string prompt."""
        return "\n".join([f"{m.role}: {m.content}" for m in messages])

    @staticmethod
    def process_input(data: Union[str, List[Dict[str, str]]]) -> Union[str, List[Dict[str, str]]]:
        """Processes input to either clean a string or modify the 'content' field
        of a list of dictionaries."""
        if isinstance(data, str):
            return data.strip()  # Ensures prompt is cleaned up

        elif isinstance(data, list):
            # Ensure each item in the list is a dictionary with a 'content' key
            return [
                {**item, "content": item["content"].strip()}  # Trims whitespace in 'content'
                for item in data if isinstance(item, dict) and "content" in item
            ]
        
        else:
            raise ValidationException(
                message="Input must be a string or a list of dictionaries with a 'content' field",
                details={"input_type": str(type(data))}
            )

    async def get_completions(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        instructions: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> Union[str, AsyncIterator[str]]:
        """Gets completions from the AI model."""
        try:
            self.log_operation(
                "get_completions", 
                prompt_type=type(prompt).__name__,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            # Process the input
            processed_prompt = self.process_input(prompt)
            
            # Prepare the messages for the API
            messages = [
                {"role": "system", "content": instructions},
            ]
            
            if isinstance(processed_prompt, str):
                messages.append({"role": "user", "content": processed_prompt})
            elif isinstance(processed_prompt, list):
                messages.extend(processed_prompt)
            
            # Call the API
            response = await self.client.chat.completions.create(
                model=settings.MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                async def response_stream():
                    async for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                return response_stream()
            else:
                return response.choices[0].message.content
                
        except ValidationException as e:
            # Re-raise validation exceptions
            raise e
        except Exception as e:
            # Log and wrap other exceptions
            logger.error(f"Error in AI service: {str(e)}")
            raise AIServiceException(
                message="Failed to get completions from AI model",
                details={"error": str(e)}
            )
    
    async def extract_metadata(self, query: str) -> Dict[str, str]:
        """Extract language metadata from user input"""
        try:
            self.log_operation("extract_metadata", query=query)
            
            response_str = await self.get_completions(
                query,
                settings.language_metadata_extraction_prompt
            )
            
            try:
                metadata_dict = json.loads(response_str)
                return metadata_dict
            except json.JSONDecodeError as e:
                raise ValidationException(
                    message="Failed to parse metadata JSON from AI response",
                    details={"response": response_str, "error": str(e)}
                )
                
        except Exception as e:
            if not isinstance(e, (ValidationException, AIServiceException)):
                logger.error(f"Error extracting metadata: {str(e)}")
                raise AIServiceException(
                    message="Failed to extract language metadata",
                    details={"error": str(e)}
                )
            raise

# Create a global service instance
ai_service = AIService()