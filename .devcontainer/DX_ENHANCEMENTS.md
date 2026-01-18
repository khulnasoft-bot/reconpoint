# Developer Experience (DX) Enhancement Guide

## Overview

This guide provides optional but highly recommended tools and configurations to enhance your development experience with ReconPoint. These enhancements complement the production-ready DevContainer setup.

---

## 1. Testing & Code Quality

### 1.1 Pytest Configuration ✅ Done

The `pytest.ini` file is pre-configured with:
- **Markers** for organizing tests by type (unit, integration, api, celery, etc.)
- **Coverage reporting** (terminal, HTML, XML)
- **Test discovery** patterns
- **Timeout handling** to prevent hanging tests
- **Django integration** via pytest-django

**Usage:**
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest web/tests/test_nmap.py -v

# Run tests matching a pattern
pytest -k test_model -v

# Run with debugger on failure
pytest --pdb

# Parallel execution (faster)
pytest -n auto

# Generate coverage report
pytest --cov=web --cov-report=html
```

### 1.2 Coverage Configuration ✅ Done

`.coveragerc` provides:
- Excluded paths (migrations, tests, venv)
- Detailed reports (terminal, HTML, XML)
- Line-by-line exclusion rules

**Workflow:**
```bash
# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in browser

# View coverage in terminal
coverage report --show-missing

# Check coverage threshold
coverage report --fail-under=80
```

### 1.3 Code Quality Tools

#### Black (Code Formatter) ✅ Configured
```bash
# Format all Python code
black web/

# Format specific file
black web/api/views.py

# Check formatting without changes
black --check web/
```

#### isort (Import Sorter) ✅ Configured
```bash
# Sort imports
isort web/

# Check without changes
isort --check-only web/
```

#### Flake8 (Linter) ✅ Configured
```bash
# Lint code
flake8 web/

# Generate report
flake8 web/ --statistics
```

#### mypy (Type Checker) ✅ Configured
```bash
# Type check code
mypy web/api/

# Generate report
mypy web/ --html-report ./mypy-report
```

### 1.4 Pre-commit Hooks ✅ Installed

Pre-commit automatically runs code quality checks before commits:
```bash
# Run manually on all files
pre-commit run --all-files

# Skip pre-commit on specific commit
git commit --no-verify

# Update hook versions
pre-commit autoupdate
```

**Current hooks:**
- Trailing whitespace check
- End-of-file fixer
- YAML validation
- Large file detection
- Black formatting
- isort import sorting
- Flake8 linting

---

## 2. Django-Specific Enhancements

### 2.1 Django Debug Toolbar ✅ Installed

The Debug Toolbar is included for development. Enable it:

**Step 1:** Add to `settings.py` (development override):
```python
# reconPoint/settings.py (development only)
if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
```

**Step 2:** Add to `urls.py`:
```python
# reconPoint/urls.py
if DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

**Benefits:**
- SQL query inspection and optimization
- Template rendering analysis
- HTTP headers inspection
- Cache statistics
- Performance profiling

### 2.2 Django Extensions ✅ Installed

Enhanced management commands:

```bash
# Shell Plus (enhanced Django shell)
python manage.py shell_plus --ipython

# Generate model graph
python manage.py graph_models -a -o models.png

# Show URLs
python manage.py show_urls

# Find templates
python manage.py find_templates
```

### 2.3 django-querycount

Monitor database queries:
```python
# In settings.py (development)
if DEBUG:
    MIDDLEWARE = ['querycount.middleware.QueryCountDebugMiddleware'] + MIDDLEWARE
```

Prints query count and execution time for each request.

---

## 3. IDE Integration

### 3.1 VS Code Extensions (Auto-installed) ✅

The following extensions are pre-configured in `devcontainer.json`:

**Python Development:**
- ms-python.python - Python support
- ms-python.vscode-pylance - Type checking
- ms-python.debugpy - Debugging
- ms-python.black-formatter - Black integration
- ms-python.flake8 - Flake8 integration

**Django:**
- batisteo.vscode-django - Django support

**Database:**
- mtxr.sqltools - SQL tools
- mtxr.sqltools-driver-pg - PostgreSQL driver
- cweijan.dbg-for-mysql - Database browser

**API Testing:**
- humao.rest-client - REST Client
- thunder-client.thunder-client - Thunder Client

**Git:**
- eamodio.gitlens - GitLens
- mhutchie.git-graph - Git Graph

**Code Quality:**
- sonarsource.sonarlint-vscode - SonarLint
- gruntfuggly.todo-tree - TODO Tree
- charliermarsh.ruff - Ruff Linter

### 3.2 Debugging Configuration ✅ Done

