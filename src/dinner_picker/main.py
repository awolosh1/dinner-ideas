"""
Dinner Picker
=============
A tiny FastAPI app that suggests a random dinner idea — either something to
cook, or a menu item from a local restaurant you've added yourself. You get
3 "no"s before the app makes you say yes to the next one.

Run with:
    uvicorn dinner_picker.main:app --reload
Then open http://127.0.0.1:8000
Admin page (add recipes/restaurants/menu items) at /admin
"""

import random
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .database import engine, init_db
from .models import (
    Ingredient,
    IngredientIn,
    MenuItem,
    MenuItemIn,
    Recipe,
    RecipeIn,
    RecipeIngredient,
    Restaurant,
    RestaurantIn,
)

BASE_DIR = Path(__file__).resolve().parents[2]

app = FastAPI(title="Dinner Picker")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.cache = None

init_db()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    with Session(engine) as session:
        restaurants = session.exec(select(Restaurant).order_by(Restaurant.name)).all()
        recipes = session.exec(select(Recipe).order_by(Recipe.id.desc())).all()
        menu_items = session.exec(
            select(MenuItem, Restaurant)
            .join(Restaurant, MenuItem.restaurant_id == Restaurant.id)
            .order_by(MenuItem.id.desc())
        ).all()
        ingredient_rows = session.exec(
            select(RecipeIngredient, Ingredient)
            .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
            .order_by(RecipeIngredient.recipe_id, Ingredient.name)
        ).all()

    recipe_rows = [dict(r) for r in recipes]
    by_recipe = {}
    for recipe_ingredient, ingredient in ingredient_rows:
        by_recipe.setdefault(recipe_ingredient.recipe_id, []).append(
            {
                "id": recipe_ingredient.id,
                "recipe_id": recipe_ingredient.recipe_id,
                "ingredient_id": ingredient.id,
                "name": ingredient.name,
                "quantity": recipe_ingredient.quantity,
                "notes": recipe_ingredient.notes,
            }
        )
    for recipe in recipe_rows:
        recipe["ingredients"] = by_recipe.get(recipe["id"], [])

    menu_rows = [{
        **dict(m),
        "restaurant_name": r.name,
    } for m, r in menu_items]

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "restaurants": [dict(r) for r in restaurants],
            "recipes": recipe_rows,
            "menu_items": menu_rows,
        },
    )


def _idea_from_recipe(row: Recipe) -> dict:
    return {
        "id": f"cook-{row.id}",
        "type": "cook",
        "title": row.name,
        "subtitle": row.description,
        "image_url": row.image_url,
        "restaurant_name": None,
        "price": None,
    }


def _idea_from_menu_item(row: tuple[MenuItem, Restaurant]) -> dict:
    menu_item, restaurant = row
    image = menu_item.image_url or restaurant.image_url
    return {
        "id": f"takeout-{menu_item.id}",
        "type": "takeout",
        "title": menu_item.name,
        "subtitle": menu_item.description,
        "image_url": image,
        "restaurant_name": restaurant.name,
        "price": menu_item.price,
    }


def _all_ideas() -> list[dict]:
    with Session(engine) as session:
        recipes = session.exec(select(Recipe)).all()
        menu_rows = session.exec(
            select(MenuItem, Restaurant)
            .join(Restaurant, MenuItem.restaurant_id == Restaurant.id)
        ).all()

    ideas = [_idea_from_recipe(r) for r in recipes]
    ideas += [_idea_from_menu_item(r) for r in menu_rows]
    return ideas


@app.get("/api/random")
def random_idea(mood: str = "all", exclude: str = ""):
    excluded_ids = {i for i in exclude.split(",") if i}
    all_ideas = _all_ideas()
    pool = [
        idea for idea in all_ideas
        if (mood in {"all", "any"} or idea["type"] == mood) and idea["id"] not in excluded_ids
    ]

    if not pool:
        pool = [idea for idea in all_ideas if idea["id"] not in excluded_ids]
        if not pool:
            if not all_ideas:
                raise HTTPException(
                    status_code=404,
                    detail="No dinner ideas yet — add some recipes or restaurants in /admin.",
                )
            pool = all_ideas

    return random.choice(pool)


@app.get("/api/ideas")
def list_ideas(mood: str = "all"):
    ideas = _all_ideas()
    filtered = [idea for idea in ideas if mood in {"all", "any"} or idea["type"] == mood]
    random.shuffle(filtered)
    return filtered


@app.post("/api/recipes")
def add_recipe(recipe: RecipeIn):
    with Session(engine) as session:
        row = Recipe.model_validate(recipe)
        session.add(row)
        session.commit()
        session.refresh(row)
        return {"id": row.id}


