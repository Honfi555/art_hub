from .articles import ArticleData, ArticleAnnouncement
from .authorization import SignInData, ChangePasswordData
from .user_info import AuthorInfo, DescriptionUpdate

__all__: list[str] = ["ArticleData", "SignInData", "ChangePasswordData", "AuthorInfo", "ArticleAnnouncement", "DescriptionUpdate"]
__version__: str = "0.3.0"
__author__: str = "honfi555"
__email__: str = "kasanindaniil@gmail.com"
