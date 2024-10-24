
from pydantic import BaseModel

# User models
class User(BaseModel):
    username: str
    email: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
