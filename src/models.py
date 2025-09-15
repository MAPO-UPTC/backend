from pydantic import BaseModel


class SignUpSchema(BaseModel):
    email: str
    password: str
    first_name: str
    second_first_name: str
    last_name: str
    second_last_name: str
    phone_number: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "string",
                "first_name": "John",
                "second_first_name": "Doe",
                "last_name": "Smith",
                "second_last_name": "Johnson",
                "phone_number": "123-456-7890",
            }
        }


class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "string",
            }
        }