Launch configurations available in `.vscode/launch.json`:

**Via VS Code UI:**
1. Open the Run view (Ctrl+Shift+D)
2. Select a configuration:
   - "Django: Runserver" - Start dev server with debugger
   - "Django: Shell Plus" - Interactive shell
   - "Django: Tests" - Run Django tests
   - "Pytest: All Tests" - Run all pytest tests
   - "Pytest: Current File" - Test current file
   - "Celery: Worker" - Debug Celery worker
   - "Celery: Beat" - Debug scheduler
   - "Full Stack" - Run all services together

**Setting Breakpoints:**
1. Click on line number in code editor
2. Run debugger (F5)
3. Debugger will pause at breakpoint

**Console Debugging:**
```bash
# Python debugger (pdb)
import pdb; pdb.set_trace()

# IPython debugger (enhanced)
from IPython import embed; embed()

# Better debugger (pdbpp)
import pdb; pdb.set_trace()  # Auto-enhanced by pdbpp
```

---

## 4. Performance Profiling

### 4.1 Django Silk

Real-time request/response profiling:

```python
# settings.py (development)
INSTALLED_APPS += ['silk']
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
```

```python
# urls.py
urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
```

Access at: http://localhost:8000/silk/

**Features:**
- Request/response timeline
- SQL query analysis
- Profiling reports
- Request replay

### 4.2 Line Profiler

Profile specific functions:

```python
from line_profiler import LineProfiler

@profile  # Decorate function to profile
def expensive_operation():
    pass

# Run with kernprof
# kernprof -l -v script.py
```

### 4.3 Memory Profiler

Track memory usage:

```python
from memory_profiler import profile

@profile
def memory_intensive():
    pass

# Run with memory_profiler
# python -m memory_profiler script.py
```

---

## 5. Database Tools

### 5.1 SQLTools Integration (VS Code)

**Setup:**
1. Open VS Code
2. Click SQLTools icon in sidebar
3. Add connection (already pre-configured)
4. Click to connect

**Features:**
- SQL editor with autocomplete
- Run queries
- View table data
- Generate reports

### 5.2 PostgreSQL Commands

```bash
# Connect to database
psql -h db -U reconpoint -d reconpoint

# Useful queries
\dt              # List tables
\d table_name    # Describe table
\df              # List functions
\dx              # List extensions

# Backup database
pg_dump -h db -U reconpoint reconpoint > backup.sql

# Restore database
psql -h db -U reconpoint reconpoint < backup.sql
```

### 5.3 Neo4j Browser

Access at: http://localhost:7474

**Default credentials:**
- Username: neo4j
- Password: password

**Query examples:**
```cypher
# View all nodes
MATCH (n) RETURN n LIMIT 25

# Find relationships
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50

# Create test node
CREATE (n:TestNode {name: "Test"}) RETURN n
```

---

## 6. API Development Tools

### 6.1 REST Client Extension

Create `.http` files for API testing:

```http
### Get dashboard data
GET http://localhost:8000/api/dashboard/
Authorization: Bearer YOUR_TOKEN

### Create scan
POST http://localhost:8000/api/scan/
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "target": "example.com",
  "engine": "subfinder"
}

### Get results
GET http://localhost:8000/api/results/1/
Authorization: Bearer YOUR_TOKEN
```

Run: Right-click → "Send Request"

### 6.2 Thunder Client

Alternative REST client with UI:
1. Open Thunder Client (sidebar icon)
2. Create request
3. Configure URL, method, headers
4. Send and inspect response

### 6.3 Generate API Documentation

Using drf-spectacular (configured):

```bash
# Generate OpenAPI schema
python manage.py spectacular --file schema.yml

# View Swagger UI
http://localhost:8000/api/schema/swagger-ui/

# View ReDoc
http://localhost:8000/api/schema/redoc/
```

---

## 7. Logging & Monitoring

### 7.1 Enhanced Logging Setup

Current `settings.py` includes comprehensive logging. Enhancements:

```python
# Add request logging
LOGGING['loggers']['django.request'] = {
    'handlers': ['console', 'file'],
    'level': 'INFO',
}

# Add custom app logging
LOGGING['loggers']['reconPoint.custom'] = {
    'handlers': ['console'],
    'level': 'DEBUG' if DEBUG else 'INFO',
}
```

**Usage:**
```python
import logging
logger = logging.getLogger('reconPoint.custom')
logger.info("Custom message")
```

### 7.2 Structured Logging (Optional)

Install and configure structlog:

```bash
pip install structlog python-json-logger
```

```python
import structlog
logger = structlog.get_logger()
logger.info("event", request_id=123, user_id=456)
```

