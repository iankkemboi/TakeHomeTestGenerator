# Quick Start Guide

Get up and running with the Take-Home Test Generator in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- Google Gemini API key (free tier available)

## Step 1: Get a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

## Step 2: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd TakeHomeTestGenerator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
echo "GEMINI_API_KEY=your_actual_api_key_here" >> .env
```

## Step 4: Run the Server

```bash
# Start the FastAPI server
python -m backend.main

# Or with auto-reload for development
uvicorn backend.main:app --reload
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## Step 5: Test the API

### Option A: Using the Interactive Docs

1. Open your browser to `http://localhost:8000/docs`
2. Click on `POST /api/v1/assignments/generate`
3. Click "Try it out"
4. Use this example request:

```json
{
  "job_title": "Senior Backend Engineer",
  "job_description": "We're building a fintech platform that processes payroll for 10,000+ companies across Europe. As a Senior Backend Engineer, you'll design and build scalable APIs for payroll processing, implement complex tax calculations, and integrate with banking APIs (SEPA). You'll work with Python, FastAPI, PostgreSQL, and Redis. We need someone with 5+ years of backend experience, strong API design skills, and experience with financial systems.",
  "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
  "time_budget_hours": 4.0,
  "seniority_level": "senior",
  "must_evaluate": ["API design", "error handling"]
}
```

5. Click "Execute"
6. Wait 60-90 seconds for generation
7. View the generated assignment in the response

### Option B: Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/assignments/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior Backend Engineer",
    "job_description": "We are building a fintech platform that processes payroll for 10,000+ companies across Europe. As a Senior Backend Engineer, you will design and build scalable APIs for payroll processing, implement complex tax calculations, and integrate with banking APIs (SEPA). You will work with Python, FastAPI, PostgreSQL, and Redis. We need someone with 5+ years of backend experience, strong API design skills, and experience with financial systems.",
    "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
    "time_budget_hours": 4.0,
    "seniority_level": "senior",
    "must_evaluate": ["API design", "error handling"]
  }'
```

### Option C: Using the CLI Script

```bash
python scripts/generate_sample.py
```

This will generate a sample assignment and save it to `sample_assignment.json`.

## Understanding the Response

The API returns a complete assignment with three main components:

### 1. Candidate Brief
What candidates receive:
- Assignment title
- Business context (200-400 words)
- Must-have requirements (3-7 items)
- Nice-to-have requirements
- Submission guidelines
- Evaluation criteria overview
- Time estimate

### 2. Evaluator Guide
What evaluators use:
- Detailed scoring rubric (weights sum to 1.0)
- Seniority-specific expectations
- Common pitfalls to watch for
- Red flags (poor understanding)
- Green flags (strong performance)
- Calibration notes

### 3. Time Breakdown
Detailed time allocation:
- Setup time
- Core implementation time
- Testing time
- Documentation time
- Buffer time

## Next Steps

- **Customize inputs**: Try different job descriptions, seniority levels, and time budgets
- **Validate first**: Use `/api/v1/assignments/validate` to quickly check if inputs will work
- **Review output**: Check `scope_warnings` for potential issues
- **Run tests**: `pytest` to verify everything works

## Common Issues

### "GEMINI_API_KEY must be provided"
Make sure your `.env` file exists and contains `GEMINI_API_KEY=your_key`

### "Job description too short"
Job descriptions must be at least 500 characters. Add more detail about responsibilities and tech stack.

### "Time mismatch" error
The generator couldn't fit requirements into your time budget. Try:
- Increasing time budget
- Reducing `must_evaluate` items
- Using a lower seniority level

### "Rate limit exceeded"
Free tier has 15 requests/minute. Wait a minute and try again, or upgrade your Gemini API tier.

## Development Mode

For development with auto-reload:

```bash
uvicorn backend.main:app --reload --log-level debug
```

This will restart the server whenever you change code.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run only fast unit tests
pytest -m unit
```

## What's Next?

- Read the [API Documentation](http://localhost:8000/docs)
- Check out [example outputs](./examples.md)
- Learn about [customization options](../README.md#api-usage)
- Explore the [architecture](../Productspec.md#system-architecture)

## Need Help?

- Check the [README](../README.md) for detailed documentation
- Review the [Product Spec](../Productspec.md) for architecture details
- Open an issue on GitHub
