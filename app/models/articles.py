from pydantic import BaseModel


class ArticleAnnouncement(BaseModel):
	id: int
	title: str
	user_name: str
	announcement: str


class ArticleData(BaseModel):
	id: int
	title: str
	user_name: str
	article_body: str
