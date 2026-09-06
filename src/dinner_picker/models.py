from typing import Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


class RecipeBase(SQLModel):
    name: str = Field(index=True)
    description: str = ""
    image_url: str = ""


class Recipe(RecipeBase, table=True):
    __tablename__ = "recipes"

    id: Optional[int] = Field(default=None, primary_key=True)
    ingredients: list["RecipeIngredient"] = Relationship(back_populates="recipe")


class IngredientBase(SQLModel):
    name: str = Field(index=True, unique=True)


class Ingredient(IngredientBase, table=True):
    __tablename__ = "ingredients"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_links: list["RecipeIngredient"] = Relationship(back_populates="ingredient")


class RecipeIngredientBase(SQLModel):
    quantity: str = ""
    notes: str = ""


class RecipeIngredient(RecipeIngredientBase, table=True):
    __tablename__ = "recipe_ingredients"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipes.id", ondelete="CASCADE")
    ingredient_id: Optional[int] = Field(default=None, foreign_key="ingredients.id", ondelete="CASCADE")
    recipe: Optional[Recipe] = Relationship(back_populates="ingredients")
    ingredient: Optional[Ingredient] = Relationship(back_populates="recipe_links")

    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id"),)


class RestaurantBase(SQLModel):
    name: str = Field(index=True)
    image_url: str = ""


class Restaurant(RestaurantBase, table=True):
    __tablename__ = "restaurants"

    id: Optional[int] = Field(default=None, primary_key=True)
    menu_items: list["MenuItem"] = Relationship(back_populates="restaurant")


class MenuItemBase(SQLModel):
    restaurant_id: int = Field(foreign_key="restaurants.id", ondelete="CASCADE")
    name: str = Field(index=True)
    description: str = ""
    price: str = ""
    image_url: str = ""


class MenuItem(MenuItemBase, table=True):
    __tablename__ = "menu_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    restaurant: Optional[Restaurant] = Relationship(back_populates="menu_items")


class RecipeCreate(RecipeBase):
    pass


class IngredientCreate(IngredientBase):
    quantity: str = ""
    notes: str = ""


class RestaurantCreate(RestaurantBase):
    pass


class MenuItemCreate(MenuItemBase):
    pass


class RecipeIn(RecipeCreate):
    pass


class IngredientIn(IngredientCreate):
    pass


class RestaurantIn(RestaurantCreate):
    pass


class MenuItemIn(MenuItemCreate):
    pass
