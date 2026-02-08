# Fatima Zehra Boutique - Project Constitution

**Project**: Fatima Zehra Boutique - Cloud-Native E-Commerce Platform
**Date**: 2026-01-26
**Status**: Foundation Phase
**Target Deployment**: GitHub Pages (Frontend) + Netlify Functions (Backend) + Neon PostgreSQL (Database)

---

## Project Vision

Build a **world-class, full-stack e-commerce platform** for Fatima Zehra Boutique with elegant design, AI-powered chat assistance, and seamless cloud deployment.

### Core Values
1. **User-Centric**: Beautiful, responsive UI that works on all devices
2. **Performance**: < 3s page load time, optimal Core Web Vitals
3. **Reliability**: 99.9% uptime, graceful error handling
4. **Security**: JWT authentication, secure password storage, CORS enforcement
5. **Scalability**: Serverless architecture, cloud-native design
6. **Branding**: "Fatima Zehra Boutique" elegance throughout

---

## Technical Standards

### Frontend Development (Next.js 16 + Tailwind CSS)

**Language**: TypeScript (`.tsx` files)

**Code Quality**:
- ESLint configuration enforced
- Prettier auto-formatting (80-char lines)
- Type safety: No `any` types, strict mode enabled
- Component organization: One component per file in `components/`
- Naming: `PascalCase` for components, `camelCase` for variables

**Performance Targets**:
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Cumulative Layout Shift (CLS): < 0.1
- Time to Interactive (TTI): < 3s
- Bundle size: < 150KB gzipped (initially)

**Testing**:
- Unit tests: Jest + React Testing Library
- Minimum 70% code coverage for components
- Test file naming: `*.test.tsx`
- Acceptance criteria: All critical user flows tested

**Styling**:
- Tailwind CSS utility classes (no CSS files unless necessary)
- Design tokens: `colors.pink-600`, `colors.purple-600`, `colors.amber-500`
- Fonts: Playfair Display (headings, serif), Inter (body, sans-serif)
- Responsive breakpoints: Mobile-first (sm, md, lg, xl, 2xl)
- Dark mode: Optional (use `dark:` classes)

**Security**:
- No hardcoded API keys or secrets
- Sanitize user input before rendering
- CSRF tokens for forms
- CSP headers configured
- Environment variables: `.env.local` (never committed)

**Accessibility**:
- WCAG 2.1 AA compliance
- Semantic HTML (button, nav, main, section)
- ARIA labels where needed
- Keyboard navigation supported
- Color contrast > 4.5:1

### Backend Development (FastAPI + SQLModel)

**Language**: Python 3.11+

**Code Quality**:
- Type hints on all functions: `def register(user: UserCreate) -> UserResponse:`
- Docstrings: Google style for public APIs
- Naming: `snake_case` for functions/variables, `PascalCase` for classes
- No print statements (use logging)
- Max function length: 50 lines (refactor if longer)

**API Design**:
- RESTful conventions: `GET /api/resource`, `POST /api/resource`, `DELETE /api/resource/:id`
- Response format: Always JSON with consistent structure:
  ```json
  {"success": true, "data": {...}, "error": null}
  {"success": false, "data": null, "error": "reason"}
  ```
- HTTP Status Codes:
  - 200: Success
  - 201: Created
  - 400: Bad Request
  - 401: Unauthorized (auth failed)
  - 403: Forbidden (auth OK, permission denied)
  - 404: Not Found
  - 500: Server Error
- Rate limiting: 100 requests/minute per IP (implement in middleware)
- Timeouts: 10s max (Netlify Functions limit)

**Database (Neon PostgreSQL)**:
- ORM: SQLModel (SQLAlchemy + Pydantic)
- Connection pooling: min=5, max=10
- Migrations: Alembic
- Naming: `snake_case` for tables and columns
- Primary keys: `id SERIAL PRIMARY KEY` on all tables
- Timestamps: `created_at`, `updated_at` on all tables
- Indexes: On frequently queried columns (email, category_id, featured)

**Authentication**:
- Method: JWT (JSON Web Tokens)
- Storage: Bearer tokens in Authorization header
- Secret: 32+ character random string (from env var)
- Expiration: 24 hours
- Password hashing: bcrypt with 12 salt rounds
- Routes: Public endpoints (register, products), protected endpoints (/me, cart, orders)

