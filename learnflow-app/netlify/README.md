# Netlify Functions

Serverless backend functions:

- **functions/** - API endpoints
  - user-service.py
  - product-service.py
  - order-service.py
  - chat-service.py

Deploy with:
```bash
netlify deploy --prod
```

Configuration: netlify.toml
Environment: Set in Netlify dashboard

Each function wraps FastAPI app with Mangum.
