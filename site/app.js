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

function asShortMoney(value) {
  if (isMissing(value) || isUnavailableString(value) || isInvalidNumberValue(value)) return UNAVAILABLE;
  const number = Number(value);
  if (!Number.isFinite(number)) return UNAVAILABLE;
  if (Math.abs(number) >= 1_000_000) return `$${(number / 1_000_000).toFixed(2)}M`;
  if (Math.abs(number) >= 1_000) return `$${(number / 1_000).toFixed(1)}K`;
  return `$${number.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function asPercent(value) {
  const number = numberOrNull(value);
  if (number === null) return "--";
  return `${number > 0 ? "+" : ""}${number.toFixed(1)}%`;
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

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function setText(selector, text) {
  const node = document.querySelector(selector);
  if (node) node.textContent = text;
}

function setBar(selector, percent) {
  const node = document.querySelector(selector);
  if (node) node.style.width = `${clamp(percent, 0, 100).toFixed(1)}%`;
}

function marketMood(change) {
  if (change === null) {
    return {
      state: "unknown",
      label: "data missing",
      copy: "The latest free snapshot did not include a clean 24h move.",
    };
  }
  if (change <= -20) {
    return {
      state: "rough",
      label: "rough today",
      copy: "The robot is still on screen, but the chart is hitting back hard.",
    };
  }
  if (change <= -5) {
    return {
      state: "down",
      label: "down today",
      copy: "Still active, but the latest read is red.",
    };
  }
  if (change < 5) {
    return {
      state: "flat",
      label: "mostly flat",
      copy: "The chart is not doing much in either direction.",
    };
  }
  return {
    state: "up",
    label: "up today",
    copy: "Green on the latest read, still volatile and not a promise.",
  };
}

function populateCoinRead(data) {
  if (!document.querySelector("[data-market-status]")) return;
  const change = numberOrNull(data.price_change_h24_pct);
  const liquidity = numberOrNull(data.liquidity_usd);
  const volume = numberOrNull(data.volume_h24_usd);
  const marketCap = numberOrNull(data.market_cap_usd ?? data.fdv_usd);
  const curve = numberOrNull(data.bonding_curve_progress);
  const buys = numberOrNull(data.txns_h24?.buys);
  const sells = numberOrNull(data.txns_h24?.sells);
  const trades = (buys ?? 0) + (sells ?? 0);
  const mood = marketMood(change);
  const moodCard = document.querySelector("[data-market-mood]");
  if (moodCard) moodCard.dataset.marketMood = mood.state;
  setText("[data-market-status]", mood.label);
  setText("[data-market-status-copy]", mood.copy);
  setText("[data-market-change]", asPercent(change));
  setText("[data-curve-label]", curve === null ? "--" : curve >= 100 ? "curve complete" : `${curve.toFixed(0)}% complete`);
  setText("[data-trade-count]", trades ? `${trades} public 24h trades` : "--");
  const summary = document.querySelector("[data-coin-summary]");
  if (summary) {
    const capText = marketCap === null ? "unknown size" : `${asShortMoney(marketCap)} market cap`;
    const liquidityText = liquidity === null ? "unknown liquidity" : `${asShortMoney(liquidity)} liquidity`;
    const activityText = trades ? `${trades} trades in 24h` : "activity unavailable";
    summary.textContent = `${mood.label}. ${capText}. ${liquidityText}. ${activityText}.`;
  }
}

async function loadSnapshot() {
  try {
    const response = await fetch("data/token_snapshot.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`snapshot ${response.status}`);
    const data = await response.json();
    if (data.token_address !== TOKEN_ADDRESS) throw new Error("wrong token snapshot");
    populateFields(data);
    populateCoinRead(data);
    document.querySelectorAll("[data-href-field]").forEach((node) => {
      const value = data[node.dataset.hrefField];
      if (value) node.href = value;
    });
  } catch (error) {
    populateFields({});
    populateCoinRead({});
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
  const target = document.querySelector("[data-history-chart], [data-normie-chart]");
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
    const width = 760;
    const height = 260;
    const pad = 34;
    const coords = points.map((point, index) => {
      const raw = point.marketCap ?? point.price ?? min;
      const x = pad + (index * (width - pad * 2)) / (points.length - 1);
      const y = height - pad - ((raw - min) / span) * (height - pad * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });
    const firstPoint = points[0].marketCap ?? points[0].price ?? min;
    const lastPoint = points[points.length - 1].marketCap ?? points[points.length - 1].price ?? min;
    const direction = lastPoint > firstPoint ? "higher than first read" : lastPoint < firstPoint ? "lower than first read" : "back where it started";
    const first = escapeHtml(points[0].timestamp.slice(0, 10));
    const last = escapeHtml(points[points.length - 1].timestamp.slice(0, 10));
    target.innerHTML = `
      <div class="chart-header">
        <span>market-cap trail</span>
        <strong>${direction}</strong>
      </div>
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Historical market-cap trail for CHATTY">
        <rect x="0" y="0" width="${width}" height="${height}" fill="#fffcf2"></rect>
        <line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="#d8d0bd" stroke-width="2"></line>
        <line x1="${pad}" y1="${pad}" x2="${pad}" y2="${height - pad}" stroke="#d8d0bd" stroke-width="2"></line>
        <polyline points="${coords.join(" ")}" fill="none" stroke="#10110f" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"></polyline>
        <polyline points="${coords.join(" ")}" fill="none" stroke="#79f2ae" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"></polyline>
        ${coords.map((coord) => {
          const [x, y] = coord.split(",");
          return `<circle cx="${x}" cy="${y}" r="6" fill="#10110f"></circle>`;
        }).join("")}
        <text x="${pad}" y="${height - 8}" font-size="16" font-weight="800">${first}</text>
        <text x="${width - pad}" y="${height - 8}" text-anchor="end" font-size="16" font-weight="800">${last}</text>
        <text x="${pad}" y="25" font-size="16" font-weight="800">range ${asShortMoney(min)} to ${asShortMoney(max)}</text>
      </svg>
      <p class="small-note">Snapshot trail only. Missing values are skipped, not guessed.</p>
    `;
  } catch {
    target.textContent = "Historical snapshots unavailable.";
  }
}

setupCopyButtons();
loadSnapshot();
loadPublicUpdates();
loadHistoryChart();
