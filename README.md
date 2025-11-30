# Take-Home Test Generator

AI-powered generator that creates realistic, scoped take-home coding assignments with business context, explicit time breakdowns, and standardized evaluation rubrics.

## Problem Statement

Engineering teams waste 468+ hours annually creating inconsistent take-home assignments. Candidates spend 3-4x stated time on poorly scoped tests. Current solutions generate generic challenges that don't reflect actual job requirements or company context.

## Solution

This tool uses Google Gemini AI to generate assignments that:
- Reflect actual job responsibilities, not generic coding challenges
- Respect candidate time with realistic scope
- Provide clear evaluation criteria
- Test for seniority-appropriate skills

## Features

- **4-Phase Generation Pipeline**:
  1. Context extraction from job descriptions
  2. Scope definition with must-have/nice-to-have requirements
  3. Automatic validation of time estimates and quality
  4. Evaluation rubric with seniority-specific expectations

- **Quality Gates**: Ensures assignments meet quality standards
- **Time Breakdown**: Explicit time estimates for setup, implementation, testing, documentation
- **Evaluation Rubrics**: Standardized scoring to reduce evaluator bias
- **Business Context**: Specific, realistic scenarios tied to job responsibilities

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd TakeHomeTestGenerator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running the API

Start the FastAPI server:

```bash
python -m backend.main
```

Or with uvicorn directly:

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
bun install
```

3. Start the development server:
```bash
npm run dev
# or
bun run dev
```

The frontend will be available at `http://localhost:3000`

### Using the Web Interface

1. Make sure the backend is running on `http://localhost:8000`
2. Open `http://localhost:3000` in your browser
3. Fill out the 3-step form:
   - **Step 1**: Job title, description, tech stack
   - **Step 2**: Time budget, seniority level, evaluation criteria
   - **Step 3**: Optional company context and challenges
4. Click "Generate Assignment" and wait 60-90 seconds
5. View the generated assignment in tabs:
   - **Candidate Brief**: What to send to candidates
   - **Evaluator Guide**: Scoring rubric and evaluation criteria
   - **Time Breakdown**: Detailed time allocation
6. Download as Markdown file or generate a new assignment

## API Usage

### Generate Assignment

**POST** `/api/v1/assignments/generate`

```bash
curl -X POST "http://localhost:8000/api/v1/assignments/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior Backend Engineer",
    "job_description": "Build scalable APIs for our fintech platform processing payroll transactions...",
    "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
    "time_budget_hours": 4.0,
    "seniority_level": "senior",
    "must_evaluate": ["API design", "error handling", "testing"],
    "company_context": "Fintech startup processing €50M+ monthly payroll",
    "submission_format": "github"
  }'
```

**Response:**
```json
{
  "candidate_brief": {
    "title": "Payroll Transaction Processing API",
    "business_context": "...",
    "requirements": {
      "must_have": [...],
      "nice_to_have": [...],
      "constraints": [...]
    },
    "submission_guidelines": "...",
    "evaluation_criteria": [...],
    "time_estimate": "4 hours"
  },
  "evaluator_guide": {
    "scoring_rubric": [...],
    "common_pitfalls": [...],
    "red_flags": [...],
    "green_flags": [...],
    "calibration_notes": "..."
  },
  "time_breakdown": {
    "total_minutes": 240,
    "setup_minutes": 20,
    "core_implementation_minutes": 150,
    "testing_minutes": 40,
    "documentation_minutes": 20,
    "buffer_minutes": 10
  },
  "assignment_id": "...",
  "estimated_difficulty": "medium",
  "scope_warnings": [...]
}
```

### Validate Input

**POST** `/api/v1/assignments/validate`

Quick validation without generating full assignment:

```bash
curl -X POST "http://localhost:8000/api/v1/assignments/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Backend Engineer",
    "job_description": "...",
    "tech_stack": ["Python"],
    "time_budget_hours": 3.0,
    "seniority_level": "mid"
  }'
```

### Health Check

**GET** `/health`

```bash
curl http://localhost:8000/health
```

## Project Structure

