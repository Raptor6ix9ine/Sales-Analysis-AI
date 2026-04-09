import csv
import io
import os
import sys
from pathlib import Path
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer import validate_columns, parse_rows, analyze
from src.logger import logger

api_bp = Blueprint('api', __name__)


@api_bp.route('/healthz', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


@api_bp.route('/analyze', methods=['POST'])
def analyze_endpoint():
    """Main analysis endpoint"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                "error": "No file uploaded. Please attach a CSV file."
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "error": "No file selected. Please choose a CSV file."
            }), 400
        
        # Validate file extension
        filename = secure_filename(file.filename)
        if not filename or not filename.lower().endswith('.csv'):
            return jsonify({
                "error": "Invalid file type. Please upload a .csv file."
            }), 400
        
        # Read file content
        file_content = file.read().decode('utf-8')
        
        if not file_content.strip():
            return jsonify({
                "error": "The uploaded file is empty."
            }), 400
        
        # Parse CSV
        try:
            csv_reader = csv.DictReader(io.StringIO(file_content), skipinitialspace=True)
            raw_rows = list(csv_reader)
        except Exception as e:
            logger.error(f"CSV parsing error: {e}")
            return jsonify({
                "error": "Failed to parse CSV file. Please check the format."
            }), 400
        
        if not raw_rows:
            return jsonify({
                "error": "The CSV file has no data rows."
            }), 400
        
        # Validate columns
        headers = list(raw_rows[0].keys()) if raw_rows else []
        missing_cols = validate_columns(headers)
        
        if missing_cols:
            return jsonify({
                "error": f"Invalid file format. Missing required columns: {', '.join(missing_cols)}.",
                "hint": "Required columns: date, product, revenue, quantity, region",
                "missingColumns": missing_cols
            }), 400
        
        # Parse and clean rows
        rows, warnings = parse_rows(raw_rows)
        
        if not rows:
            return jsonify({
                "error": "No valid data rows found after cleaning. Check your file for invalid dates or numbers.",
                "warnings": warnings
            }), 400
        
        if len(rows) < 5:
            return jsonify({
                "error": f"Dataset too small — only {len(rows)} valid row(s) found. Please upload at least 5 rows for meaningful analysis.",
                "warnings": warnings
            }), 400
        
        # Run full analysis
        result = analyze(rows)
        
        # Convert result to dictionary for JSON serialization
        result_dict = {
            "success": True,
            "data": {
                "kpis": {
                    "totalRevenue": result.kpis.totalRevenue,
                    "totalOrders": result.kpis.totalOrders,
                    "growthRate": result.kpis.growthRate,
                    "avgOrderValue": result.kpis.avgOrderValue,
                    "topProduct": result.kpis.topProduct,
                    "topRegion": result.kpis.topRegion,
                },
                "charts": {
                    "salesOverTime": {
                        "labels": result.charts.salesOverTime.labels,
                        "data": result.charts.salesOverTime.data,
                    },
                    "revenueByProduct": {
                        "labels": result.charts.revenueByProduct.labels,
                        "data": result.charts.revenueByProduct.data,
                    },
                    "revenueByRegion": {
                        "labels": result.charts.revenueByRegion.labels,
                        "data": result.charts.revenueByRegion.data,
                    },
                },
                "insights": [
                    {
                        "type": insight.type,
                        "text": insight.text,
                    }
                    for insight in result.insights
                ],
                "recommendations": [
                    {
                        "icon": rec.icon,
                        "text": rec.text,
                    }
                    for rec in result.recommendations
                ],
                "forecast": {
                    "nextWeek": result.forecast.nextWeek,
                    "nextMonth": result.forecast.nextMonth,
                    "growthTrend": result.forecast.growthTrend,
                    "anomaly": result.forecast.anomaly,
                },
                "summary": result.summary,
            },
            "warnings": warnings,
            "rowCount": len(rows),
        }
        
        return jsonify(result_dict)
    
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({
            "error": "Something went wrong during analysis. Please try again."
        }), 500


@api_bp.route('/chat', methods=['POST'])
def chat_endpoint():
    """AI chat endpoint — answers questions about the current analysis"""
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON body received."}), 400

        message = (data.get('message') or '').strip()
        if not message:
            return jsonify({"error": "Message is required."}), 400

        context = data.get('context', {})
        kpis = context.get('kpis', {})
        summary = context.get('summary', '')
        insights = context.get('insights', [])
        recommendations = context.get('recommendations', [])
        forecast = context.get('forecast', {})

        # Build a rich system prompt from analysis context
        insight_text = '\n'.join(f"- {i.get('text', '')}" for i in insights[:5])
        rec_text = '\n'.join(f"- {r.get('text', '')}" for r in recommendations[:4])

        system_prompt = f"""You are a sharp, concise sales data analyst AI embedded inside a dashboard.
The user has uploaded a CSV. Here is the full analysis:

KPIs:
- Total Revenue: ${kpis.get('totalRevenue', 0):,.0f}
- Total Orders: {kpis.get('totalOrders', 0)}
- Growth Rate: {kpis.get('growthRate', 0):.1f}%
- Avg Order Value: ${kpis.get('avgOrderValue', 0):,.0f}
- Top Product: {kpis.get('topProduct', 'N/A')}
- Top Region: {kpis.get('topRegion', 'N/A')}

Summary: {summary}

Insights:
{insight_text}

Recommendations:
{rec_text}

Forecast:
- Next Week: ${forecast.get('nextWeek', 0):,.0f}
- Next Month: ${forecast.get('nextMonth', 0):,.0f}
- Trend: {forecast.get('growthTrend', '')}
- Anomaly: {forecast.get('anomaly', 'None')}

Answer the user's question using only this data. Be specific, cite numbers, and keep responses under 3 sentences."""

        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return jsonify({"error": "Groq API key not configured."}), 500

        from openai import OpenAI
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=200,
            temperature=0.4,
        )

        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return jsonify({"error": "Chat failed. Please try again."}), 500
