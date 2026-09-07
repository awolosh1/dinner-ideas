const MAX_NOS = 3;

const state = {
  noCount: 0,
  rejected: [],
  current: null,
  busy: false,
  mood: "any",
};

const app = document.getElementById("app");

function setupMoodButtons() {
  document.querySelectorAll(".mood-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const mood = button.dataset.mood;
      if (!mood || state.busy) return;

      state.mood = mood;
      state.noCount = 0;
      state.rejected = [];

      document.querySelectorAll(".mood-btn").forEach((el) => {
        el.classList.toggle("active", el.dataset.mood === mood);
      });

      advance();
    });
  });
}

setupMoodButtons();

function ticketFrame(innerHtml, stampHtml = "") {
  return `
    <div class="ticket">
      ${stampHtml}
      ${innerHtml}
    </div>
  `;
}

function orderLine() {
  const now = new Date();
  const time = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  return `<div class="order-line"><span>order no. ${Math.floor(Math.random() * 900 + 100)}</span><span>${time}</span></div>`;
}

async function fetchIdea() {
  const params = new URLSearchParams();

  if (state.rejected.length) {
    params.set("exclude", state.rejected.join(","));
  }

  if (state.mood !== "any") {
    params.set("mood", state.mood);
  }

  const query = params.toString() ? `?${params.toString()}` : "";
  const res = await fetch(`/api/random${query}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Something went wrong.");
  }
  return res.json();
}

function renderError(message) {
  app.innerHTML = `
    <div class="ticket">
      ${orderLine()}
      <p class="dish-sub">${message}</p>
      <p class="dish-sub">Head to <a href="/admin">the admin page</a> to add a recipe or a restaurant first.</p>
    </div>
  `;
}

function renderIdea() {
  const idea = state.current;
  const forcedYes = state.noCount >= MAX_NOS;

  const tagHtml = idea.type === "cook"
    ? `<span class="tag cook">Cook at home</span>`
    : `<span class="tag takeout">Takeout · ${idea.restaurant_name}</span>`;

  const photoHtml = idea.image_url
    ? `<img src="${idea.image_url}" alt="${idea.title}" loading="lazy" decoding="async">`
    : `<div class="no-photo">no picture added yet</div>`;

  const metaHtml = idea.type === "takeout" && idea.price
    ? `<div class="dish-meta"><span>${idea.restaurant_name}</span><span>${idea.price}</span></div>`
    : "";

  const marks = Array.from({ length: MAX_NOS }, (_, i) =>
    `<span class="mark ${i < state.noCount ? "used" : ""}"></span>`
  ).join("");

  const bannerHtml = forcedYes
    ? `<div class="forced-banner show">out of no's — this one's dinner.</div>`
    : "";

  const buttonsHtml = forcedYes
    ? `<div class="actions">
         <button class="decision yes" id="yesBtn">Yes, let's eat this</button>
       </div>`
    : `<div class="actions">
         <button class="decision no" id="noBtn">No</button>
         <button class="decision yes" id="yesBtn">Yes</button>
       </div>`;

  app.innerHTML = ticketFrame(`
    ${orderLine()}
    ${bannerHtml}
    ${tagHtml}
    <div class="photo-frame">${photoHtml}</div>
    <h1 class="dish-name">${idea.title}</h1>
    ${idea.subtitle ? `<p class="dish-sub">${idea.subtitle}</p>` : ""}
    ${metaHtml}
    <div class="tally">
      <span>no's used:</span>
      <span class="marks">${marks}</span>
    </div>
    ${buttonsHtml}
  `, `<div class="stamp tomato" id="stampNo">passed</div><div class="stamp avocado" id="stampYes">it's decided</div>`);

  const noBtn = document.getElementById("noBtn");
  if (noBtn) noBtn.addEventListener("click", onNo);
  document.getElementById("yesBtn").addEventListener("click", onYes);
}

function flashStamp(id) {
  return new Promise((resolve) => {
    const el = document.getElementById(id);
    if (!el) return resolve();
    el.classList.add("show");
    setTimeout(() => resolve(), 420);
  });
}

async function onNo() {
  if (state.busy) return;
  state.busy = true;
  await flashStamp("stampNo");
  state.rejected.push(state.current.id);
  state.noCount += 1;
  await advance();
  state.busy = false;
}

async function onYes() {
  if (state.busy) return;
  state.busy = true;
  await flashStamp("stampYes");
  renderDecided(state.current);
  state.busy = false;
}

function renderDecided(idea) {
  const line = idea.type === "cook"
    ? `Tonight you're cooking: <strong>${idea.title}</strong>`
    : `Tonight it's takeout: <strong>${idea.title}</strong> from <strong>${idea.restaurant_name}</strong>`;

  app.innerHTML = `
    <div class="ticket">
      ${orderLine()}
      <div class="photo-frame">${idea.image_url ? `<img src="${idea.image_url}" alt="${idea.title}" loading="lazy" decoding="async">` : `<div class="no-photo">no picture added yet</div>`}</div>
      <h1 class="dish-name">${idea.title}</h1>
      ${idea.subtitle ? `<p class="dish-sub">${idea.subtitle}</p>` : ""}
    </div>
    <div class="decided-note">
      ${line}. Decision's final — the ticket's been punched.
      <br>
      <button id="restartBtn">Pick again tomorrow</button>
    </div>
  `;
  document.getElementById("restartBtn").addEventListener("click", () => {
    state.noCount = 0;
    state.rejected = [];
    advance();
  });
}

async function advance() {
  try {
    state.current = await fetchIdea();
    renderIdea();
  } catch (err) {
    renderError(err.message);
  }
}

advance();
