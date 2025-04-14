from pydantic import BaseModel

__all__: list[str] = ["SignInData", "ChangePasswordData"]


class SignInData(BaseModel):
	login: str
	password: str


class ChangePasswordData(BaseModel):
	login: str
	old_password: str
	new_password: str
