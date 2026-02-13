# 🔑 API Configuration Guide

## Quick Start

### 1️⃣ Add Your OpenAI API Key

Edit the `.env` file in this directory (`ai-service/.env`):

```env
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

> **Where to get your API key:** https://platform.openai.com/api-keys

### 2️⃣ Restart the Server

The server will auto-reload when you save the `.env` file, OR you can manually restart:

```bash
# The server should already be running with:
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3️⃣ Test the Endpoints

Run the test script:

```bash
python test_api.py
```

## Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/ideas/generate` | POST | Generate startup ideas |
| `/api/v2/verification/economics` | POST | Calculate unit economics |
| `/api/v2/verification/feasibility` | POST | Assess tech feasibility |
| `/api/v2/verification/traffic` | POST | Estimate traffic |
| `/api/v2/assets/landing-page` | POST | Generate landing page |

## Interactive API Docs

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

**Server won't start?**
- Check that port 8000 is not in use
- Verify Python 3.14 is installed
- Run: `pip install -r requirements.txt`

**API calls failing?**
- Verify your OpenAI API key is correct
- Check you have API credits: https://platform.openai.com/usage
- Review server logs for errors
