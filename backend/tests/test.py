# from pydantic import BaseModel, EmailStr

# # Data required when creating a user (Request)
# class UserCreate(BaseModel):
#     username: str
#     email: str

# # Data returned to the user (Response) - includes generated database ID
# class UserResponse(BaseModel):
#     id: int
#     username: str
#     email: str
#     is_active: bool

#     class Config:
#         # Tells Pydantic to read data directly from SQLAlchemy models
#         from_attributes = True