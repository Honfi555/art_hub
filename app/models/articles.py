from pydantic import BaseModel


class ArticleData(BaseModel):
	id: int
	title: str
	user_id: int
	article_body: str
