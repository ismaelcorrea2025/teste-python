from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None

class User(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)