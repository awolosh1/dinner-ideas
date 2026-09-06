from pydantic import BaseModel, Field


class RecipeIn(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    image_url: str = ""


class RestaurantIn(BaseModel):
    name: str = Field(..., min_length=1)
    image_url: str = ""


class MenuItemIn(BaseModel):
    restaurant_id: int
    name: str = Field(..., min_length=1)
    description: str = ""
    price: str = ""
    image_url: str = ""  # optional; falls back to restaurant's image
