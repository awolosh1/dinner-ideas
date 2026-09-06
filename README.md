# Dinner Picker

A tiny FastAPI app that suggests a random dinner idea — cook it yourself,
or order takeout from a local restaurant you've added. You get **3 no's**
before the app makes the next suggestion your dinner.

## How it works

- **Two kinds of ideas:** `cook` (a recipe) and `takeout` (a menu item from
  a restaurant).
- **Restaurants** are added manually by name, with one picture.
- **Menu items** are added one dish at a time, linked to a restaurant. If a
  menu item doesn't get its own picture, it automatically uses the
  restaurant's picture.
- **The 3-no rule:** each time you say "No," the idea is marked as passed
  and a new random one is drawn (it won't repeat within the same round).
  After 3 no's, the next suggestion drops the "No" button — you only get
  "Yes."

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open:
- **http://127.0.0.1:8000** — the picker itself
- **http://127.0.0.1:8000/admin** — add/remove recipes, restaurants, and menu items

The app uses a local SQLite file (`dinner.db`), created automatically on
first run with a few sample recipes and restaurants so it's not empty out
of the box. Delete `dinner.db` to reset it.

## Project structure

```
main.py          FastAPI app and all routes
database.py      SQLite schema, connection helper, seed data
models.py        Pydantic request models
templates/       Jinja2 HTML (index.html = picker, admin.html = admin)
static/          CSS + vanilla JS front end
```

## API reference

| Method | Path                         | Purpose                              |
|--------|------------------------------|---------------------------------------|
| GET    | `/api/random?exclude=id,id`  | Get one random idea, skipping given ids |
| GET    | `/api/restaurants`           | List restaurants                      |
| POST   | `/api/restaurants`           | Add a restaurant `{name, image_url}`  |
| DELETE | `/api/restaurants/{id}`      | Remove a restaurant (and its items)   |
| POST   | `/api/menu-items`            | Add a menu item `{restaurant_id, name, description, price, image_url}` |
| DELETE | `/api/menu-items/{id}`       | Remove a menu item                    |
| POST   | `/api/recipes`               | Add a recipe `{name, description, image_url}` |
| DELETE | `/api/recipes/{id}`          | Remove a recipe                       |
