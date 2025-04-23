from pydantic import BaseModel, EmailStr, constr, model_validator
from typing import List, Union, Literal, Optional


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class GenerationRequest(BaseModel):
    user_id: int = 0
    query: Union[str, List[Message]]


class MetadataRequest(BaseModel):
    user_id: int = 0
    query: str


# Authentication models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    # Pydantic V2 config for ORM compatibility
    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
    confirm_password: str

    @model_validator(mode='after')
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