---

## 8. Environment Management

### 8.1 .env.local Pattern ✅ Configured

Development-specific overrides in `.env.local`:
- Never committed to git
- Overrides values in `.env`
- Machine-specific credentials

**Key variables for development:**
```bash
DEBUG=true
TEMPLATE_DEBUG=true
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
SECURE_SSL_REDIRECT=false
SESSION_COOKIE_SECURE=false
```

### 8.2 Environment Validation

Add to `settings.py`:
```python
import sys

# Validate required env vars
required_env_vars = [
    'POSTGRES_DB',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
]

missing = [var for var in required_env_vars if var not in os.environ]
if missing and not DEBUG:
    raise ValueError(f"Missing required env vars: {missing}")
```

---

## 9. Git Workflow Optimization

### 9.1 GitLens Features

**Command Palette:**
- Search commits (Cmd+Shift+P → "GitLens: Search Commits")
- View file history
- Blame annotations
- Repository explorer

### 9.2 Conventional Commits

Configure pre-commit to enforce conventional commits:

```bash
pip install commitizen
cz commit  # Interactive commit builder
```

### 9.3 Git Aliases

```bash
git config --global alias.co checkout
git config --global alias.st status
git config --global alias.unstage 'restore --staged'
git config --global alias.last 'log -1 HEAD'
```

---

## 10. Documentation

### 10.1 Generate API Docs

```bash
# Swagger/OpenAPI
python manage.py spectacular --file schema.yml

# ReDoc (alternative UI)
# Access at /api/schema/redoc/
```

### 10.2 Code Documentation

Generate with Sphinx (optional):

```bash
pip install sphinx sphinx-rtd-theme
sphinx-quickstart docs/
```

---

## 11. Performance Optimization

### 11.1 Query Optimization Workflow

```python
# Identify N+1 queries
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    # Your code here
    pass

print(f"Queries: {len(context)}")
for query in context:
    print(query['sql'])
```

### 11.2 Cache Strategy

```python
from django.core.cache import cache

# Cache a value
cache.set('key', value, timeout=3600)

# Get with default
result = cache.get('key', default=None)

# Invalidate
cache.delete('key')
```

### 11.3 Database Connection Pooling

Already configured in `settings.py`:
```python
'CONN_MAX_AGE': 60,  # Reuse connections for 60 seconds
'OPTIONS': {
    'keepalives': 1,
    'keepalives_idle': 30,
}
```

---

## 12. Quick Reference

| Task | Command |
|------|---------|
| Start dev server | `python manage.py runserver` |
| Interactive shell | `python manage.py shell_plus` |
| Run all tests | `pytest` |
| Format code | `black web/ && isort web/` |
| Lint code | `flake8 web/` |
| Type check | `mypy web/` |
| Database shell | `psql -h db -U reconpoint reconpoint` |
| Create migration | `python manage.py makemigrations` |
| Run migrations | `python manage.py migrate` |
| Collect static files | `python manage.py collectstatic` |
| Test coverage | `pytest --cov=web` |
| Celery worker | `celery -A reconPoint worker` |
| Celery beat | `celery -A reconPoint beat` |

---

## 13. Troubleshooting

### Issue: Tests fail with "no module named django"
**Solution:** Ensure PYTHONPATH includes web directory
```bash
export PYTHONPATH=/workspaces/reconpoint/web:$PYTHONPATH
pytest
```

### Issue: Static files 404
**Solution:** Collect static files
```bash
python manage.py collectstatic --noinput
```

### Issue: Database connection refused
**Solution:** Check containers are running
```bash
docker-compose ps
docker-compose logs db
```

### Issue: Celery tasks not executing
**Solution:** Check Redis connection and worker logs
```bash
redis-cli -h redis ping
# Should print: PONG

celery -A reconPoint worker -l DEBUG
```

### Issue: Debugger not stopping at breakpoints
**Solution:** Ensure Debug mode is enabled
```bash
# In settings.py or .env
DEBUG=true

# Restart dev server with debugger
# Use VS Code Run > Start Debugging
```

---

## Next Steps

1. ✅ **Install DevContainer** - Use Remote Containers extension
2. ✅ **Run first test** - Execute `pytest --co` to list tests
3. ✅ **Check code quality** - Run `black --check web/`
4. ✅ **Debug first issue** - Set breakpoint and use debugger
5. **Optimize performance** - Use Django Debug Toolbar
6. **Contribute** - Push changes with pre-commit checks

---

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [VS Code Python](https://code.visualstudio.com/docs/languages/python)
- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Pre-commit Hooks](https://pre-commit.com/)

