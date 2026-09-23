# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Genererar index.html från headlamps.tsv.

Körning:
    uv run generate_html.py
    (eller: python generate_html.py)
"""

import argparse
import csv
import json
from pathlib import Path


HTML_PREAMBLE = """<!DOCTYPE html>
<html lang="sv">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <base target="_blank">
  <title>Orienteringspannlampor – Jämförelse</title>
  <style>
    :root {
      --bg: #0f172a;
      --bg-card: #1e293b;
      --bg-card-hover: #273549;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --primary-hover: #0284c7;
      --primary-subtle: rgba(56, 189, 248, 0.12);
      --accent: #f59e0b;
      --success: #10b981;
      --success-subtle: rgba(16, 185, 129, 0.12);
      --badge-bg: #334155;
      --table-stripe: rgba(255, 255, 255, 0.02);
      --table-hover: rgba(56, 189, 248, 0.06);
      --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.3);
      --radius: 10px;
    }

    [data-theme="light"] {
      --bg: #f8fafc;
      --bg-card: #ffffff;
      --bg-card-hover: #f1f5f9;
      --border: #e2e8f0;
      --text: #0f172a;
      --text-muted: #64748b;
      --primary: #0284c7;
      --primary-hover: #0369a1;
      --primary-subtle: rgba(2, 132, 199, 0.08);
      --accent: #d97706;
      --success: #059669;
      --success-subtle: rgba(5, 150, 105, 0.08);
      --badge-bg: #e2e8f0;
      --table-stripe: rgba(0, 0, 0, 0.015);
      --table-hover: rgba(2, 132, 199, 0.04);
      --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.4;
      padding: 16px 12px;
      transition: background-color 0.2s ease, color 0.2s ease;
    }

    .container {
      max-width: 1480px;
      margin: 0 auto;
    }

    /* Header */
    header {
      margin-bottom: 12px;
    }

    .header-top {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }

    h1 {
      font-size: 1.55rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    h1 span.icon {
      font-size: 1.35rem;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 11px;
      font-size: 0.8rem;
      font-weight: 600;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--bg-card);
      color: var(--text);
      cursor: pointer;
      transition: all 0.15s ease;
      text-decoration: none;
    }

    .btn:hover {
      background: var(--bg-card-hover);
      border-color: var(--primary);
    }

    /* Table Container */
    .table-wrapper {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow-x: auto;
      box-shadow: var(--shadow);
      margin-bottom: 20px;
      -webkit-overflow-scrolling: touch;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.82rem;
    }

    thead {
      background: rgba(0, 0, 0, 0.25);
      border-bottom: 2px solid var(--border);
    }

    [data-theme="light"] thead {
      background: #f1f5f9;
    }

    th {
      padding: 9px 8px;
      font-weight: 700;
      color: var(--text);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      user-select: none;
      cursor: pointer;
      position: relative;
      transition: background 0.15s;
    }

    th:hover {
      background: var(--table-hover);
    }

    th.no-sort {
      cursor: default;
    }

    th.no-sort:hover {
      background: transparent;
    }

    th .sort-icon {
      display: inline-block;
      margin-left: 3px;
      color: var(--text-muted);
      font-size: 0.7rem;
    }

    th.sorted-asc .sort-icon::after {
      content: "▲";
      color: var(--primary);
    }

    th.sorted-desc .sort-icon::after {
      content: "▼";
      color: var(--primary);
    }

    th:not(.sorted-asc):not(.sorted-desc) .sort-icon::after {
      content: "⇅";
      opacity: 0.35;
    }

    tbody tr {
      border-bottom: 1px solid var(--border);
      transition: background-color 0.15s ease;
    }

    tbody tr:nth-child(even) {
      background-color: var(--table-stripe);
    }

    tbody tr:hover {
      background-color: var(--table-hover);
    }

    tbody tr.highlight-orientering {
      background-color: rgba(56, 189, 248, 0.025);
    }

    td {
      padding: 7px 8px;
      vertical-align: middle;
    }

    /* Column Widths & Alignments */
    .col-image {
      width: 52px;
      min-width: 52px;
      max-width: 52px;
      text-align: center;
      padding: 5px 4px !important;
    }

    .product-thumb {
      width: 44px;
      height: 44px;
      object-fit: contain;
      background: #ffffff;
      border-radius: 6px;
      border: 1px solid var(--border);
      padding: 2px;
      display: block;
      margin: 0 auto;
      transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s ease;
      cursor: pointer;
    }

    .product-thumb:hover {
      transform: scale(2.2);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.65);
      z-index: 50;
      position: relative;
    }

    .col-model {
      min-width: 160px;
      max-width: 200px;
    }

    .product-name {
      font-weight: 700;
      font-size: 0.865rem;
      color: var(--text);
      display: flex;
      flex-direction: column;
      gap: 2px;
      line-height: 1.25;
    }

    .badge-ol {
      display: inline-flex;
      align-items: center;
      gap: 3px;
      font-size: 0.65rem;
      font-weight: 700;
      padding: 1px 5px;
      border-radius: 3px;
      background: var(--success-subtle);
      color: var(--success);
      width: fit-content;
    }

    .badge-sub3000 {
      display: inline-flex;
      align-items: center;
      gap: 3px;
      font-size: 0.65rem;
      font-weight: 600;
      padding: 1px 5px;
      border-radius: 3px;
      background: var(--badge-bg);
      color: var(--text-muted);
      width: fit-content;
    }

    /* Stores List */
    .col-stores {
      min-width: 220px;
      max-width: 270px;
      font-size: 0.775rem;
    }

    .store-list {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .store-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      line-height: 1.3;
    }

    .store-link {
      color: var(--primary);
      text-decoration: none;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 3px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 135px;
    }

    .store-link:hover {
      text-decoration: underline;
      color: var(--primary-hover);
    }

    .store-link svg {
      width: 10px;
      height: 10px;
      flex-shrink: 0;
      opacity: 0.75;
    }

    .store-price {
      font-weight: 600;
      color: var(--text);
      white-space: nowrap;
      font-size: 0.76rem;
    }

    .store-price.is-lowest {
      color: var(--success);
      font-weight: 700;
    }

    .store-note {
      font-size: 0.675rem;
      color: var(--text-muted);
      font-weight: normal;
    }

    /* Numeric metric columns - very compact */
    .col-num {
      text-align: right !important;
      white-space: nowrap;
      width: 1%;
      padding: 7px 7px !important;
    }

    .col-year {
      text-align: center !important;
      white-space: nowrap;
    }

    .metric-value {
      font-weight: 700;
      font-size: 0.855rem;
      white-space: nowrap;
    }

    .price-highlight {
      color: var(--primary);
      font-size: 0.9rem;
    }

    .metric-sub {
      font-size: 0.675rem;
      color: var(--text-muted);
      display: block;
      white-space: nowrap;
      margin-top: 1px;
    }

    /* Comments cell */
    .comments-cell {
      min-width: 220px;
      font-size: 0.785rem;
      color: var(--text);
    }

    .comments-cell ul {
      list-style-type: none;
      padding-left: 0;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .comments-cell li {
      position: relative;
      padding-left: 11px;
      line-height: 1.3;
    }

    .comments-cell li::before {
      content: "•";
      position: absolute;
      left: 0;
      color: var(--primary);
      font-weight: bold;
    }

    footer {
      text-align: center;
      font-size: 0.76rem;
      color: var(--text-muted);
      padding: 12px 0 8px;
      border-top: 1px solid var(--border);
    }

    /* Print styles */
    @media print {
      body {
        background: #fff !important;
        color: #000 !important;
        padding: 0;
      }
      .header-actions, .product-thumb:hover {
        display: none !important;
      }
      .table-wrapper {
        border: none;
        box-shadow: none;
      }
      table {
        font-size: 7pt;
      }
      th, td {
        padding: 3px 5px;
        border: 1px solid #ccc;
      }
      .product-thumb {
        width: 28px;
        height: 28px;
      }
      .store-link {
        color: #000;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-top">
        <h1>
          <span class="icon">🔦</span> Orienteringspannlampor – Jämförelse
        </h1>
        <div class="header-actions">
          <button id="themeToggle" class="btn" title="Växla ljust/mörkt läge">
            <span id="themeIcon">☀️</span> Ljust läge
          </button>
          <button id="printBtn" class="btn" title="Skriv ut / spara som PDF">
            🖨️ Skriv ut
          </button>
        </div>
      </div>
    </header>

    <!-- Table -->
    <div class="table-wrapper">
      <table id="headlampsTable">
        <thead>
          <tr>
            <th class="no-sort col-image">Bild</th>
            <th data-sort="model" class="col-model">Modell <span class="sort-icon"></span></th>
            <th data-sort="year" class="col-num col-year">Lanseringsår <span class="sort-icon"></span></th>
            <th class="no-sort col-stores">Svenska Butiker &amp; Pris</th>
            <th data-sort="price" class="col-num">Lägsta Pris <span class="sort-icon"></span></th>
            <th data-sort="lumen" class="col-num">Lumen <span class="sort-icon"></span></th>
            <th data-sort="runtime" class="col-num">Drifttid <span class="sort-icon"></span></th>
            <th data-sort="capacity" class="col-num">Kapacitet <span class="sort-icon"></span></th>
            <th data-sort="weight" class="col-num">Batterivikt <span class="sort-icon"></span></th>
            <th data-sort="headweight" class="col-num">Huvudvikt <span class="sort-icon"></span></th>
            <th class="no-sort comments-cell">Kommentar &amp; Egenskaper</th>
          </tr>
        </thead>
        <tbody id="tableBody">
"""

HTML_POSTAMBLE = """        </tbody>
      </table>
    </div>

    <footer>
      Orienteringspannlampor Sammanställning • Priser och specifikationer verifierade 2026-09
    </footer>
  </div>

  <script>
    // State
    let sortColumn = "lumen";
    let sortDirection = "desc";

    const tableBody = document.getElementById("tableBody");
    const rows = Array.from(tableBody.querySelectorAll("tr"));
    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");
    const printBtn = document.getElementById("printBtn");

    function initTheme() {
      const savedTheme = localStorage.getItem("headlamp_theme");
      if (savedTheme) {
        document.documentElement.setAttribute("data-theme", savedTheme);
        updateThemeBtn(savedTheme);
      } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
        document.documentElement.setAttribute("data-theme", "light");
        updateThemeBtn("light");
      }
    }

    function updateThemeBtn(theme) {
      if (theme === "light") {
        themeIcon.textContent = "🌙";
        themeToggle.innerHTML = '<span id="themeIcon">🌙</span> Mörkt läge';
      } else {
        themeIcon.textContent = "☀️";
        themeToggle.innerHTML = '<span id="themeIcon">☀️</span> Ljust läge';
      }
    }

    themeToggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("headlamp_theme", next);
      updateThemeBtn(next);
    });

    printBtn.addEventListener("click", () => {
      window.print();
    });

    function sortRows() {
      rows.sort((a, b) => {
        let valA, valB;
        if (sortColumn === "model") {
          valA = a.querySelector(".product-name").innerText.toLowerCase();
          valB = b.querySelector(".product-name").innerText.toLowerCase();
          return sortDirection === "asc" ? valA.localeCompare(valB) : valB.localeCompare(valA);
        } else if (sortColumn === "year") {
          valA = parseInt(a.dataset.year || "0", 10);
          valB = parseInt(b.dataset.year || "0", 10);
        } else if (sortColumn === "price") {
          valA = parseInt(a.dataset.price || "0", 10);
          valB = parseInt(b.dataset.price || "0", 10);
        } else if (sortColumn === "lumen") {
          valA = parseInt(a.dataset.lumen || "0", 10);
          valB = parseInt(b.dataset.lumen || "0", 10);
        } else if (sortColumn === "runtime") {
          valA = parseInt(a.dataset.runtime || "0", 10);
          valB = parseInt(b.dataset.runtime || "0", 10);
        } else if (sortColumn === "capacity") {
          valA = parseInt(a.dataset.capacity || "0", 10);
          valB = parseInt(b.dataset.capacity || "0", 10);
        } else if (sortColumn === "weight") {
          valA = parseInt(a.dataset.weight || "0", 10);
          valB = parseInt(b.dataset.weight || "0", 10);
        } else if (sortColumn === "headweight") {
          valA = parseInt(a.dataset.headweight || "0", 10);
          valB = parseInt(b.dataset.headweight || "0", 10);
        }

        return sortDirection === "asc" ? (valA - valB) : (valB - valA);
      });

      rows.forEach(row => tableBody.appendChild(row));
    }

    document.querySelectorAll("th[data-sort]").forEach(th => {
      th.addEventListener("click", () => {
        const col = th.dataset.sort;
        if (sortColumn === col) {
          sortDirection = sortDirection === "asc" ? "desc" : "asc";
        } else {
          sortColumn = col;
          sortDirection = (col === "price" || col === "weight" || col === "headweight") ? "asc" : "desc";
        }

        document.querySelectorAll("th[data-sort]").forEach(t => {
          t.classList.remove("sorted-asc", "sorted-desc");
        });

        th.classList.add(sortDirection === "asc" ? "sorted-asc" : "sorted-desc");
        sortRows();
      });
    });

    const initialSortTh = document.querySelector('th[data-sort="lumen"]');
    if (initialSortTh) {
      initialSortTh.classList.add("sorted-desc");
    }

    initTheme();
    sortRows();
  </script>
