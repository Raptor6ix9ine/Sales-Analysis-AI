from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class SalesRow:
    """Represents a single sales data row"""
    date: datetime
    product: str
    revenue: float
    quantity: int
    region: str


@dataclass
class KPIs:
    """Key Performance Indicators"""
    totalRevenue: float
    totalOrders: int
    growthRate: float
    avgOrderValue: float
    topProduct: str
    topRegion: str


@dataclass
class ChartData:
    """Chart data structure"""
    labels: List[str]
    data: List[float]


@dataclass
class Charts:
    """All chart data"""
    salesOverTime: ChartData
    revenueByProduct: ChartData
    revenueByRegion: ChartData


@dataclass
class Insight:
    """A single insight"""
    type: str  # "warn", "good", or "info"
    text: str


@dataclass
class Recommendation:
    """A single recommendation"""
    icon: str
    text: str


@dataclass
class Forecast:
    """Forecast data"""
    nextWeek: float
    nextMonth: float
    growthTrend: str
    anomaly: Optional[str]


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    kpis: KPIs
    charts: Charts
    insights: List[Insight]
    recommendations: List[Recommendation]
    forecast: Forecast
    summary: str


def validate_columns(headers: List[str]) -> List[str]:
    """Validate that required columns are present in CSV headers (O(n))"""
    required = {"date", "product", "revenue", "quantity", "region"}
    normalized = {h.strip().lower() for h in headers}
    return list(required - normalized)


def _parse_number(value_str: str, is_int: bool = False) -> Optional[float]:
    """Helper to parse numeric values safely"""
    try:
        if is_int:
            return float(int(''.join(c for c in value_str if c.isdigit())))
        return float(''.join(c for c in value_str if c.isdigit() or c in '.-'))
    except (ValueError, IndexError):
        return None


def parse_rows(raw_rows: List[Dict[str, str]]) -> Tuple[List[SalesRow], List[str]]:
    """Parse and validate raw CSV rows (O(n))"""
    rows: List[SalesRow] = []
    warnings: List[str] = []
    
    for i, raw_row in enumerate(raw_rows, 2):
        # Normalize keys to lowercase (O(1) per row)
        keys = {k.strip().lower(): v.strip() if v else "" for k, v in raw_row.items()}
        
        date_raw = keys.get("date", "")
        product_raw = keys.get("product", "")
        revenue_raw = keys.get("revenue", "")
        quantity_raw = keys.get("quantity", "")
        region_raw = keys.get("region", "")
        
        # Check for missing values
        if not all([date_raw, product_raw, revenue_raw, quantity_raw, region_raw]):
            warnings.append(f"Row {i}: missing values, skipped")
            continue
        
        # Parse date
        try:
            date = datetime.fromisoformat(date_raw.split('T')[0])
        except (ValueError, IndexError):
            warnings.append(f"Row {i}: invalid date \"{date_raw}\", skipped")
            continue
        
        # Parse revenue and quantity
        revenue = _parse_number(revenue_raw, is_int=False)
        quantity = _parse_number(quantity_raw, is_int=True)
        
        if revenue is None or quantity is None:
            warnings.append(f"Row {i}: invalid numbers, skipped")
            continue
        
        rows.append(SalesRow(
            date=date,
            product=product_raw,
            revenue=revenue,
            quantity=int(quantity)
        ))
    
    return rows, warnings


def _group_by_key(items: List[SalesRow], key_fn) -> Dict[str, List[SalesRow]]:
    """Group items by key function (O(n))"""
    result: Dict[str, List[SalesRow]] = defaultdict(list)
    for item in items:
        result[key_fn(item)].append(item)
    return dict(result)


def _sum(values: List[float]) -> float:
    """Sum with early exit for empty list"""
    return sum(values) if values else 0.0


def _avg(values: List[float]) -> float:
    """Average with division safety"""
    length = len(values)
    return sum(values) / length if length > 0 else 0.0


def _format_currency(n: float) -> str:
    """Format number as currency (fixed)"""
    if n >= 1_000_000:
        return f"${n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"${n / 1_000:.1f}K"
    else:
        return f"${n:.0f}"


