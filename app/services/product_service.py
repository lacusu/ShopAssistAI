"""
Enhanced Product Service for ShopAssistAI 2.0
Aligned with updated_laptop.csv which preprocessed already.
"""

import os
import re
import pandas as pd
from flask import current_app, session

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "updated_laptop.csv")

try:
    LAPTOP_DF = pd.read_csv(DATA_PATH)
    # Standardize column names
    LAPTOP_DF.columns = [c.strip().lower().replace(" ", "_") for c in LAPTOP_DF.columns]
    print(f"Loaded {len(LAPTOP_DF)} laptops from {DATA_PATH}")
except Exception as e:
    print(f"Warning: could not load laptop dataset at {DATA_PATH}: {e}")
    LAPTOP_DF = pd.DataFrame()


def _match(series, keyword):
    """Case-insensitive substring match that preserves index alignment."""
    if series is None or series.empty:
        return pd.Series([True] * 0)
    if not keyword:
        return pd.Series([True] * len(series), index=series.index)
    keyword = re.escape(keyword.lower())
    mask = series.astype(str).str.lower().str.contains(keyword, na=False)
    return mask.reindex(series.index, fill_value=False)


def map_products(filters: dict):
    if LAPTOP_DF.empty:
        return []

    df = LAPTOP_DF.copy()

    # --- Filter by brand ---
    brand = filters.get("brand", "")
    if "brand" in df.columns:
        df = df[_match(df["brand"], brand)]
        print(f"After brand filter '{brand}': {len(df)} items")

    # --- Filter by CPU / Core keywords ---
    cpu_kw = filters.get("cpu", "")
    if cpu_kw:
        mask_core = _match(df.get("core", ""), cpu_kw)
        mask_cpu_manu = _match(df.get("cpu_manufacturer", ""), cpu_kw)
        df = df[mask_core | mask_cpu_manu]
        print(f"After CPU filter '{cpu_kw}': {len(df)} items")

    # --- Filter by RAM ---
    ram_kw = filters.get("ram", "")
    if "ram_size" in df.columns:
        df = df[_match(df["ram_size"], ram_kw)]
        print(f"After RAM filter '{ram_kw}': {len(df)} items")

    # --- Filter by GPU / graphics processor ---
    gpu_kw = filters.get("gpu", "")
    if "graphics_processor" in df.columns:
        df = df[_match(df["graphics_processor"], gpu_kw)]
        print(f"After GPU filter '{gpu_kw}': {len(df)} items")

    # --- Filter by OS ---
    os_kw = filters.get("os", "")
    if "os" in df.columns:
        df = df[_match(df["os"], os_kw)]
        print(f"After OS filter '{os_kw}': {len(df)} items")

    # --- Filter by price range ---
    price_range = filters.get("price_range", "").lower()
    if "price" in df.columns:
        # Normalize price column to numeric
        df["price"] = (
            df["price"].astype(str).str.replace(r"[^0-9.]", "", regex=True).astype(float)
        )
        if "low" in price_range:
            df = df[df["price"] < 500]
        elif "mid" in price_range:
            df = df[(df["price"] >= 500) & (df["price"] <= 1000)]
        elif "high" in price_range:
            df = df[df["price"] > 1000]
        print(f"After price range filter '{price_range}': {len(df)} items")

    # --- Category keywords (expanded semantic matching) ---
    category_kw = filters.get("category", "").lower().strip()
    if category_kw:
        possible_cols = []
        if "laptop_feature" in df.columns:
            possible_cols.append(df["laptop_feature"])
        if "description" in df.columns:
            possible_cols.append(df["description"])
        if "graphics_processor" in df.columns:
            possible_cols.append(df["graphics_processor"])
        if "model_name" in df.columns:
            possible_cols.append(df["model_name"])

        combined_text = pd.Series([" ".join(map(str, vals)) for vals in zip(*possible_cols)], index=df.index)

        synonyms = {
            "gaming": ["gaming", "rtx", "gtx", "radeon", "high performance", "graphics", "rog", "legion", "tuf",
                       "predator"],
            "office": ["office", "thin", "lightweight", "ultrabook", "daily use"],
            "business": ["business", "probook", "elitebook", "thinkpad"],
            "student": ["student", "affordable", "basic", "budget"],
        }
        keywords = synonyms.get(category_kw, [category_kw])

        mask = pd.Series([False] * len(df), index=df.index)
        for kw in keywords:
            mask |= _match(combined_text, kw)

        df = df[mask]
        print(f"After category fallback filter '{category_kw}': {len(df)} items")

    limit = int(filters.get("limit", 10))
    results = df.head(limit).to_dict(orient="records")
    if current_app:
        current_app.logger.info(f"[ProductService] {len(results)} matches for {filters}")
    return results


# ---------------------------------------------------------------------
# Text formatter
# ---------------------------------------------------------------------
def recommend_products(data: dict) -> str:
    products = data.get("products", [])
    message = data.get("message", "Here are some products you might like:")
    if not products:
        not_found_msg = f"Sorry, I couldn't find any products matching your criteria. Please try different filters."
        # session["history"] = [
        #     {
        #         "role": "system",
        #         "content": not_found_msg
        #     }
        # ]
        return not_found_msg

    html_lines = [f"{message}<p>"]
    for i, p in enumerate(products, start=1):
        brand = str(p.get("brand", "")).title()
        model = str(p.get("model_name", "")).title()
        cpu = str(p.get("core", "") or p.get("cpu_manufacturer", "")).title()
        ram = str(p.get("ram_size", "")).upper()
        gpu = str(p.get("graphics_processor", "")).title()
        price_val = p.get("price", "N/A")

        try:
            price_num = float(str(price_val).replace(",", "").replace("$", ""))
            price_fmt = f"${price_num:,.0f}"
        except:
            price_fmt = str(price_val)

        html_lines.append(
            f"<div class='product-row'>"
            f"<div class='product-info'>{i}. {brand} <b>{model}</b> — {cpu} | {ram} | {gpu}</div>"
            f"<div class='product-price'>💲{price_fmt}</div>"
            f"</div>"
        )

    html_lines.append("</p>")
    html_text = "\n".join(html_lines)

    if current_app:
        current_app.logger.info(f"[ProductService] Recommended {len(products)} items.")
    return html_text