```
TakeHomeTestGenerator/
├── backend/
│   ├── api/
│   │   ├── routes.py              # FastAPI endpoints
│   │   ├── schemas.py             # Pydantic models
│   │   └── dependencies.py        # Dependency injection
│   ├── core/
│   │   ├── generator.py           # Main generation pipeline
│   │   ├── validator.py           # Scope validation logic
│   │   ├── quality_gates.py       # Quality check implementations
│   │   └── prompts.py             # Prompt templates
│   ├── clients/
│   │   └── gemini_client.py       # Gemini API wrapper
│   ├── utils/
│   │   └── logger.py              # Structured logging setup
│   ├── tests/
│   │   ├── test_generator.py
│   │   └── fixtures/
│   ├── main.py                    # FastAPI app entry point
│   └── config.py                  # Configuration management
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration

Environment variables (`.env`):

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
ENVIRONMENT=development           # development, staging, production
```

## Running Tests

Run all tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=backend --cov-report=html
```

Run specific test file:

```bash
pytest backend/tests/test_generator.py
```

Run only unit tests (fast):

```bash
pytest -m unit
```

## Success Metrics

The generator aims to achieve:
- Assignment completion time matches stated estimate (±30 min, 80% of candidates)
- Evaluator scoring consistency (±10% variance between reviewers)
- Time-to-create reduced from 3 hours to 15 minutes
- Candidate completion rate >70% (vs industry average ~45%)

## Architecture

### 4-Phase Generation Pipeline

1. **Context Extraction** (10-15s)
   - Analyzes job description
   - Identifies responsibilities, business domain, tech stack
   - Validates extracted context

2. **Scope Definition** (15-20s)
   - Generates must-have/nice-to-have requirements
   - Creates realistic business context
   - Defines technical constraints

3. **Validation** (10s)
   - Checks time estimates (±15% tolerance)
   - Validates business context quality
   - Ensures seniority-appropriate complexity

4. **Rubric Generation** (15-20s)
   - Creates evaluation rubric with weights
   - Defines seniority-specific expectations
   - Generates calibration notes

**Total time**: ~60-90 seconds

### Quality Gates

- **Context Validation**: 3+ responsibilities, business domain identified
- **Scope Validation**: Time estimates within ±15% of budget, 200+ char context
- **Rubric Validation**: Weights sum to 1.0, 3-7 evaluation areas
- **Seniority Matching**: Complexity matches target level

## API Cost

Using Gemini Flash 2.5:
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- **Cost per assignment: ~$0.002-0.004**

Significantly cheaper than other AI providers while maintaining quality.

## Error Handling

The API provides structured error responses:

- `400 Bad Request`: Invalid input or scope mismatch
- `503 Service Unavailable`: AI service temporarily down
- `500 Internal Server Error`: Unexpected errors

Example error response:
```json
{
  "error": "scope_mismatch",
  "message": "Time mismatch: requirements sum to 360 minutes but budget is 240 minutes",
  "suggestion": "Try reducing requirements or increasing time budget"
}
```

## Development

### Code Style

Format code with Black:
```bash
black backend/
```

Lint with Ruff:
```bash
ruff check backend/
```

Type check with MyPy:
```bash
mypy backend/
```

### Adding New Features

1. Add schemas to `backend/api/schemas.py`
2. Update generation pipeline in `backend/core/generator.py`
3. Add quality gates in `backend/core/quality_gates.py`
4. Create tests in `backend/tests/`
5. Update API routes in `backend/api/routes.py`

## Roadmap

### MVP (Week 1-3)
- [x] Core generation pipeline
- [x] Quality gates and validation
- [x] FastAPI endpoints
- [ ] Basic frontend (React)
- [ ] Documentation and examples

### Phase 2 (Week 4-5)
- [ ] Template library
- [ ] Assignment refinement workflow
- [ ] Storage (PostgreSQL)

### Phase 3 (Week 6-8)
- [ ] Candidate submission portal
- [ ] Time tracking integration
- [ ] Analytics dashboard

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Create an issue on GitHub
- Check API documentation at `/docs`

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI model
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Structlog](https://www.structlog.org/) - Structured logging
