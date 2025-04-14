from pydantic import BaseModel

__all__: list[str] = ["AuthorInfo", "DescriptionUpdate"]


class AuthorInfo(BaseModel):
	id: int
	author_name: str
	description: str


class DescriptionUpdate(BaseModel):
	description: str
