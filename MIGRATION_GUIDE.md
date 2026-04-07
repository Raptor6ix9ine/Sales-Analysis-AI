# Migration Guide: TypeScript to Python Backend

## Overview

The Sales Analysis AI project now has a Python-based backend alternative to the original TypeScript/Node.js implementation. Both backends provide identical functionality - you can switch between them seamlessly.

## Directory Structure

```
artifacts/
├── api-server/                 # Original TypeScript/Express backend
│   ├── src/
│   ├── package.json
│   ├── tsconfig.json
│   └── README.md
│
├── api-server-python/          # New Python/Flask backend
│   ├── src/
│   │   ├── app.py             # Flask application factory
│   │   ├── routes.py          # API route handlers
│   │   ├── analyzer.py        # Sales analysis logic
│   │   ├── logger.py          # Logging configuration
│   │   └── index.py           # Entry point
│   ├── requirements.txt        # Python dependencies
│   ├── README.md
│   └── .gitignore
│
└── [other workspaces...]
```

## Quick Start with Python Backend

### 1. Install Dependencies

```bash
cd artifacts/api-server-python
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python src/index.py
```

Server will run on `http://localhost:3001` (same port as TypeScript version)

### 3. Environment Variables

Both backends support the same environment variables:

```bash
PORT=3001              # Server port (default: 3001)
NODE_ENV=development   # Environment (development or production)
LOG_LEVEL=INFO        # Logging level
```

## API Compatibility

The Python backend is **100% API-compatible** with the TypeScript backend:

### Health Check
```
GET /api/healthz
Response: { "status": "ok" }
```

### Analyze CSV
```
POST /api/analyze
Content-Type: multipart/form-data

file: sample.csv
```

**Response**: Identical to TypeScript version - same JSON structure with:
- `success`: boolean
- `data`: Analysis results (KPIs, charts, insights, recommendations, forecast)
- `warnings`: Array of parsing warnings
- `rowCount`: Number of valid rows processed

## Updating Frontend Configuration

If your frontend is pointing to a specific backend, update the API endpoint:

### Example Frontend Configuration

**TypeScript Backend:**
```typescript
const API_BASE_URL = 'http://localhost:3001';
```

**Python Backend:**
```typescript
const API_BASE_URL = 'http://localhost:3001';  // Same URL!
```

Since both run on the same port with the same API paths, **no frontend changes are required**.

## Comparison

| Feature | TypeScript | Python |
|---------|-----------|--------|
| Framework | Express.js | Flask |
| Port | 3001 | 3001 |
| CSV Parsing | csv-parse | csv module |
| HTTP Server | Native | werkzeug |
| Logging | Pino | Python logging |
| API Routes | `/api/healthz`, `/api/analyze` | `/api/healthz`, `/api/analyze` |
| Analysis Logic | ~300 lines | ~400 lines |
| Dependencies | ~10 npm packages | 4 pip packages |
| Development | `npm run dev` | `python src/index.py` |

## Functional Parity

The Python backend includes **all features** of the TypeScript version:

✅ CSV file upload and validation  
✅ Data parsing with error handling  
✅ KPI calculation (revenue, orders, growth, AOV)  
✅ Chart data generation (time series, by product, by region)  
✅ Anomaly detection  
✅ Revenue forecasting (next week, next month)  
✅ Growth trend analysis  
✅ Automated insights (good/warn/info)  
✅ Business recommendations  
✅ Comprehensive logging  
✅ CORS middleware support  
✅ Static file serving  

## Development Workflow

### Running TypeScript Backend
```bash
cd artifacts/api-server
npm install
npm run dev
```

### Running Python Backend
```bash
cd artifacts/api-server-python
pip install -r requirements.txt
python src/index.py
```

### Testing Both

You can run both simultaneously on different ports:

**TypeScript on 3001:**
```bash
cd artifacts/api-server
npm run dev  # PORT=3001
```

**Python on 3002:**
```bash
cd artifacts/api-server-python
PORT=3002 python src/index.py
```

## Performance Considerations

- **Python/Flask**: Simpler, more Pythonic, easier to extend with ML libraries
- **TypeScript/Express**: Faster startup, native TypeScript support
- Both should handle the same workload adequately

## Troubleshooting

### Python Backend Won't Start

1. Ensure Python 3.8+ is installed:
   ```bash
   python --version
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. Check port availability:
   ```bash
   netstat -ano | findstr :3001  # Windows
   lsof -i :3001                  # macOS/Linux
   ```

### CSV Upload Fails

Both backends require these columns (case-insensitive):
- date
- product
- revenue
- quantity
- region

## Next Steps

- Choose your preferred backend
- Update any deployment configurations
- Test with your CSV data
- Deploy to your environment

## Notes

- Both backends serve the `sample.csv` file from `artifacts/sales-ai/public/`
- Analysis output is identical between implementations
- The Python backend automatically handles edge cases (empty files, invalid data, etc.)
- Logging is environment-aware (colored in development, plain in production)
