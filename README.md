# Sales Analysis AI - Project Documentation

## 📋 Quick Start

### Backend (Python Flask)
```bash
cd artifacts/api-server-python
pip install -r requirements.txt
python src/index.py
```
Server runs on `http://localhost:3001`

### Frontend (React + Vite)
```bash
cd artifacts/sales-ai
npm install
npm run dev
```
Frontend runs on `http://localhost:5173`

---

## 🏗️ Project Structure

```
Sales-Analysis-AI/
├── artifacts/
│   ├── api-server-python/       # Python/Flask backend
│   │   ├── src/
│   │   │   ├── app.py           # Flask app factory
│   │   │   ├── routes.py        # API endpoints
│   │   │   ├── analyzer.py      # Analysis engine (optimized)
│   │   │   ├── logger.py        # Logging setup
│   │   │   ├── index.py         # Entry point (dev)
│   │   ├── wsgi.py              # Production entry point
│   │   ├── requirements.txt     # Dependencies
│   │   └── README.md
│   │
│   ├── sales-ai/                # React frontend
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── pages/
│   │   │   ├── components/      # shadcn/ui components
│   │   │   ├── hooks/
│   │   ├── vite.config.ts       # Vite + API proxy
│   │   ├── package.json
│   │   └── index.html
│   │
│   └── mockup-sandbox/          # UI component sandbox
│
├── package.json                 # Workspace root config
├── pnpm-workspace.yaml          # Simplified workspace
├── tsconfig.json
├── MIGRATION_GUIDE.md
└── README.md
```

---

## 🚀 Features

### Backend
✅ CSV upload & validation  
✅ Real-time data analysis  
✅ KPI calculation  
✅ Chart data generation  
✅ Anomaly detection  
✅ Revenue forecasting  
✅ Automated insights & recommendations  
✅ CORS enabled  
✅ Production-ready (Gunicorn support)  

### Frontend
✅ File upload interface  
✅ Real-time dashboard  
✅ Interactive charts (Recharts)  
✅ API integration  
✅ Responsive design  

---

## 📊 API Endpoints

### Health Check
```
GET /api/healthz
Response: { "status": "ok" }
```

### Analyze CSV
```
POST /api/analyze
Content-Type: multipart/form-data

file: <CSV file>

Response: {
  "success": true,
  "data": {
    "kpis": { ... },
    "charts": { ... },
    "insights": [ ... ],
    "recommendations": [ ... ],
    "forecast": { ... },
    "summary": "..."
  },
  "warnings": [ ... ],
  "rowCount": number
}
```

---

## 📈 Performance Optimizations

### Backend (Python)
- **Time Complexity**: O(n log n) due to sorting
- **Space Complexity**: O(n) for data storage
- **Optimizations**:
  - Early parsing validation
  - Single-pass data grouping
  - Constant-time forecasting
  - Efficient helper functions
  - Type hints for better performance

### Frontend (React)
- **Tree-shaking enabled**: Only used code bundled
- **Code splitting**: Vite automatic chunk splitting
- **Lazy loading**: React.lazy for pages
- **API caching**: React Query with 5min stale time
- **Optimize dependencies**: Removed unused libraries

### Project-wide
- **Removed unused packages**: db, api-zod, integrations, etc.
- **Consolidated workspace**: Only active packages
- **Removed artifacts**: Old mockups, Replit files
- **Cleaned config**: Removed unnecessary npm config

---

## 🔧 Development

### Python Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run dev server (auto-reload)
python src/index.py

# Production deployment
gunicorn -w 4 -b 0.0.0.0:3001 wsgi:app
```

### React Frontend Development
```bash
# Install dependencies  
npm install

# Development server (hot reload)
npm run dev

# Build for production
npm run build

# Preview build
npm run preview
```

---

## 📝 CSV Format

**Required columns** (case-insensitive):
- `date` - Date in YYYY-MM-DD format
- `product` - Product name
- `revenue` - Revenue amount (numbers only)
- `quantity` - Order quantity
- `region` - Geographic region

**Example**:
```csv
date,product,revenue,quantity,region
2024-01-03,ProMax Suite,1820,12,North
2024-01-05,Starter Plan,640,8,South
2024-01-07,Enterprise,3200,4,East
```

**Requirements**:
- Minimum 5 rows
- Valid dates
- Numeric revenue/quantity

---

## 🔐 Environment Variables

```bash
# Backend
PORT=3001                    # Server port
NODE_ENV=development         # development or production
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR

# Frontend
VITE_API_URL=http://localhost:3001
```

---

## 📦 Dependencies

### Backend
- Flask 3.0.0
- Flask-CORS 4.0.0
- python-multipart 0.0.6
- python-dateutil 2.8.2
- gunicorn 21.2.0 (production)

### Frontend
- React 18.2.0
- Vite 7.3.0
- Recharts 2.10.3
- React Query 5.28.0
- TailwindCSS 3.3.6
- shadcn/ui components

---

## 🧪 Testing CSV Upload

1. **Using sample data**:
   ```
   Download from http://localhost:3001/sample.csv
   ```

2. **Create your own**:
   - Use the CSV format above
   - Minimum 5 rows
   - Valid data

3. **Via API**:
   ```bash
   curl -X POST http://localhost:3001/api/analyze \
     -F "file=@data.csv"
   ```

---

## 🚨 Troubleshooting

### Backend won't start
- Check Python 3.8+ is installed
- Verify port 3001 is available
- Check `requirements.txt` is installed

### Frontend can't reach API
- Verify backend is running on port 3001
- Check browser console for CORS errors
- Verify API proxy in `vite.config.ts`

### CSV upload fails
- Check required columns: date, product, revenue, quantity, region
- Verify minimum 5 rows
- Check date format (YYYY-MM-DD)
- Ensure numeric data has no currency symbols

---

## 📚 Architecture

```
┌─────────────────────┐
│ React Frontend      │
│ (Vite + TailwindCSS)│
└────────┬────────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────┐
│ Flask API Server            │
│ - /api/healthz             │
│ - /api/analyze (POST)       │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Analysis Engine (Python)    │
│ - CSV parsing               │
│ - KPI calculation           │
│ - Chart generation          │
│ - Forecasting              │
│ - Insights                 │
└─────────────────────────────┘
```

---




---

## 📞 Support

For issues or questions:
1. Check the API logs: `console output`
2. Verify CSV format
3. Check browser console for frontend errors
4. Ensure both backend and frontend are running