**Testing**:
- Framework: pytest
- Minimum coverage: 80%
- Test file location: `tests/` directory
- Fixtures: Reusable test data
- Mocking: External APIs (OpenAI) mocked in tests
- Naming: `test_*.py` files, `test_*()` functions

**Error Handling**:
- Custom exception classes: `UserNotFound`, `InvalidPassword`, `ProductOutOfStock`
- All endpoints return proper error responses (never 500 unless critical)
- Logging: All errors logged with context (user_id, request_id)
- Graceful degradation: Chat fails → show message, not crash

**Dependencies**:
```
fastapi==0.104.1
sqlmodel==0.0.14
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
bcrypt==4.1.0
python-jose[cryptography]==3.3.0
openai==1.3.0
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.25.0
mangum==0.17.0  # For Netlify Functions
```

### Database (Neon PostgreSQL)

**Connection**:
- Connection string format: `postgresql://user:pass@host:port/dbname`
- Pooling: Neon's built-in connection pooling (min 5, max 10)
- Retry logic: 3 retries with exponential backoff (500ms, 1s, 2s)
- Timeout: 5 seconds per query

**Schema Standards**:
- Table naming: `plural_snake_case` (users, products, orders)
- Column naming: `snake_case`
- Data types:
  - Text: `VARCHAR(255)` for strings with known max length, `TEXT` for unbounded
  - Numbers: `INTEGER` or `DECIMAL(10, 2)` for prices
  - Dates: `TIMESTAMP DEFAULT NOW()` for creation times
  - Boolean: `BOOLEAN DEFAULT FALSE`
- All tables have: `id SERIAL PRIMARY KEY`, `created_at TIMESTAMP`, `updated_at TIMESTAMP`

**Indexes**:
- Foreign keys automatically indexed
- Email fields indexed (lookups)
- Search fields indexed (product name, category)
- Featured products indexed (filtering)
- Session IDs indexed (chat history)

**Data Retention**:
- Active records: Keep indefinitely
- Deleted records: Soft delete (add `deleted_at` column) for 90 days
- Chat history: Keep for 1 year, then archive
- Backups: Daily automated (Neon default)

### Deployment (GitHub Pages + Netlify + Neon)

**Frontend Deployment** (GitHub Pages):
- Build: `next build && next export`
- Output: `./out/` directory
- Branch: Push to `gh-pages` branch
- URL: `https://[username].github.io/fatima-zehra-boutique/`
- CDN: GitHub's CDN (automatic)
- SSL: Automatic HTTPS

**Backend Deployment** (Netlify Functions):
- Build: `netlify deploy --prod`
- Functions: `netlify/functions/*.py` (Mangum wrapped)
- URL: `https://[site-name].netlify.app/.netlify/functions/[service-name]`
- Cold start: Accept 1-2s on first call
- Timeout: 10 seconds (hard limit)
- Scaling: Automatic (no config needed)

**Database Deployment** (Neon PostgreSQL):
- Tier: Free tier (512MB) for development, upgrade as needed
- Region: US-East (default)
- Backups: Daily automated
- Connection string: Stored in Netlify environment variables
- URL format: `postgresql://[user]:[pass]@[host]/[dbname]`

**Environment Variables**:
- Frontend (`.env.local`):
  ```
  NEXT_PUBLIC_API_URL=https://[site-name].netlify.app/.netlify/functions
  NEXT_PUBLIC_SITE_NAME=Fatima Zehra Boutique
  ```
- Backend (Netlify UI):
  ```
  NEON_DATABASE_URL=postgresql://...
  JWT_SECRET=your-secret-key
  OPENAI_API_KEY=sk-...
  CORS_ORIGINS=https://[username].github.io
  ```

### Architecture Patterns

**Microservices**:
- 3 independent services: user-service, product-service, order-service
- Each service has own database tables (no cross-service queries)
- Services communicate via HTTPS API calls only
- No shared state between services

**Authentication Flow**:
1. User registers/logs in (user-service)
2. Service returns JWT token
3. Frontend stores token in localStorage
4. Subsequent requests include `Authorization: Bearer <token>`
5. Protected endpoints verify token, extract user_id

**Error Handling**:
- Frontend: Show user-friendly error messages
- Backend: Log all errors with context (request_id, user_id)
- Never expose internal errors to frontend
- Graceful degradation (feature fails, not entire app)

**Caching**:
- Frontend: Service Workers for offline support
- Backend: Redis caching (optional, Phase 2)
- Database: Connection pooling (Neon handles this)

