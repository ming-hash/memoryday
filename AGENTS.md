# MemoryDay (今日吃啥) — 微信小程序菜谱管理

## Project Overview

WeChat Mini Program for personal recipe management. Three deployment modes: `local-dev`, `local`, `cloudbase` — auto-detected on startup (`app.js:initDeploymentConfig`). Default env is always development (`config/env.js:isDevelopment`).

## Architecture

- **Frontend**: Native WeChat Mini Program (WXML+WXSS+JS). Pages defined in `app.json` — 3 tabBar pages (index/menu, statistics, user) + 6 sub-pages (dish-detail, dish-edit, login, settings, deployment, webview).
- **Backend**: Django **4.2.7** REST Framework in `backend/`. Apps: `users`, `dishes`, `tags`, `stats`, `upload`, `cos`. JWT via `djangorestframework-simplejwt`. Docs at `/swagger/` and `/redoc/`.
  - URL structure: `/api/auth/`, `/api/dishes/`, `/api/tags/`, `/api/stats/`, `/api/upload/`, `/api/cos/`
  - Settings: `settings/base.py` → `settings/development.py` (default in `manage.py`) or `settings/production.py`
  - Dev: SQLite (`db.sqlite3`). Production: MySQL via docker-compose (`docker-compose.yml`).
  - ⚠️ Dead code: `memoryday_backend/settings.py` (old monolithic) still exists alongside `memoryday_backend/settings/` package. Only the `settings/` package is used.
- **CloudBase Cloud Functions**: `cloudfunctions/getOpenId` (returns `{openid, appid, unionid}`), `cloudfunctions/memoryday-api` (action-based CRUD proxy with hardcoded data, no DB).
- **CloudBase CloudRun**: `memoryday-backend/` (Node.js, SSE, WebSocket, OpenAI integration). Separate deploy wrapper at `cloudrun/memoryday-backend/` (Dockerfile + cloudbaserc.json).
- **Storage**: Tencent Cloud COS, bucket `memoryday-{suffix}`, region `ap-beijing`. Frontend SDK at `config/cos.js`, service at `services/cosService.js`. Backend COS app at `apps/cos/`.

## Key Commands

```bash
# Backend
cd backend && python manage.py runserver

# Backend deps
pip install -r requirements.txt && pip install -r requirements-cos.txt

# Frontend COS setup
npm run setup-cos    # install cos-wx-sdk-v5
npm run test-cos     # verify COS config

# Lint/Format (no eslintrc/prettierrc found — uses defaults)
npm run lint         # eslint --ext .js
npm run format       # prettier **/*.{js,json,wxml,wxss}

# Build (both are no-ops — compile/upload in WeChat DevTools)
npm run dev          # "请在微信开发者工具中编译"
npm run build        # "请在微信开发者工具中上传"

# Test (no-op placeholder)
npm test             # "暂无测试框架"
```

## API Routing

`app.js:request()` dispatches by `deploymentMode`:
- `cloudbase`: `wx.cloud.callFunction` → `memoryday-api` with `{action, data}`
- `local*`: `wx.request` at `this.globalData.baseUrl` (Django backend)

CloudBase API uses `cloudfunctions/memoryday-api/index.js` with action dispatch (`getDishes`, `getRandomDish`, `getDishDetail`). Local API uses Django REST endpoints under `/api/`.

## Directory Naming Warning

Two distinct backend directories:
- `backend/` — **Django** (Python) REST API. The main backend.
- `memoryday-backend/` — **CloudBase CloudRun** (Node.js) for SSE, WebSocket, OpenAI.

## Important Conventions

- **Dual API mode**: Frontend supports both local Django API and CloudBase cloud functions. Always check `deploymentMode` in `globalData` before adding API calls.
- **Deployment auto-detection**: `utils/deployment.js` probes all modes (priority: local-dev > local > cloudbase), picks the best available, persists to wx storage.
- **Event bus**: `utils/event.js` — `eventBus` + `Events` constants used for cross-component communication.
- **Performance monitoring**: `utils/performance.js` tracks API request timing and page load metrics.
- **COS bucket**: `memoryday-1259810697` in `ap-beijing`. Uses signed URLs for private bucket access.
- **No test framework**. Don't rely on `npm test`.

## CloudBase MCP

Configured in `.opencode.json` — uses `@cloudbase/cloudbase-mcp` for CloudBase operations (deploy functions, manage auth, query database).

## Duplicate Rule Files

The same CloudBase rules template is duplicated across many AI config dirs (`.claude/`, `.cursor/`, `.github/`, `.gemini/`, `.augment-guidelines`, `.rules/`, `.clinerules/`, `.roo/`, `.windsurf/`, etc.) — all derivatives of the CLAUDE.md template. Only `AGENTS.md` is authoritative for OpenCode.