</body>
</html>
"""


def parse_bool(val: str, default: bool = False) -> bool:
    val_str = str(val).strip().lower()
    if val_str in ("true", "1", "yes", "ja", "t"):
        return True
    if val_str in ("false", "0", "no", "nej", "f"):
        return False
    return default


def parse_stores(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            return json.loads(raw)
        except Exception:
            pass
    stores = []
    for item in raw.split(";;"):
        item = item.strip()
        if not item:
            continue
        parts = [p.strip() for p in item.split("|")]
        name = parts[0] if len(parts) > 0 else ""
        url = parts[1] if len(parts) > 1 else ""
        price_str = parts[2] if len(parts) > 2 else "0"
        try:
            price_sek = int(price_str.replace(" ", ""))
        except ValueError:
            price_sek = 0
        note = parts[3] if len(parts) > 3 else ""
        stores.append({
            "name": name,
            "url": url,
            "price_sek": price_sek,
            "note": note
        })
    return stores


def parse_comments(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            return json.loads(raw)
        except Exception:
            pass
    return [c.strip() for c in raw.split(";;") if c.strip()]


def load_headlamps_from_tsv(tsv_path: Path):
    if not tsv_path.exists():
        raise FileNotFoundError(f"Hittade inte TSV-filen: {tsv_path}")

    headlamps = []
    with open(tsv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if not row.get("id"):
                continue

            lumen = int(row.get("lumen") or 0)
            stores = parse_stores(row.get("stores", ""))
            comments = parse_comments(row.get("comments", ""))

            # Calculate lowest price
            prices = [s["price_sek"] for s in stores if s.get("price_sek")]
            min_price = min(prices) if prices else 0
            primary_store = next((s for s in stores if s.get("price_sek") == min_price), stores[0] if stores else {"url": "#"})
            primary_url = primary_store.get("url", "#")

            battery_weight_g = int(row.get("battery_weight_g") or 0)
            battery_weight_text = row.get("battery_weight_text") or f"{battery_weight_g} g"

            head_weight_g = int(row.get("head_weight_g") or 0)
            head_weight_text = row.get("head_weight_text") or f"{head_weight_g} g"

            meets_3000lm = parse_bool(row.get("meets_3000lm", ""), default=(lumen >= 3000))

            headlamps.append({
                "id": row.get("id"),
                "model": row.get("model", ""),
                "brand": row.get("brand", ""),
                "release_year": int(row.get("release_year") or 0),
                "image_url": row.get("image_url", ""),
                "lumen": lumen,
                "runtime_text": row.get("runtime_text", ""),
                "runtime_min": int(row.get("runtime_min") or 0),
                "capacity_wh": int(row.get("capacity_wh") or 0),
                "capacity_sub": row.get("capacity_sub", ""),
                "battery_weight_g": battery_weight_g,
                "battery_weight_text": battery_weight_text,
                "head_weight_g": head_weight_g,
                "head_weight_text": head_weight_text,
                "head_weight_sub": row.get("head_weight_sub", ""),
                "meets_3000lm": meets_3000lm,
                "comments": comments,
                "stores": stores,
                "lowest_price_sek": min_price,
                "primary_url": primary_url,
            })
    return headlamps


def generate_rows_html(headlamps):
    rows_html = []
    for h in headlamps:
        highlight_cls = "highlight-orientering" if h["meets_3000lm"] else ""
        comments_li = "\n".join(f"                <li>{c}</li>" for c in h["comments"])
        
        store_rows = []
        min_p = h["lowest_price_sek"]
        for s in h["stores"]:
            is_lowest = (s["price_sek"] == min_p)
            lowest_badge = ' is-lowest' if is_lowest else ''
            p_formatted = f"{s['price_sek']:,}".replace(",", " ")
            note_span = f' <span class="store-note">({s["note"]})</span>' if s.get("note") else ''
            store_rows.append(
                f'                <div class="store-row">'
                f'<a href="{s["url"]}" target="_blank" rel="noopener noreferrer" class="store-link" title="{s["name"]}">'
                f'{s["name"]}'
                f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'
                f'</a>'
                f'<span class="store-price{lowest_badge}">{p_formatted} kr{note_span}</span>'
                f'</div>'
            )
        stores_html = "\n".join(store_rows)

        price_formatted = f"{h['lowest_price_sek']:,}".replace(",", " ")
        lumen_formatted = f"{h['lumen']:,}".replace(",", " ")
        head_sub_html = f'\n              <span class="metric-sub">{h["head_weight_sub"]}</span>' if h.get("head_weight_sub") else ''

        row = f"""          <tr data-lumen="{h['lumen']}" data-price="{h['lowest_price_sek']}" data-runtime="{h['runtime_min']}" data-capacity="{h['capacity_wh']}" data-weight="{h['battery_weight_g']}" data-headweight="{h['head_weight_g']}" data-year="{h['release_year']}" class="{highlight_cls}">
            <td class="col-image">
              <a href="{h['primary_url']}" target="_blank" rel="noopener noreferrer">
                <img src="{h['image_url']}" alt="{h['model']}" class="product-thumb" loading="lazy">
              </a>
            </td>
            <td class="col-model">
              <div class="product-name">{h['model']}</div>
            </td>
            <td class="col-num col-year">
              <div class="metric-value">{h['release_year']}</div>
            </td>
            <td class="col-stores">
              <div class="store-list">
{stores_html}
              </div>
            </td>
            <td class="col-num">
              <div class="metric-value price-highlight">{price_formatted} kr</div>
              <span class="metric-sub">Lägsta pris</span>
            </td>
            <td class="col-num">
              <div class="metric-value">{lumen_formatted} lm</div>
            </td>
            <td class="col-num">
              <div class="metric-value">{h['runtime_text']}</div>
            </td>
            <td class="col-num">
              <div class="metric-value">{h['capacity_wh']} Wh</div>
              <span class="metric-sub">{h['capacity_sub']}</span>
            </td>
            <td class="col-num">
              <div class="metric-value">{h['battery_weight_text']}</div>
            </td>
            <td class="col-num">
              <div class="metric-value">{h['head_weight_text']}</div>{head_sub_html}
            </td>
            <td class="comments-cell">
              <ul>
{comments_li}
              </ul>
            </td>
          </tr>"""
        rows_html.append(row)

    return "\n\n".join(rows_html)


def main():
    parser = argparse.ArgumentParser(description="Generera index.html från headlamps.tsv")
    parser.add_argument(
        "--tsv",
        type=Path,
        default=Path(__file__).resolve().parent / "headlamps.tsv",
        help="Sökväg till headlamps.tsv"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "index.html",
        help="Sökväg till output HTML-fil"
    )
    args = parser.parse_args()

    print(f"Läser rådata från: {args.tsv}")
    headlamps = load_headlamps_from_tsv(args.tsv)
    print(f"Hittade {len(headlamps)} pannlampor.")

    rows_str = generate_rows_html(headlamps)
    full_html = HTML_PREAMBLE + rows_str + "\n" + HTML_POSTAMBLE

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"HTML genererad och sparad till: {args.output}")


if __name__ == "__main__":
    main()