@app.delete("/api/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    with Session(engine) as session:
        recipe = session.get(Recipe, recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        session.delete(recipe)
        session.commit()
    return {"ok": True}


@app.get("/api/restaurants")
def list_restaurants():
    with Session(engine) as session:
        rows = session.exec(select(Restaurant).order_by(Restaurant.name)).all()
        return [dict(r) for r in rows]


@app.post("/api/restaurants")
def add_restaurant(restaurant: RestaurantIn):
    with Session(engine) as session:
        row = Restaurant.model_validate(restaurant)
        session.add(row)
        session.commit()
        session.refresh(row)
        return {"id": row.id}


@app.delete("/api/restaurants/{restaurant_id}")
def delete_restaurant(restaurant_id: int):
    with Session(engine) as session:
        row = session.get(Restaurant, restaurant_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        session.delete(row)
        session.commit()
    return {"ok": True}


@app.post("/api/menu-items")
def add_menu_item(item: MenuItemIn):
    with Session(engine) as session:
        restaurant = session.get(Restaurant, item.restaurant_id)
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        row = MenuItem.model_validate(item)
        session.add(row)
        session.commit()
        session.refresh(row)
        return {"id": row.id}


@app.delete("/api/menu-items/{item_id}")
def delete_menu_item(item_id: int):
    with Session(engine) as session:
        row = session.get(MenuItem, item_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Menu item not found")
        session.delete(row)
        session.commit()
    return {"ok": True}


@app.put("/api/menu-items/{item_id}")
def update_menu_item(item_id: int, item: MenuItemIn):
    with Session(engine) as session:
        row = session.get(MenuItem, item_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Menu item not found")
        restaurant = session.get(Restaurant, item.restaurant_id)
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        row.restaurant_id = item.restaurant_id
        row.name = item.name
        row.description = item.description
        row.price = item.price
        row.image_url = item.image_url
        session.add(row)
        session.commit()
        return {"ok": True}


@app.get("/api/recipes/{recipe_id}/ingredients")
def list_recipe_ingredients(recipe_id: int):
    with Session(engine) as session:
        rows = session.exec(
            select(RecipeIngredient, Ingredient)
            .join(Ingredient, RecipeIngredient.ingredient_id == Ingredient.id)
            .where(RecipeIngredient.recipe_id == recipe_id)
            .order_by(Ingredient.name)
        ).all()

    return [{
        "id": recipe_ingredient.id,
        "ingredient_id": ingredient.id,
        "name": ingredient.name,
        "quantity": recipe_ingredient.quantity,
        "notes": recipe_ingredient.notes,
    } for recipe_ingredient, ingredient in rows]


@app.post("/api/recipes/{recipe_id}/ingredients")
def add_recipe_ingredient(recipe_id: int, ingredient: IngredientIn):
    with Session(engine) as session:
        recipe = session.get(Recipe, recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")

        name = ingredient.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Ingredient name is required")

        existing_ingredient = session.exec(
            select(Ingredient).where(Ingredient.name == name)
        ).first()

        if existing_ingredient is None:
            existing_ingredient = Ingredient(name=name)
            session.add(existing_ingredient)
            session.commit()
            session.refresh(existing_ingredient)

        existing_link = session.exec(
            select(RecipeIngredient).where(
                RecipeIngredient.recipe_id == recipe_id,
                RecipeIngredient.ingredient_id == existing_ingredient.id,
            )
        ).first()

        if existing_link is not None:
            existing_link.quantity = ingredient.quantity
            existing_link.notes = ingredient.notes
            session.add(existing_link)
            session.commit()
            session.refresh(existing_link)
            recipe_ingredient_id = existing_link.id
        else:
            link = RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_id=existing_ingredient.id,
                quantity=ingredient.quantity,
                notes=ingredient.notes,
            )
            session.add(link)
            session.commit()
            session.refresh(link)
            recipe_ingredient_id = link.id

    return {"id": recipe_ingredient_id}


@app.delete("/api/ingredients/{ingredient_id}")
def delete_recipe_ingredient(ingredient_id: int):
    with Session(engine) as session:
        row = session.get(RecipeIngredient, ingredient_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        ingredient_id_value = row.ingredient_id
        session.delete(row)
        remaining = session.exec(
            select(RecipeIngredient).where(RecipeIngredient.ingredient_id == ingredient_id_value)
        ).first()
        if remaining is None:
            ingredient_record = session.get(Ingredient, ingredient_id_value)
            if ingredient_record is not None:
                session.delete(ingredient_record)
        session.commit()
    return {"ok": True}
