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

function numberOrNull(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[char]);
}

async function loadHistoryChart() {
  const target = document.querySelector("[data-history-chart]");
  if (!target) return;
  try {
    const response = await fetch("data/history.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`history ${response.status}`);
    const data = await response.json();
    const rows = Array.isArray(data.snapshots) ? data.snapshots : [];
    const points = rows
      .map((row) => ({
        timestamp: row.timestamp,
        price: numberOrNull(row.price_usd),
        marketCap: numberOrNull(row.market_cap_usd),
      }))
      .filter((row) => row.price !== null || row.marketCap !== null);
    if (points.length < 2) {
      target.textContent = "Not enough historical snapshots yet.";
      return;
    }
    const values = points.map((point) => point.marketCap ?? point.price).filter((value) => value !== null);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = max - min || 1;
    const width = 720;
    const height = 240;
    const pad = 36;
    const coords = points.map((point, index) => {
      const raw = point.marketCap ?? point.price ?? min;
      const x = pad + (index * (width - pad * 2)) / (points.length - 1);
      const y = height - pad - ((raw - min) / span) * (height - pad * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });
    const first = escapeHtml(points[0].timestamp);
    const last = escapeHtml(points[points.length - 1].timestamp);
    target.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Historical market cap snapshot line chart">
        <rect x="0" y="0" width="${width}" height="${height}" fill="#fffdf4"></rect>
        <line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="#151515" stroke-width="3"></line>
        <line x1="${pad}" y1="${pad}" x2="${pad}" y2="${height - pad}" stroke="#151515" stroke-width="3"></line>
        <polyline points="${coords.join(" ")}" fill="none" stroke="#24d1a4" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"></polyline>
        ${coords.map((coord) => {
          const [x, y] = coord.split(",");
          return `<circle cx="${x}" cy="${y}" r="7" fill="#151515"></circle>`;
        }).join("")}
        <text x="${pad}" y="${height - 8}" font-size="16" font-weight="800">${first}</text>
        <text x="${width - pad}" y="${height - 8}" text-anchor="end" font-size="16" font-weight="800">${last}</text>
        <text x="${pad}" y="24" font-size="16" font-weight="800">Market cap snapshot range: ${asMoney(min)} to ${asMoney(max)}</text>
      </svg>
      <p class="small-note">Volatile historical public snapshots, not trading signals. Missing values are skipped, not guessed.</p>
    `;
  } catch {
    target.textContent = "Historical snapshots unavailable.";
  }
}

setupCopyButtons();
loadSnapshot();
loadPublicUpdates();
loadHistoryChart();
