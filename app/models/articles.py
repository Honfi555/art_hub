from pydantic import BaseModel

__all__: list[str] = ["ArticleAnnouncement", "ArticleData", "ArticleFull", "ArticleAdd", "ImagesAdd"]


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


class ArticleFull(BaseModel):
	id: int
	title: str
	user_name: str
	announcement: str
	article_body: str


class ArticleAdd(BaseModel):
	title: str
	announcement: str
	article_body: str


class ImagesAdd(BaseModel):
	article_id: int
	images: list[str]
