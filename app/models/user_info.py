from pydantic import BaseModel


class AuthorInfo(BaseModel):
	id: int
	author_name: str
	description: str
