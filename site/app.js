const TOKEN_ADDRESS = "jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump";
const UNAVAILABLE = "Unavailable from free public snapshot";
const SNAPSHOT_UNAVAILABLE = "Snapshot unavailable";

function isMissing(value) {
  return value === undefined || value === null || value === "" || String(value).trim() === "";
}

function isUnavailableString(value) {
  return typeof value === "string" && value.toLowerCase().includes("unavailable");
}

function isInvalidNumberValue(value) {
  return (typeof value === "number" && !Number.isFinite(value)) || (typeof value === "string" && /^(nan|infinity|-infinity)$/i.test(value.trim()));
}

function asMoney(value) {
  if (isMissing(value) || isUnavailableString(value) || isInvalidNumberValue(value)) return UNAVAILABLE;
  const number = Number(value);
  if (!Number.isFinite(number)) return UNAVAILABLE;
  return number < 1 ? `$${number.toFixed(8)}` : `$${number.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function asPlain(value) {
  if (isMissing(value) || isUnavailableString(value) || isInvalidNumberValue(value)) return UNAVAILABLE;
  return String(value);
}

function asTimestamp(value) {
  if (isMissing(value) || isUnavailableString(value)) return SNAPSHOT_UNAVAILABLE;
  return String(value);
}

function formatField(node, data) {
  const key = node.dataset.field;
  const value = data ? data[key] : undefined;
  let text = key === "timestamp" ? asTimestamp(value) : node.dataset.money === "true" ? asMoney(value) : asPlain(value);
  if (node.dataset.suffix && text !== UNAVAILABLE && text !== SNAPSHOT_UNAVAILABLE) {
    text += node.dataset.suffix;
  }
  return text;
}

function populateFields(data) {
  document.querySelectorAll("[data-field]").forEach((node) => {
    node.textContent = formatField(node, data);
  });
}

async function loadSnapshot() {
  try {
    const response = await fetch("data/token_snapshot.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`snapshot ${response.status}`);
    const data = await response.json();
    if (data.token_address !== TOKEN_ADDRESS) throw new Error("wrong token snapshot");
    populateFields(data);
    document.querySelectorAll("[data-href-field]").forEach((node) => {
      const value = data[node.dataset.hrefField];
      if (value) node.href = value;
    });
  } catch (error) {
    populateFields({});
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
