async function requestJson(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Request failed");
  }
  return res.json();
}

async function postJson(url, data) {
  return requestJson(url, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

async function putJson(url, data) {
  return requestJson(url, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

function formToObject(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  if ("restaurant_id" in data) data.restaurant_id = parseInt(data.restaurant_id, 10);
  return data;
}

function attachForm(formId, endpoint) {
  const form = document.getElementById(formId);
  if (!form) return;
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const data = formToObject(form);
      const itemId = form.dataset.editId;
      if (itemId) {
        await putJson(`${endpoint}/${itemId}`, data);
        form.dataset.editId = "";
        form.reset();
        const submitBtn = form.querySelector(".submit");
        if (submitBtn) submitBtn.textContent = "Add menu item";
        const cancelBtn = document.getElementById("menuItemCancel");
        if (cancelBtn) cancelBtn.hidden = true;
      } else {
        await postJson(endpoint, data);
        form.reset();
      }
      location.reload();
    } catch (err) {
      alert(err.message);
    }
  });
}

function attachMenuItemEdits() {
  const form = document.getElementById("menuItemForm");
  if (!form) return;

  const submitBtn = form.querySelector(".submit");
  const cancelBtn = document.getElementById("menuItemCancel");

  document.querySelectorAll("button.edit[data-kind='menu-items']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.closest(".existing-item");
      if (!item) return;

      form.dataset.editId = item.dataset.id;
      document.getElementById("m-restaurant").value = item.dataset.restaurantId || "";
      document.getElementById("m-name").value = item.dataset.name || "";
      document.getElementById("m-description").value = item.dataset.description || "";
      document.getElementById("m-price").value = item.dataset.price || "";
      document.getElementById("m-image").value = item.dataset.imageUrl || "";

      if (submitBtn) submitBtn.textContent = "Save menu item";
      if (cancelBtn) cancelBtn.hidden = false;
      window.scrollTo({ top: form.offsetTop - 20, behavior: "smooth" });
    });
  });

  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      form.dataset.editId = "";
      form.reset();
      if (submitBtn) submitBtn.textContent = "Add menu item";
      cancelBtn.hidden = true;
    });
  }
}

function attachRecipeIngredientForms() {
  document.querySelectorAll(".ingredient-form").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const recipeId = form.dataset.recipeId;
      const nameInput = form.querySelector("input[name='ingredient_name']");
      const qtyInput = form.querySelector("input[name='ingredient_quantity']");
      const notesInput = form.querySelector("input[name='ingredient_notes']");

      if (!recipeId || !nameInput || !nameInput.value.trim()) {
        return;
      }

      try {
        await postJson(`/api/recipes/${recipeId}/ingredients`, {
          name: nameInput.value.trim(),
          quantity: qtyInput ? qtyInput.value.trim() : "",
          notes: notesInput ? notesInput.value.trim() : "",
        });
        location.reload();
      } catch (err) {
        alert(err.message);
      }
    });
  });

  document.querySelectorAll("button.del-ingredient").forEach((btn) => {
    btn.addEventListener("click", async () => {
      if (!confirm("Remove this ingredient?")) return;
      try {
        const res = await fetch(`/api/ingredients/${btn.dataset.id}`, { method: "DELETE" });
        if (!res.ok) throw new Error("Could not delete ingredient");
        location.reload();
      } catch (err) {
        alert(err.message);
      }
    });
  });
}

attachForm("restaurantForm", "/api/restaurants");
attachForm("menuItemForm", "/api/menu-items");
attachForm("recipeForm", "/api/recipes");
attachMenuItemEdits();
attachRecipeIngredientForms();

document.querySelectorAll("button.del").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const kind = btn.dataset.kind;
    const id = btn.dataset.id;
    if (!confirm("Remove this?")) return;
    try {
      const res = await fetch(`/api/${kind}/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Could not delete");
      location.reload();
    } catch (err) {
      alert(err.message);
    }
  });
});

async function loadSharedMenuItems() {
  console.log("loadSharedMenuItems called");
  const container = document.getElementById("sharedMenuItemList");
  if (!container) return;
  
  try {
    const items = await requestJson("/api/menu-items/shared/available");
    console.log("Shared menu items:", items);
    
    if (items.length === 0) {
      container.innerHTML = '<span class="empty-msg">No menu items from other users available.</span>';
      return;
    }
    
    container.innerHTML = items.map(item => `
      <div class="existing-item">
        <span>${item.name} <span class="meta">— ${item.restaurant_name}</span></span>
        ${item.description ? `<div class="meta">${item.description}</div>` : ""}
        <div class="existing-actions">
          <button class="add-shared" data-kind="menu-items" data-id="${item.id}">add to mine</button>
        </div>
      </div>
    `).join("");
    
    document.querySelectorAll("button.add-shared[data-kind='menu-items']").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm("Add this menu item to your collection?")) return;
        try {
          await postJson(`/api/menu-items/shared/${btn.dataset.id}/add`, {});
          location.reload();
        } catch (err) {
          alert(err.message);
        }
      });
    });
  } catch (err) {
    container.innerHTML = `<span class="empty-msg">Error loading menu items: ${err.message}</span>`;
  }
}

async function loadSharedRecipes() {
  const container = document.getElementById("sharedRecipeList");
  if (!container) return;
  
  try {
    const recipes = await requestJson("/api/recipes/shared/available");
    console.log("Shared recipes:", recipes);
    
    if (recipes.length === 0) {
      container.innerHTML = '<span class="empty-msg">No recipes from other users available.</span>';
      return;
    }
    
    container.innerHTML = recipes.map(recipe => `
      <div class="existing-item">
        <span>${recipe.name}</span>
        ${recipe.description ? `<div class="meta">${recipe.description}</div>` : ""}
        <div class="existing-actions">
          <button class="add-shared" data-kind="recipes" data-id="${recipe.id}">add to mine</button>
        </div>
      </div>
    `).join("");
    
    document.querySelectorAll("button.add-shared[data-kind='recipes']").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm("Add this recipe to your collection?")) return;
        try {
          await postJson(`/api/recipes/shared/${btn.dataset.id}/add`, {});
          location.reload();
        } catch (err) {
          alert(err.message);
        }
      });
    });
  } catch (err) {
    console.error("Error loading recipes:", err);
    container.innerHTML = `<span class="empty-msg">Error loading recipes: ${err.message}</span>`;
  }
}

loadSharedMenuItems();
loadSharedRecipes();

console.log("Admin page loaded - functions called");