def analyze(rows: List[SalesRow]) -> AnalysisResult:
    """Perform comprehensive analysis on sales data (O(n log n) due to sorting)"""
    if not rows:
        raise ValueError("No rows to analyze")
    
    # Sort by date once (O(n log n))
    rows.sort(key=lambda r: r.date)
    
    # ── Basic KPIs (O(n)) ───────────────────────────────────────────────────
    total_revenue = _sum([r.revenue for r in rows])
    total_orders = len(rows)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
    
    # ── Sales over time weekly buckets (O(n)) ────────────────────────────────
    by_week: Dict[str, float] = {}
    for row in rows:
        d = row.date
        start_of_week = d - timedelta(days=d.weekday() + 1)
        label = start_of_week.strftime("%b %d")
        by_week[label] = by_week.get(label, 0) + row.revenue
    
    week_labels = list(by_week.keys())
    week_data = list(by_week.values())
    
    # ── Growth rate: last 25% vs previous 25% (O(n)) ───────────────────────
    quarter = max(1, len(rows) // 4)
    recent_rows = rows[-quarter:]
    prev_rows = rows[-quarter * 2:-quarter]
    recent_revenue = _sum([r.revenue for r in recent_rows])
    prev_revenue = _sum([r.revenue for r in prev_rows])
    growth_rate = ((recent_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0.0
    
    # ── Revenue by product (O(n)) ──────────────────────────────────────────
    by_product = _group_by_key(rows, lambda r: r.product)
    product_revenues = sorted(
        [{"name": name, "revenue": _sum([r.revenue for r in rs])} 
         for name, rs in by_product.items()],
        key=lambda x: x["revenue"],
        reverse=True
    )
    
    top_product = product_revenues[0]["name"] if product_revenues else "N/A"
    top_product_pct = (product_revenues[0]["revenue"] / total_revenue * 100) if total_revenue > 0 and product_revenues else 0.0
    
    # ── Revenue by region (O(n)) ───────────────────────────────────────────
    by_region = _group_by_key(rows, lambda r: r.region)
    region_revenues = sorted(
        [{"name": name, "revenue": _sum([r.revenue for r in rs])} 
         for name, rs in by_region.items()],
        key=lambda x: x["revenue"],
        reverse=True
    )
    
    top_region = region_revenues[0]["name"] if region_revenues else "N/A"
    worst_region = region_revenues[-1] if region_revenues else None
    avg_region_revenue = _avg([r["revenue"] for r in region_revenues])
    worst_region_drop_pct = (
        ((avg_region_revenue - worst_region["revenue"]) / avg_region_revenue * 100)
        if avg_region_revenue > 0 and worst_region else 0.0
    )
    
    # ── Anomaly detection (O(n)) ──────────────────────────────────────────
    by_day: Dict[str, float] = {}
    for row in rows:
        label = row.date.strftime("%Y-%m-%d")
        by_day[label] = by_day.get(label, 0) + row.revenue
    
    day_revenues = [{"d": d, "v": v} for d, v in by_day.items()]
    avg_day = _avg([x["v"] for x in day_revenues])
    anomaly_day = next((x for x in day_revenues if x["v"] > avg_day * 2.5), None)
    
    anomaly_label = None
    if anomaly_day:
        anomaly_date = datetime.fromisoformat(anomaly_day["d"])
        anomaly_label = f"Unusual spike on {anomaly_date.strftime('%b %d')} — {anomaly_day['v'] / avg_day:.1f}x above average"
    
    # ── Forecast (O(1))─────────────────────────────────────────────────────
    wlen = len(week_data)
    slope = 0.0
    if wlen >= 2:
        last4 = week_data[-min(4, wlen):]
        slope = (last4[-1] - last4[0]) / (len(last4) - 1)
    
    last_week_revenue = week_data[-1] if wlen > 0 else avg_order_value * 10
    next_week_forecast = max(0, last_week_revenue + slope)
    next_month_forecast = max(0, next_week_forecast * 4 + slope * 10)
    
    growth_trend = "Upward trend" if slope > 0 else "Declining trend" if slope < 0 else "Stable"
    
    # ── Insights (O(1)) ────────────────────────────────────────────────────
    insights: List[Insight] = []
    
    if growth_rate < -10:
        insights.append(Insight(type="warn", text=f"Revenue dropped {abs(growth_rate):.1f}% recently — may signal seasonal dip or competitive pressure."))
    elif growth_rate > 10:
        insights.append(Insight(type="good", text=f"Revenue grew {growth_rate:.1f}% in the latest period — strong positive momentum."))
    else:
        insights.append(Insight(type="info", text=f"Revenue is relatively stable with {abs(growth_rate):.1f}% change in the latest period."))
    
    insights.append(Insight(type="good", text=f"\"{top_product}\" is your top product, contributing {top_product_pct:.0f}% of total revenue."))
    
    if worst_region and worst_region_drop_pct > 15:
        insights.append(Insight(type="warn", text=f"{worst_region['name']} region is underperforming by {worst_region_drop_pct:.0f}% below the regional average."))
    
    insights.append(Insight(type="good", text=f"Average order value is {_format_currency(avg_order_value)} across {total_orders:,} orders."))
    
    if anomaly_day:
        insights.append(Insight(type="warn", text=f"Anomaly detected: {anomaly_label}"))
    
    if len(product_revenues) > 1:
        bottom_product = product_revenues[-1]
        bottom_pct = (bottom_product["revenue"] / total_revenue * 100) if total_revenue > 0 else 0.0
        if bottom_pct < 10:
            insights.append(Insight(type="warn", text=f"\"{bottom_product['name']}\" contributes only {bottom_pct:.1f}% of revenue — consider reviewing its positioning."))
    
    # ── Recommendations (O(1)) ──────────────────────────────────────────────
    recs: List[Recommendation] = []
    
    recs.append(Recommendation(icon="bullseye", text=f"Increase marketing budget for \"{top_product}\" — it drives {top_product_pct:.0f}% of your revenue with the highest ROI."))
    
    if worst_region and worst_region_drop_pct > 15:
        recs.append(Recommendation(icon="magnifying-glass", text=f"Investigate \"{worst_region['name']}\" region — assign a dedicated rep or run a targeted campaign to close the {worst_region_drop_pct:.0f}% performance gap."))
    
    if growth_rate < -10:
        recs.append(Recommendation(icon="chart-line", text="Revenue is declining — consider running promotions or discounts to re-engage customers and reverse the trend."))
    else:
        recs.append(Recommendation(icon="boxes-stacked", text=f"Maintain inventory levels for \"{top_product}\" — demand trend suggests continued strong performance."))
    
    if len(product_revenues) > 1:
        recs.append(Recommendation(icon="user-tie", text=f"Bundle \"{top_product}\" with lower-performing products to lift overall average order value."))
    
    # ── Summary sentence ────────────────────────────────────────────────────
    summary = f"Analysis of {total_orders:,} orders totalling {_format_currency(total_revenue)}. {'Growing' if growth_rate >= 0 else 'Declining'} at {abs(growth_rate):.1f}% with \"{top_product}\" leading."
    
    # ── Build result ────────────────────────────────────────────────────────
    return AnalysisResult(
        kpis=KPIs(
            totalRevenue=total_revenue,
            totalOrders=total_orders,
            growthRate=growth_rate,
            avgOrderValue=avg_order_value,
            topProduct=top_product,
            topRegion=top_region
        ),
        charts=Charts(
            salesOverTime=ChartData(labels=week_labels, data=week_data),
            revenueByProduct=ChartData(labels=[p["name"] for p in product_revenues], data=[p["revenue"] for p in product_revenues]),
            revenueByRegion=ChartData(labels=[r["name"] for r in region_revenues], data=[r["revenue"] for r in region_revenues])
        ),
        insights=insights,
        recommendations=recs,
        forecast=Forecast(
            nextWeek=next_week_forecast,
            nextMonth=next_month_forecast,
            growthTrend=growth_trend,
            anomaly=anomaly_label
        ),
        summary=summary
    )


def parse_rows(raw_rows: List[Dict[str, str]]) -> Tuple[List[SalesRow], List[str]]:
    """
    Parse and validate raw CSV rows.
    Returns tuple of (parsed rows, warnings)
    """
    rows: List[SalesRow] = []
    warnings: List[str] = []
    
    for i, raw_row in enumerate(raw_rows):
        # Normalize keys to lowercase
        keys = {k.strip().lower(): v.strip() if v else "" for k, v in raw_row.items()}
        
        date_raw = keys.get("date", "")
        product_raw = keys.get("product", "")
        revenue_raw = keys.get("revenue", "")
        quantity_raw = keys.get("quantity", "")
        region_raw = keys.get("region", "")
        
        # Check for missing values
        if not all([date_raw, product_raw, revenue_raw, quantity_raw, region_raw]):
            warnings.append(f"Row {i + 2}: missing values, skipped")
            continue
        
        # Parse date
        try:
            date = datetime.fromisoformat(date_raw.split('T')[0])
        except (ValueError, IndexError):
            warnings.append(f"Row {i + 2}: invalid date \"{date_raw}\", skipped")
            continue
        
        # Parse revenue (remove currency symbols and whitespace)
        try:
            revenue = float(''.join(c for c in revenue_raw if c.isdigit() or c in '.-'))
        except ValueError:
            warnings.append(f"Row {i + 2}: invalid revenue number, skipped")
            continue
        
        # Parse quantity
        try:
            quantity = int(''.join(c for c in quantity_raw if c.isdigit()))
        except ValueError:
            warnings.append(f"Row {i + 2}: invalid quantity number, skipped")
            continue
        
        rows.append(SalesRow(
            date=date,
            product=product_raw,
            revenue=revenue,
            quantity=quantity,
            region=region_raw
        ))
    
    return rows, warnings


def _group_by(items: List[SalesRow], key_fn) -> Dict[str, List[SalesRow]]:
    """Group items by a key function"""
    result: Dict[str, List[SalesRow]] = defaultdict(list)
    for item in items:
        k = key_fn(item)
        result[k].append(item)
    return dict(result)


def _sum(values: List[float]) -> float:
    """Sum a list of floats"""
    return sum(values) if values else 0


def _avg(values: List[float]) -> float:
    """Calculate average of a list of floats"""
    return sum(values) / len(values) if values else 0


def _format_currency(n: float) -> str:
    """Format a number as currency"""
    if n >= 1_000_000:
        return f"${n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"${n / 1_000:.1f}K"
    else:
        return f"${n:.0f}"


def analyze(rows: List[SalesRow]) -> AnalysisResult:
    """
    Perform comprehensive analysis on sales data.
    """
    # Sort by date
    rows.sort(key=lambda r: r.date)
    
    # ── Basic KPIs ──────────────────────────────────────────────────────────
    total_revenue = _sum([r.revenue for r in rows])
    total_orders = len(rows)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # ── Sales over time (weekly buckets) ─────────────────────────────────────
    by_week: Dict[str, float] = {}
    for row in rows:
        d = row.date
        # Get start of week (Sunday)
        start_of_week = d - timedelta(days=d.weekday() + 1)
        label = start_of_week.strftime("%b %d")
        by_week[label] = by_week.get(label, 0) + row.revenue
    
    week_labels = list(by_week.keys())
    week_data = list(by_week.values())
    
    # ── Growth rate: last 25% vs previous 25% ────────────────────────────────
    quarter = max(1, len(rows) // 4)
    recent_rows = rows[-quarter:]
    prev_rows = rows[-quarter * 2:-quarter]
    recent_revenue = _sum([r.revenue for r in recent_rows])
    prev_revenue = _sum([r.revenue for r in prev_rows])
    growth_rate = ((recent_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
    
    # ── Revenue by product ──────────────────────────────────────────────────
    by_product = _group_by(rows, lambda r: r.product)
    product_revenues = sorted(
        [{"name": name, "revenue": _sum([r.revenue for r in rs])} 
         for name, rs in by_product.items()],
        key=lambda x: x["revenue"],
        reverse=True
    )
    
    top_product = product_revenues[0]["name"] if product_revenues else "N/A"
    top_product_pct = (product_revenues[0]["revenue"] / total_revenue * 100) if total_revenue > 0 and product_revenues else 0
    
    # ── Revenue by region ───────────────────────────────────────────────────
    by_region = _group_by(rows, lambda r: r.region)
    region_revenues = sorted(
        [{"name": name, "revenue": _sum([r.revenue for r in rs])} 
         for name, rs in by_region.items()],
        key=lambda x: x["revenue"],
        reverse=True
    )
    
    top_region = region_revenues[0]["name"] if region_revenues else "N/A"
    worst_region = region_revenues[-1] if region_revenues else None
    avg_region_revenue = _avg([r["revenue"] for r in region_revenues])
    worst_region_drop_pct = (
        ((avg_region_revenue - worst_region["revenue"]) / avg_region_revenue * 100)
        if avg_region_revenue > 0 and worst_region else 0
    )
    
    # ── Anomaly detection ───────────────────────────────────────────────────
    by_day: Dict[str, float] = {}
    for row in rows:
        label = row.date.strftime("%Y-%m-%d")
        by_day[label] = by_day.get(label, 0) + row.revenue
    
    day_revenues = [{"d": d, "v": v} for d, v in by_day.items()]
    avg_day = _avg([x["v"] for x in day_revenues])
    anomaly_day = next((x for x in day_revenues if x["v"] > avg_day * 2.5), None)
    
    anomaly_label = None
    if anomaly_day:
        anomaly_date = datetime.fromisoformat(anomaly_day["d"])
        anomaly_label = f"Unusual spike on {anomaly_date.strftime('%b %d')} — {anomaly_day['v'] / avg_day:.1f}x above average"
    
    # ── Forecast (simple linear extrapolation on weekly data) ────────────────
    wlen = len(week_data)
    slope = 0
    if wlen >= 2:
        last4 = week_data[-min(4, wlen):]
        slope = (last4[-1] - last4[0]) / (len(last4) - 1)
    
    last_week_revenue = week_data[-1] if wlen > 0 else avg_order_value * 10
    next_week_forecast = max(0, last_week_revenue + slope)
    next_month_forecast = max(0, next_week_forecast * 4 + slope * 10)
    
    if slope > 0:
        growth_trend = "Upward trend"
    elif slope < 0:
        growth_trend = "Declining trend"
    else:
        growth_trend = "Stable"
    
    # ── Insights ────────────────────────────────────────────────────────────
    insights: List[Insight] = []
    
    if growth_rate < -10:
        insights.append(Insight(
            type="warn",
            text=f"Revenue dropped {abs(growth_rate):.1f}% recently — may signal seasonal dip or competitive pressure."
        ))
    elif growth_rate > 10:
        insights.append(Insight(
            type="good",
            text=f"Revenue grew {growth_rate:.1f}% in the latest period — strong positive momentum."
        ))
    else:
        insights.append(Insight(
            type="info",
            text=f"Revenue is relatively stable with {abs(growth_rate):.1f}% change in the latest period."
        ))
    
    insights.append(Insight(
        type="good",
        text=f"\"{top_product}\" is your top product, contributing {top_product_pct:.0f}% of total revenue."
    ))
    
    if worst_region and worst_region_drop_pct > 15:
        insights.append(Insight(
            type="warn",
            text=f"{worst_region['name']} region is underperforming by {worst_region_drop_pct:.0f}% below the regional average."
        ))
    
    insights.append(Insight(
        type="good",
        text=f"Average order value is {_format_currency(avg_order_value)} across {total_orders:,} orders."
    ))
    
    if anomaly_day:
        insights.append(Insight(
            type="warn",
            text=f"Anomaly detected: {anomaly_label}"
        ))
    
    if len(product_revenues) > 1:
        bottom_product = product_revenues[-1]
        bottom_pct = (bottom_product["revenue"] / total_revenue * 100) if total_revenue > 0 else 0
        if bottom_pct < 10:
            insights.append(Insight(
                type="warn",
                text=f"\"{bottom_product['name']}\" contributes only {bottom_pct:.1f}% of revenue — consider reviewing its positioning."
            ))
    
    # ── Recommendations ────────────────────────────────────────────────────
    recs: List[Recommendation] = []
    
    recs.append(Recommendation(
        icon="bullseye",
        text=f"Increase marketing budget for \"{top_product}\" — it drives {top_product_pct:.0f}% of your revenue with the highest ROI."
    ))
    
    if worst_region and worst_region_drop_pct > 15:
        recs.append(Recommendation(
            icon="magnifying-glass",
            text=f"Investigate \"{worst_region['name']}\" region — assign a dedicated rep or run a targeted campaign to close the {worst_region_drop_pct:.0f}% performance gap."
        ))
    
    if growth_rate < -10:
        recs.append(Recommendation(
            icon="chart-line",
            text="Revenue is declining — consider running promotions or discounts to re-engage customers and reverse the trend."
        ))
    else:
        recs.append(Recommendation(
            icon="boxes-stacked",
            text=f"Maintain inventory levels for \"{top_product}\" — demand trend suggests continued strong performance."
        ))
    
    if len(product_revenues) > 1:
        recs.append(Recommendation(
            icon="user-tie",
            text=f"Bundle \"{top_product}\" with lower-performing products to lift overall average order value."
        ))
    
    # ── Summary sentence ────────────────────────────────────────────────────
    summary = f"Analysis of {total_orders:,} orders totalling {_format_currency(total_revenue)}. {'Growing' if growth_rate >= 0 else 'Declining'} at {abs(growth_rate):.1f}% with \"{top_product}\" leading."
    
    # ── Build chart data ────────────────────────────────────────────────────
    chart_data = Charts(
        salesOverTime=ChartData(labels=week_labels, data=week_data),
        revenueByProduct=ChartData(
            labels=[p["name"] for p in product_revenues],
            data=[p["revenue"] for p in product_revenues]
        ),
        revenueByRegion=ChartData(
            labels=[r["name"] for r in region_revenues],
            data=[r["revenue"] for r in region_revenues]
        )
    )
    
    return AnalysisResult(
        kpis=KPIs(
            totalRevenue=total_revenue,
            totalOrders=total_orders,
            growthRate=growth_rate,
            avgOrderValue=avg_order_value,
            topProduct=top_product,
            topRegion=top_region
        ),
        charts=chart_data,
        insights=insights,
        recommendations=recs,
        forecast=Forecast(
            nextWeek=next_week_forecast,
            nextMonth=next_month_forecast,
            growthTrend=growth_trend,
            anomaly=anomaly_label
        ),
        summary=summary
    )
