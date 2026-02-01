from pytrends.request import TrendReq
import pandas as pd


def _get_pytrends():
    """Create and return a TrendReq instance."""
    # tz=360 corresponds to UTC+6; use 0 for UTC if you prefer local times
    return TrendReq(hl="en-US", tz=0)

def interest_over_time(keywords, timeframe="today 12-m", geo="US"):
    """Return interest over time for comma-separated keywords.

    Returns a list of dicts: [{"date": "YYYY-MM-DD", "keyword1": 23, ...}, ...]
    """
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
    if not kw_list:
        return []

    pytrends = _get_pytrends()
    pytrends.build_payload(kw_list, timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time()
    if df is None or df.empty:
        return []

    # Drop isPartial column if present
    if "isPartial" in df.columns:
        df = df.drop(columns=["isPartial")

    results = []
    for idx, row in df.iterrows():
        entry = {"date": idx.strftime("%Y-%m-%d")}
        for kw in kw_list:
            val = row.get(kw, 0)
            try:
                entry[kw] = int(val) if pd.notna(val) else 0
            except Exception:
                entry[kw] = val
        results.append(entry)
    return results

def interest_by_region(keywords, timeframe="today 12-m", geo="", resolution="COUNTRY"):
    """Return interest by region.

    Returns list of dicts: [{"region": name, "keyword": kw, "value": int}, ...]
    """
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
    if not kw_list:
        return []

    pytrends = _get_pytrends()
    pytrends.build_payload(kw_list, timeframe=timeframe, geo=geo)
    df = pytrends.interest_by_region(resolution=resolution, inc_low_vol=True, inc_geo_code=False)
    if df is None or df.empty:
        return []

    results = []
    for region, row in df.iterrows():
        for kw in kw_list:
            val = row.get(kw, 0)
            try:
                v = int(val) if pd.notna(val) else 0
            except Exception:
                v = val
            results.append({"region": str(region), "keyword": kw, "value": v})
    return results

def related_topics(keyword, timeframe="today 12-m", geo="", top_or_rising="top"):
    """Return related topics for a single keyword.

    top_or_rising should be 'top' or 'rising'. Returns list of dicts with topic info.
    """
    if not keyword:
        return []

    pytrends = _get_pytrends()
    kw_list = [keyword]
    pytrends.build_payload(kw_list, timeframe=timeframe, geo=geo)
    rt = pytrends.related_topics()
    key = kw_list[0]
    if key not in rt or rt[key] is None:
        return []

    df = rt[key].get(top_or_rising)
    if df is None or df.empty:
        return []

    results = []
    for _, row in df.iterrows():
        # pytrends often returns columns like 'topic_title', 'topic_type' and 'value'
        title = row.get("topic_title") or row.get("topic") or row.get("value")
        ttype = row.get("topic_type") or row.get("type")
        value = row.get("value")
        try:
            value = int(value) if pd.notna(value) else None
        except Exception:
            pass
        results.append({"topic_title": title, "type": ttype, "value": value})
    return results

def related_queries(keyword, timeframe="today 12-m", geo="", top_or_rising="top"):
    """Return related queries for a single keyword.

    Returns list of {"query": str, "value": int|None}.
    """
    if not keyword:
        return []

    pytrends = _get_pytrends()
    kw_list = [keyword]
    pytrends.build_payload(kw_list, timeframe=timeframe, geo=geo)
    rq = pytrends.related_queries()
    key = kw_list[0]
    if key not in rq or rq[key] is None:
        return []

    df = rq[key].get(top_or_rising)
    if df is None or df.empty:
        return []

    results = []
    for _, row in df.iterrows():
        q = row.get("query") or row.get("value")
        val = row.get("value")
        try:
            val = int(val) if pd.notna(val) else None
        except Exception:
            pass
        results.append({"query": q, "value": val})
    return results

def trending_searches(geo="US"):
    """Return current trending searches for a region.

    geo examples: 'US', 'GLOBAL', 'GB'.
    """
    pn_map = {
        "US": "united_states",
        "GLOBAL": "global",
        "GB": "united_kingdom",
    }
    pn = pn_map.get(geo.upper(), "united_states")

    pytrends = _get_pytrends()
    df = pytrends.trending_searches(pn=pn)
    if df is None or df.empty:
        return []

    col = df.columns[0]
    return [str(x) for x in df[col].tolist()]