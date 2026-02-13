# 🚀 Quick Start: Nova AI Service V2 Features

This guide covers all the powerful features developed for the **Nova AI Service V2**.

## 🔌 Service URL
Base URL: `http://localhost:8000` (or `http://localhost:8002` if running for Java integration)

---

## 1. 📊 Advanced Analysis (V2 Engine)

### **Deterministic Scoring**
Run a 100% deterministic market analysis of a startup idea.
- **Endpoint**: `POST /api/v2/score-idea`
- **Use Case**: Get an objective MVS (Market Validation Score) without LLM hallucinations.

### **Strategic Audit Agent**
Ask qualitative questions about a specific score.
- **Endpoint**: `POST /api/v2/explain-score`
- **Questions**: "Why is my market score low?", "What is the TAM?", "Give me a VC perspective."

---

## 2. 🔍 Market Research

### **Smart Comparison Search**
Find 5 real-world startups similar to an idea and their outcomes (acquired, failed, growing).
- **Endpoint**: `POST /api/v2/comparison/find-similar`
- **Requires**: `PRODUCTHUNT_API_TOKEN` in `.env`

### **Universal Validation**
Multi-sector validation using 6 free APIs (Trends, Youtube, Reddit, etc.).
- **Endpoint**: `POST /api/v2/validation/validate`

---

## 3. 🎨 Asset Generation

### **Lean Canvas**
Generate a full Lean Canvas in JSON and a beautiful HTML view.
- **Endpoint**: `POST /api/v2/assets/lean-canvas`

### **Pitch Deck Outline**
Generate a 5-slide pitch deck structure.
- **Endpoint**: `POST /api/v2/assets/pitch-deck`

### **Landing Page**
Generate a high-conversion HTML landing page.
- **Endpoint**: `POST /api/v2/assets/landing-page`

---

## 🧪 4. Business Verification Tools

### **Unit Economics**
Calculate LTV/CAC and profitability thresholds.
- **Endpoint**: `POST /api/v2/verification/economics`

### **Tech Feasibility**
Assess TRL (Technology Readiness Level) and engineering risks.
- **Endpoint**: `POST /api/v2/verification/feasibility`

### **Traffic Estimator**
Estimate potential ad traffic and costs using search trends.
- **Endpoint**: `POST /api/v2/verification/traffic`

---

## 🛠️ Testing Everything
Run the comprehensive integration test suite to verify all endpoints are operational:

```bash
cd ai-service
python run_integration_tests.py
```

### **Manual Health Check**
`GET /health` -> `{"status":"healthy","version":"2.0.0"}`
