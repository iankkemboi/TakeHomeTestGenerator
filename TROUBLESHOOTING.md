# Troubleshooting Guide

Common issues and solutions for the Take-Home Test Generator.

## Backend Issues

### 1. "GEMINI_API_KEY must be provided"

**Problem**: The API key is not set in the environment.

**Solution**:
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key
echo "GEMINI_API_KEY=your_actual_key_here" >> .env
```

Get your API key from: https://makersuite.google.com/app/apikey

### 2. "Gemini API call failed"

**Problem**: Issues with the Gemini API.

**Common Causes**:
- Invalid API key
- Rate limit exceeded (free tier: 15 requests/min)
- Network connectivity issues
- API service down

**Solutions**:
```bash
# Test your API key
python -c "import google.generativeai as genai; import os; from dotenv import load_dotenv; load_dotenv(); genai.configure(api_key=os.getenv('GEMINI_API_KEY')); model = genai.GenerativeModel('gemini-1.5-pro-latest'); print(model.generate_content('Hello').text)"

# Check rate limits - wait 1 minute if exceeded
# Verify network: ping google.com
```

### 3. "Job description too short"

**Problem**: Job description must be at least 100 characters.

**Solution**:
Add more details about:
- Role responsibilities
- Technical requirements
- Tech stack details
- Team structure
- Company context

### 4. "Time mismatch" or "Scope validation failed"

**Problem**: The generator couldn't fit requirements into the time budget.

**Solutions**:
- Increase `time_budget_hours` (2.0 to 8.0)
- Reduce items in `must_evaluate`
- Lower `seniority_level`
- Simplify the job description

### 5. "Module not found" errors

**Problem**: Dependencies not installed.

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

## Frontend Issues

### 1. "Network Error" in browser

**Problem**: Frontend can't connect to backend.

**Solutions**:
```bash
# Make sure backend is running
curl http://localhost:8000/health

# If not running, start it:
cd /path/to/TakeHomeTestGenerator
python -m backend.main

# Check CORS settings in backend/config.py
# Default allows: http://localhost:3000
```

### 2. "Request Timeout"

**Problem**: Generation takes longer than 2 minutes.

**Causes**:
- Slow Gemini API response
- Complex job description
- High server load

**Solutions**:
- Wait and retry
- Simplify the job description
- Check Gemini API status
- Increase timeout in `frontend/src/api/client.ts` (line 13)

### 3. Frontend won't start

**Problem**: npm/bun errors.

**Solutions**:
```bash
cd frontend

# Clear and reinstall
rm -rf node_modules package-lock.json
npm install

# Or with bun
rm -rf node_modules
bun install

# Start dev server
npm run dev
```

### 4. "Unexpected token" or TypeScript errors

**Problem**: Build/compile errors.

**Solutions**:
```bash
# Check Node version (need 18+)
node --version

# Update if needed
nvm install 18
nvm use 18

# Clean build
rm -rf node_modules dist
npm install
npm run build
```

## Integration Issues

### 1. CORS errors in browser console

**Problem**: Backend rejecting frontend requests.

**Solution**:

Edit `backend/config.py`:
```python
allowed_origins: list[str] = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:3000",
]
```

Restart backend after changes.

### 2. 500 Internal Server Error

**Problem**: Backend error during generation.

**Debug Steps**:
```bash
# Check backend logs in terminal
# Look for Python tracebacks

# Test API directly
curl -X POST http://localhost:8000/api/v1/assignments/generate \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Test Engineer",
    "job_description": "Build test automation for our platform. You will write unit tests, integration tests, and e2e tests using pytest and Selenium. Must have 3+ years experience with Python testing frameworks.",
    "tech_stack": ["Python", "Pytest"],
    "time_budget_hours": 3.0,
    "seniority_level": "mid",
    "must_evaluate": ["testing"],
    "avoid_topics": []
  }'

