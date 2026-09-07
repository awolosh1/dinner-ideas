from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


class RecipeBase(SQLModel):
    name: str = Field(index=True)
    description: str = ""
    image_url: str = ""


class Recipe(RecipeBase, table=True):
    __tablename__ = "recipes"

    id: int | None = Field(default=None, primary_key=True)
    ingredients: list[RecipeIngredient] = Relationship(back_populates="recipe")
    user_links: list[RecipeUserLink] = Relationship(back_populates="recipe")


class RecipeUserLink(SQLModel, table=True):
    __tablename__ = "recipe_user_links"

    id: int | None = Field(default=None, primary_key=True)
    user_email: str = Field(index=True)
    recipe_id: int = Field(foreign_key="recipes.id", ondelete="CASCADE")
    recipe: Recipe | None = Relationship(back_populates="user_links")

    __table_args__ = (UniqueConstraint("user_email", "recipe_id"),)


class IngredientBase(SQLModel):
    name: str = Field(index=True, unique=True)


class Ingredient(IngredientBase, table=True):
    __tablename__ = "ingredients"

    id: int | None = Field(default=None, primary_key=True)
    recipe_links: list[RecipeIngredient] = Relationship(back_populates="ingredient")


class RecipeIngredientBase(SQLModel):
    quantity: str = ""
    notes: str = ""


class RecipeIngredient(RecipeIngredientBase, table=True):
    __tablename__ = "recipe_ingredients"

    id: int | None = Field(default=None, primary_key=True)
    recipe_id: int | None = Field(
        default=None, foreign_key="recipes.id", ondelete="CASCADE"
    )
    ingredient_id: int | None = Field(
        default=None, foreign_key="ingredients.id", ondelete="CASCADE"
    )
    recipe: Recipe | None = Relationship(back_populates="ingredients")
    ingredient: Ingredient | None = Relationship(back_populates="recipe_links")

    __table_args__ = (UniqueConstraint("recipe_id", "ingredient_id"),)


class RestaurantBase(SQLModel):
    name: str = Field(index=True)
    image_url: str = ""


class Restaurant(RestaurantBase, table=True):
    __tablename__ = "restaurants"

    id: int | None = Field(default=None, primary_key=True)
    menu_items: list[MenuItem] = Relationship(back_populates="restaurant")


class MenuItemBase(SQLModel):
    restaurant_id: int = Field(foreign_key="restaurants.id", ondelete="CASCADE")
    name: str = Field(index=True)
    description: str = ""
    price: str = ""
    image_url: str = ""


class MenuItem(MenuItemBase, table=True):
    __tablename__ = "menu_items"

    id: int | None = Field(default=None, primary_key=True)
    restaurant: Restaurant | None = Relationship(back_populates="menu_items")
    user_links: list[MenuItemUserLink] = Relationship(back_populates="menu_item")


class MenuItemUserLink(SQLModel, table=True):
    __tablename__ = "menu_item_user_links"

    id: int | None = Field(default=None, primary_key=True)
    user_email: str = Field(index=True)
    menu_item_id: int = Field(foreign_key="menu_items.id", ondelete="CASCADE")
    menu_item: MenuItem | None = Relationship(back_populates="user_links")

    __table_args__ = (UniqueConstraint("user_email", "menu_item_id"),)


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
