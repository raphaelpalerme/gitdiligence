# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in GitDiligence, please report it responsibly:

1. **Do NOT open a public issue**
2. Email: raphaelpalerme2@gmail.com
3. Include a description of the vulnerability and steps to reproduce

I will respond within 48 hours and work on a fix.

## Scope

GitDiligence interacts with:
- **GitHub API** — using your personal access token
- **Google Gemini API** / **Anthropic Claude API** — using your API keys

API keys are stored locally in `.env` and never transmitted anywhere except to their respective APIs.
