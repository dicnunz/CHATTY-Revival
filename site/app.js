const TOKEN_ADDRESS = "jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump";

function asMoney(value) {
  if (value === undefined || value === null || value === "") return "unavailable";
  const number = Number(value);
  if (!Number.isFinite(number)) return String(value);
  return number < 1 ? `$${number.toFixed(8)}` : `$${number.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function asPlain(value) {
  if (value === undefined || value === null || value === "") return "unavailable";
  return String(value);
}

async function loadSnapshot() {
  try {
    const response = await fetch("data/token_snapshot.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`snapshot ${response.status}`);
    const data = await response.json();
    if (data.token_address !== TOKEN_ADDRESS) throw new Error("wrong token snapshot");
    document.querySelectorAll("[data-field]").forEach((node) => {
      const key = node.dataset.field;
      const value = data[key];
      node.textContent = node.dataset.money === "true" ? asMoney(value) : asPlain(value);
    });
    document.querySelectorAll("[data-href-field]").forEach((node) => {
      const value = data[node.dataset.hrefField];
      if (value) node.href = value;
    });
  } catch (error) {
    document.querySelectorAll("[data-field]").forEach((node) => {
      if (!node.textContent.trim()) node.textContent = "unavailable";
    });
  }
}

function setupCopyButtons() {
  document.querySelectorAll("[data-copy-contract]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(TOKEN_ADDRESS);
      } catch {
        const area = document.createElement("textarea");
        area.value = TOKEN_ADDRESS;
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        area.remove();
      }
      const original = button.textContent;
      button.textContent = "Copied";
      setTimeout(() => {
        button.textContent = original;
      }, 1400);
    });
  });
}

async function loadPublicUpdates() {
  const target = document.querySelector("[data-public-updates]");
  if (!target) return;
  try {
    const response = await fetch("data/public_updates.md", { cache: "no-store" });
    if (!response.ok) throw new Error(`updates ${response.status}`);
    target.textContent = await response.text();
  } catch {
    target.textContent = "Public update log unavailable in this local view.";
  }
}

setupCopyButtons();
loadSnapshot();
loadPublicUpdates();
