# from pydantic import BaseModel, EmailStr

# # Dane, których wymagamy przy tworzeniu użytkownika (Request)
# class UserCreate(BaseModel):
#     username: str
#     email: str

# # Dane, które zwracamy użytkownikowi (Response) - dodajemy wygenerowane przez bazę ID
# class UserResponse(BaseModel):
#     id: int
#     username: str
#     email: str
#     is_active: bool

#     class Config:
#         # Informuje Pydantica, żeby potrafił czytać dane bezpośrednio z modeli SQLAlchemy
#         from_attributes = True