---

## Branding Guidelines

### "Fatima Zehra Boutique" Identity

**Color Palette**:
- Primary: Pink (`#EC4899`, Tailwind `pink-600`)
- Secondary: Purple (`#9333EA`, Tailwind `purple-600`)
- Accent: Amber/Gold (`#F59E0B`, Tailwind `amber-500`)
- Neutral: Gray (`#6B7280`, Tailwind `gray-500`)
- Background: White (`#FFFFFF`) or off-white (`#F9FAFB`)

**Typography**:
- Headings (h1-h3): Playfair Display, serif (elegant)
- Body text: Inter, sans-serif (modern, readable)
- Logo: "Fatima Zehra Boutique" in Playfair Display

**Visual Elements**:
- Elegant, minimalist design (not cluttered)
- Professional fashion photography
- Consistent spacing (8px grid)
- Subtle shadows and hover effects
- Smooth transitions (200ms)

**Copy Tone**:
- Friendly but professional
- Product descriptions: Highlight elegance and quality
- CTAs: "Discover", "Explore", "Add to Collection"
- Support: Helpful, not robotic

---

## Non-Functional Requirements

### Performance
- Page load: < 3s (LCP)
- API response: < 500ms (p95)
- Database query: < 100ms (p95)
- Chat streaming: Start < 2s
- Image load: Lazy loading with placeholders

### Reliability
- Uptime target: 99.9% (43 minutes downtime/month)
- Error rate: < 0.1% of requests
- Database failover: Automatic (Neon handles)
- Graceful degradation: Chat fails, rest works

### Security
- HTTPS enforced (GitHub Pages + Netlify + Neon)
- Password: Bcrypt hashing, min 8 characters
- JWT: 24-hour expiration, HttpOnly cookies (if possible)
- API: CORS restricted to GitHub Pages domain
- Database: SQL injection prevention (SQLAlchemy ORM)
- Secrets: Never committed (.env files)

### Cost
- Hosting: Free tier (GitHub Pages + Netlify + Neon free tier)
- APIs: OpenAI pay-as-you-go
- Domain: Optional custom domain (no extra cost for GitHub Pages)
- Monthly budget: < $50/month

---

## Definition of Done

### Code Review Checklist
- [ ] Code follows style guide (ESLint/Black)
- [ ] Type hints present and correct
- [ ] Tests written and passing (80%+ coverage)
- [ ] No hardcoded secrets
- [ ] Error handling present
- [ ] API responses consistent
- [ ] Performance targets met
- [ ] Accessibility standards followed
- [ ] Documentation updated

### Feature Acceptance
- [ ] User story acceptance criteria met
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing on desktop + mobile
- [ ] No console errors or warnings
- [ ] No performance regression
- [ ] Merged to main/master branch

### Deployment Readiness
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] CI/CD pipeline passing
- [ ] Staging environment tested
- [ ] Ready for production

---

## Team Standards

### Git Workflow
- Main branch: `main` (protected, requires PR)
- Feature branches: `feature/short-description`
- Commit messages: "feat: ...", "fix: ...", "docs: ...", "refactor: ..."
- PRs: Require 1 approval before merging

### Documentation
- README.md: Project overview + quick start
- API.md: API endpoint documentation
- DEPLOYMENT.md: How to deploy
- Code comments: Only for "why", not "what"

### Communication
- Updates: Recorded in Prompt History Records (PHRs)
- Decisions: Documented in Architecture Decision Records (ADRs)
- Planning: Specs + Plans + Tasks defined upfront

---

## Success Metrics

### User Satisfaction
- No critical bugs reported
- Performance: < 3s load time (LCP)
- Mobile conversion rate: > 30% of desktop
- Chat feature: > 50% of users use it

### Developer Experience
- Onboarding time: < 1 hour
- Local dev setup: `docker-compose up -d` (1 command)
- Deploy time: < 10 minutes
- Test coverage: > 80%

### Business Metrics
- Cart abandonment: < 70%
- Checkout completion: > 30% of cart sessions
- Average order value: Tracked
- Customer retention: Tracked

---

## Additional Resources

- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Tailwind CSS**: https://tailwindcss.com/
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **Neon Docs**: https://neon.tech/docs
- **Netlify Functions**: https://docs.netlify.com/functions/
- **GitHub Pages**: https://pages.github.com/

---

**This constitution ensures all team members understand the project vision, technical standards, and quality expectations.**