# Check response for detailed error
```

### 3. JSON parsing errors

**Problem**: "Failed to parse JSON from Gemini response"

**Cause**: Gemini returned non-JSON or malformed JSON.

**Solutions**:
- Retry the request (prompts include JSON instructions)
- Check backend logs for the actual response
- The retry logic should handle this automatically

## Performance Issues

### 1. Generation takes >90 seconds

**Normal Behavior**: Generation typically takes 60-90 seconds.

**If consistently >90s**:
- Check your internet connection speed
- Verify Gemini API isn't experiencing issues
- Try a simpler job description
- Check CPU usage on your machine

### 2. High memory usage

**Cause**: Large context or many concurrent requests.

**Solutions**:
- Restart backend periodically
- Limit concurrent requests
- Monitor with: `ps aux | grep python`

## Testing Issues

### 1. Pytest import errors

**Problem**: "ModuleNotFoundError: No module named 'backend'"

**Solution**:
```bash
# Run from project root
cd /path/to/TakeHomeTestGenerator

# Activate venv
source venv/bin/activate

# Run tests
pytest

# Or set PYTHONPATH
PYTHONPATH=. pytest
```

### 2. Tests fail with "GEMINI_API_KEY not found"

**Solution**:
```bash
# Load .env in tests
# Already handled in code, but verify .env exists
ls -la .env

# Run with env var explicitly
GEMINI_API_KEY=your_key pytest
```

## Development Issues

### 1. Hot reload not working (backend)

**Solution**:
```bash
# Use uvicorn with reload
uvicorn backend.main:app --reload --log-level debug

# Or use the run script
./run.sh
```

### 2. Changes not reflecting (frontend)

**Solution**:
```bash
# Vite HMR should work automatically
# If not, restart dev server
# Ctrl+C to stop
npm run dev

# Hard refresh browser
# Mac: Cmd+Shift+R
# Windows: Ctrl+Shift+R
```

## API Documentation Issues

### 1. Swagger UI not loading

**Problem**: http://localhost:8000/docs shows blank page.

**Solutions**:
```bash
# Check backend is running
curl http://localhost:8000/

# Try alternative docs
open http://localhost:8000/redoc

# Check browser console for errors
# Disable ad blockers
```

## Getting Help

If you're still stuck:

1. **Check logs**:
   - Backend: Look at terminal running `python -m backend.main`
   - Frontend: Check browser DevTools Console
   - Network: Check browser DevTools Network tab

2. **Enable debug mode**:
   ```bash
   # Backend
   LOG_LEVEL=DEBUG python -m backend.main

   # Frontend - check Network tab in browser
   ```

3. **Minimal reproduction**:
   ```bash
   # Test with minimal input
   python scripts/generate_sample.py
   ```

4. **Check versions**:
   ```bash
   python --version  # Should be 3.11+
   node --version    # Should be 18+
   pip list | grep -E "fastapi|pydantic|google-generativeai"
   ```

5. **Create an issue**:
   - Include error messages
   - Include your Python/Node versions
   - Include steps to reproduce
   - Include backend logs

## Common Error Messages

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| "GEMINI_API_KEY must be provided" | Missing API key | Add to .env |
| "Time mismatch" | Scope too large/small | Adjust time budget |
| "Network Error" | Backend not running | Start backend |
| "Request Timeout" | Generation taking too long | Wait or retry |
| "CORS error" | Wrong origin | Update backend config |
| "Module not found" | Missing dependencies | `pip install -r requirements.txt` |
| "Port already in use" | Port 8000/3000 taken | Kill process or change port |

## Debug Checklist

- [ ] Backend running on :8000
- [ ] Frontend running on :3000
- [ ] .env file exists with GEMINI_API_KEY
- [ ] Virtual environment activated
- [ ] Dependencies installed (pip/npm)
- [ ] API key is valid (test with curl)
- [ ] No firewall blocking localhost
- [ ] Browser DevTools checked
- [ ] Backend logs checked
- [ ] Rate limits not exceeded

---

**Still having issues?** Create a GitHub issue with:
- Error message
- Steps to reproduce
- Environment (OS, Python version, Node version)
- Backend logs
