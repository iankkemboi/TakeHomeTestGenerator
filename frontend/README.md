# Take-Home Test Generator - Frontend

React + TypeScript frontend for the Take-Home Test Generator.

## Features

- **Multi-step Input Form**: Clean wizard-style form for entering assignment parameters
- **Real-time Validation**: Validates inputs before submission
- **Loading States**: Shows progress during AI generation (60-90 seconds)
- **Tabbed Output Display**:
  - Candidate Brief
  - Evaluator Guide with scoring rubric
  - Time Breakdown visualization
- **Markdown Export**: Download assignments as .md files
- **Responsive Design**: Works on desktop and mobile

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Radix UI (tabs, dialogs)
- React Markdown
- Axios

## Getting Started

### Prerequisites

- Node.js 18+ or Bun
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install
# or
bun install
```

### Development

```bash
# Start dev server
npm run dev
# or
bun run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
# or
bun run build
```

### Preview Production Build

```bash
npm run preview
# or
bun run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts          # API client with axios
│   ├── components/
│   │   ├── InputForm.tsx      # Multi-step input form
│   │   ├── OutputDisplay.tsx  # Tabbed output with markdown
│   │   └── LoadingState.tsx   # Loading indicator
│   ├── types/
│   │   └── assignment.ts      # TypeScript interfaces
│   ├── App.tsx                # Main app component
│   ├── main.tsx               # Entry point
│   └── index.css              # Tailwind styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Components

### InputForm

3-step wizard for collecting assignment parameters:
1. **Job Details**: Title, description, tech stack
2. **Assignment Details**: Time budget, seniority, evaluation criteria
3. **Optional Context**: Company context, challenges, submission format

Features:
- Tag-based input for tech stack and evaluation criteria
- Real-time validation
- Step navigation with progress indicator

### OutputDisplay

Tabbed display of generated assignment:
- **Candidate Brief Tab**: What candidates see
- **Evaluator Guide Tab**: Scoring rubric, flags, pitfalls
- **Time Breakdown Tab**: Visual time allocation

Features:
- Markdown rendering
- Download as .md file
- Syntax highlighting for code
- Collapsible sections

### LoadingState

Shows progress during generation:
- Animated spinner
- Phase breakdown with time estimates
- Total expected time

## Configuration

Create a `.env` file (optional):

```env
VITE_API_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`.

## Development Tips

### Hot Module Replacement

Vite provides instant HMR. Changes to components will update immediately without full page reload.

### Type Safety

All API types are defined in `src/types/assignment.ts` and match the backend Pydantic models exactly.

### API Integration

The frontend proxies `/api` requests to the backend during development (configured in `vite.config.ts`). This avoids CORS issues.

### Styling

Uses Tailwind CSS with custom utility classes defined in `index.css`. The design system uses:
- Colors: Blue (primary), Green (success), Red (error), Yellow (warning)
- Spacing: Consistent 4px grid
- Typography: System font stack

## Troubleshooting

### "Network Error"

Make sure the backend is running on `http://localhost:8000`:

```bash
cd ../
python -m backend.main
```

### "Request Timeout"

Generation can take up to 90 seconds. The timeout is set to 2 minutes. If it consistently times out, check:
- Backend logs for errors
- Gemini API key is valid
- Network connectivity

### Build Errors

Clear node_modules and reinstall:

```bash
rm -rf node_modules package-lock.json
npm install
```

## Deployment

### Static Hosting

Build and deploy the `dist/` folder to any static hosting:

```bash
npm run build

# Deploy dist/ to:
# - Vercel
# - Netlify
# - Cloudflare Pages
# - AWS S3 + CloudFront
```

### Environment Variables

Set `VITE_API_URL` to your production API URL in your hosting platform.

## Contributing

1. Follow the existing code style
2. Use TypeScript for type safety
3. Keep components focused and reusable
4. Add error handling for API calls
5. Test on different screen sizes

## License

MIT
