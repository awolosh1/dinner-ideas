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

from .database import get_conn, init_db
from .models import MenuItemIn, RecipeIn, RestaurantIn

BASE_DIR = Path(__file__).resolve().parents[2]

app = FastAPI(title="Dinner Picker")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.cache = None   # workaround for pallets/jinja#2180 on Python 3.14

init_db()


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    with get_conn() as conn:
        restaurants = conn.execute(
            "SELECT * FROM restaurants ORDER BY name"
        ).fetchall()
        recipes = conn.execute(
            "SELECT * FROM recipes ORDER BY id DESC"
        ).fetchall()
        menu_items = conn.execute(
            """SELECT menu_items.*, restaurants.name AS restaurant_name
               FROM menu_items
               JOIN restaurants ON restaurants.id = menu_items.restaurant_id
               ORDER BY menu_items.id DESC"""
        ).fetchall()
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "restaurants": [dict(r) for r in restaurants],
            "recipes": [dict(r) for r in recipes],
            "menu_items": [dict(m) for m in menu_items],
        },
    )


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _idea_from_recipe(row) -> dict:
    return {
        "id": f"cook-{row['id']}",
        "type": "cook",
        "title": row["name"],
        "subtitle": row["description"],
        "image_url": row["image_url"],
        "restaurant_name": None,
        "price": None,
    }


def _idea_from_menu_item(row) -> dict:
    image = row["item_image"] or row["restaurant_image"]
    return {
        "id": f"takeout-{row['id']}",
        "type": "takeout",
        "title": row["name"],
        "subtitle": row["description"],
        "image_url": image,
        "restaurant_name": row["restaurant_name"],
        "price": row["price"],
    }


def _all_ideas() -> list[dict]:
    with get_conn() as conn:
        recipes = conn.execute("SELECT * FROM recipes").fetchall()
        items = conn.execute(
            """SELECT menu_items.id AS id,
                      menu_items.name AS name,
                      menu_items.description AS description,
                      menu_items.price AS price,
                      menu_items.image_url AS item_image,
                      restaurants.name AS restaurant_name,
                      restaurants.image_url AS restaurant_image
               FROM menu_items
               JOIN restaurants ON restaurants.id = menu_items.restaurant_id"""
        ).fetchall()

    ideas = [_idea_from_recipe(r) for r in recipes]
    ideas += [_idea_from_menu_item(r) for r in items]
    return ideas


# --------------------------------------------------------------------------
# API: random suggestion
# --------------------------------------------------------------------------

@app.get("/api/random")
def random_idea(mood: str = "all", exclude: str = ""):
    """
    Return one random dinner idea.
    `exclude` is a comma-separated list of idea ids already rejected this
    round, so the same idea isn't shown twice in a row.
    `mood` can be "all", "cook", or "takeout" to narrow the pool.
    """
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


# --------------------------------------------------------------------------
# API: idea list / random order
# --------------------------------------------------------------------------

@app.get("/api/ideas")
def list_ideas(mood: str = "all"):
    """Return all dinner ideas for the selected mood in a random order."""
    ideas = _all_ideas()
    filtered = [idea for idea in ideas if mood in {"all", "any"} or idea["type"] == mood]
    random.shuffle(filtered)
    return filtered


# --------------------------------------------------------------------------
# API: admin - recipes
# --------------------------------------------------------------------------

@app.post("/api/recipes")
def add_recipe(recipe: RecipeIn):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO recipes (name, description, image_url) VALUES (?, ?, ?)",
            (recipe.name, recipe.description, recipe.image_url),
        )
        conn.commit()
        return {"id": cur.lastrowid}


@app.delete("/api/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        conn.commit()
    return {"ok": True}


# --------------------------------------------------------------------------
# API: admin - restaurants
# --------------------------------------------------------------------------

@app.get("/api/restaurants")
def list_restaurants():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM restaurants ORDER BY name").fetchall()
        return [dict(r) for r in rows]


@app.post("/api/restaurants")
def add_restaurant(restaurant: RestaurantIn):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO restaurants (name, image_url) VALUES (?, ?)",
            (restaurant.name, restaurant.image_url),
        )
        conn.commit()
        return {"id": cur.lastrowid}


@app.delete("/api/restaurants/{restaurant_id}")
def delete_restaurant(restaurant_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM restaurants WHERE id = ?", (restaurant_id,))
        conn.commit()
    return {"ok": True}


# --------------------------------------------------------------------------
# API: admin - menu items
# --------------------------------------------------------------------------

@app.post("/api/menu-items")
def add_menu_item(item: MenuItemIn):
    with get_conn() as conn:
        restaurant = conn.execute(
            "SELECT id FROM restaurants WHERE id = ?", (item.restaurant_id,)
        ).fetchone()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        cur = conn.execute(
            """INSERT INTO menu_items (restaurant_id, name, description, price, image_url)
               VALUES (?, ?, ?, ?, ?)""",
            (item.restaurant_id, item.name, item.description, item.price, item.image_url),
        )
        conn.commit()
        return {"id": cur.lastrowid}


@app.delete("/api/menu-items/{item_id}")
def delete_menu_item(item_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
        conn.commit()
    return {"ok": True}


@app.put("/api/menu-items/{item_id}")
def update_menu_item(item_id: int, item: MenuItemIn):
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM menu_items WHERE id = ?", (item_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Menu item not found")

        restaurant = conn.execute(
            "SELECT id FROM restaurants WHERE id = ?", (item.restaurant_id,)
        ).fetchone()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        conn.execute(
            """UPDATE menu_items
               SET restaurant_id = ?, name = ?, description = ?, price = ?, image_url = ?
               WHERE id = ?""",
            (item.restaurant_id, item.name, item.description, item.price, item.image_url, item_id),
        )
        conn.commit()
        return {"ok": True}
