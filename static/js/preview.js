const TEMPLATE_PRESETS = {
  wedding: { store_name: "OUR ANNIVERSARY", message: "Happy Anniversary, my love" },
  breakup: { store_name: "IT'S OVER", message: "Thanks for the memories" },
  dating: { store_name: "OUR FIRST DATE", message: "Here's to many more" },
  dog: { store_name: "WELCOME HOME", message: "Best good boy since day one" },
  friends: { store_name: "BEST FRIENDS", message: "Friends since forever" },
};

const PRICES = { 12: 400, 18: 500, magnets: 49 };

function collectFormData() {
  const items = Array.from(document.querySelectorAll(".item-name")).map((nameEl, i) => {
    const priceEl = document.querySelectorAll(".item-price")[i];
    return { name: nameEl.value.trim(), price: parseFloat(priceEl.value) || 0 };
  }).filter((item) => item.name);

  return {
    store_name: document.getElementById("store_name").value.trim() || "YOUR STORE",
    items,
    custom_message: document.getElementById("custom_message").value.trim(),
    receipt_date: document.getElementById("receipt_date").value,
    height: document.getElementById("height").value,
    add_magnets: document.getElementById("add_magnets").checked,
  };
}

function renderPreview(data) {
  document.getElementById("p-store").textContent = data.store_name || "YOUR STORE";

  const itemsContainer = document.getElementById("p-items");
  itemsContainer.innerHTML = "";
  let total = 0;
  data.items.forEach((item) => {
    total += item.price;
    const row = document.createElement("div");
    row.className = "line-item";
    row.innerHTML = `<span>${item.name}</span><span>${item.price.toFixed(2)}</span>`;
    itemsContainer.appendChild(row);
  });

  document.getElementById("p-total").textContent = total.toFixed(2);
  document.getElementById("p-message").textContent = data.custom_message;
  document.getElementById("p-date").textContent = data.receipt_date || "";

  const paper = document.getElementById("receipt-preview");
  paper.style.minHeight = data.height === "18" ? "440px" : "320px";

  const base = PRICES[data.height] || PRICES["12"];
  const price = base + (data.add_magnets ? PRICES.magnets : 0);
  document.getElementById("price-tag").textContent = price;
}

function getCookiePreview(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

let debounceTimer = null;
function schedulePreviewSync() {
  clearTimeout(debounceTimer);
  const data = collectFormData();
  renderPreview(data);

  debounceTimer = setTimeout(() => {
    fetch("/api/builder/preview/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookiePreview("csrftoken"),
      },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .catch(() => null);
  }, 300);
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("builder-form");
  form.addEventListener("input", schedulePreviewSync);

  document.getElementById("template").addEventListener("change", (e) => {
    const preset = TEMPLATE_PRESETS[e.target.value];
    if (preset) {
      document.getElementById("store_name").value = preset.store_name;
      document.getElementById("custom_message").value = preset.message;
    }
    schedulePreviewSync();
  });

  document.getElementById("add-to-cart-btn").addEventListener("click", () => {
    const data = collectFormData();
    addToCart({
      product_id: document.getElementById("builder_product_id").value,
      size: data.height === "18" ? "large" : "standard",
      add_magnets: data.add_magnets,
      custom_config: JSON.stringify(data),
    }).then(() => {
      document.getElementById("add-to-cart-message").textContent = "Added to cart!";
    });
  });

  schedulePreviewSync();
});
