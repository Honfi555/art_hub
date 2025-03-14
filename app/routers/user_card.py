from fastapi import APIRouter


router = APIRouter(
	prefix="/cards",
	tags=["Маршруты для получения статей пользователей"]
)


@router.get("/card")
async def card(user: id):
	pass
