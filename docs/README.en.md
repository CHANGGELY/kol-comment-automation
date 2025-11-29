<!-- File note: English documentation, detailed architecture, setup and usage for global contributors -->

# KOL Comment Automation (English Docs)

## Purpose
- Human-like comment actions and visual automation across YouTube / Bilibili / Douyin.
- Engineering-first: stability, maintainability, scalability.

## Architecture
- Service layer (`services`): business flows (open video, scroll, locate comment box, input, submit).
- ActionKernel: unified human-like interactions (random pauses, smooth scrolls, progressive typing).
- Vision core (`vision_core`): OCR preprocessing, text recognition, screen capture.
- Captcha solver (`captcha_solver`): detect and solve common captchas (slider, etc.).
- Selector manager (`selector_manager`): versioning and history to adapt platform changes.

## Setup
- Install deps: `pip install -r 评论区引流器/-2/requirements.txt`
- Install browsers: `python -m playwright install`
- Env: configure `评论区引流器/-2/.env` for `ENABLE_HEADLESS`, `PROXY_SERVER`.
- Run example: `python 评论区引流器/-2/e2e/smoke_comment.py`

## Development
- Prioritize readability; use guard clauses; do not swallow exceptions.
- Structured logging and performance metrics; avoid leaking secrets in logs.
- Use `pre-commit` hooks locally before committing.

## Testing & Quality
- Tests: `pytest`, async tests: `pytest-asyncio`.
- Coverage goal: >80%, CI uploads coverage to Codecov.

## FAQ
- OCR init failure: automatic GPU→CPU fallback; ensure drivers and dependencies.
- Selector failure: verification and fallback triggered; check `selectors.json` versions and alternatives.
- Proxy & headless: via `.env`; network quality impacts automation stability.

## Contributing
- Issues/PRs welcome; follow naming conventions and focus on vectorized, simple implementations.
