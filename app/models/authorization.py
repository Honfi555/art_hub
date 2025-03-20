from pydantic import BaseModel


class SignInData(BaseModel):
	login: str
	password: str


class ChangePasswordData(BaseModel):
	login: str
	old_password: str
	new_password: str
