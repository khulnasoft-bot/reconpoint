# ReconPoint Production-Ready DevContainer Setup

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (or Docker + Docker Compose)
- Visual Studio Code
- [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension

### Launch DevContainer (2 minutes)

1. **Open project in VS Code:**
   ```bash
   code /workspaces/reconpoint
   ```

2. **Reopen in container:**
   - Press `Cmd+Shift+P` (or `Ctrl+Shift+P` on Linux/Windows)
   - Type "Reopen in Container"
   - Select "ReconPoint Django Dev"

3. **Wait for setup (~2-3 minutes):**
   - Container builds and initializes
   - Dependencies install
   - Database migrations run
   - Superuser created automatically

4. **Access services:**
   - Django: http://localhost:8000
   - Admin: http://localhost:8000/admin (user: `reconpoint` / password: `reconpoint`)
   - Neo4j: http://localhost:7474
   - Flower (Celery): http://localhost:5555
   - Mailhog (Email): http://localhost:8025

---

## 📁 Project Structure

```
.devcontainer/
├── devcontainer.json                 # Main configuration
├── Dockerfile                        # DevContainer image definition
├── docker-compose.devcontainer.yml   # Development services
├── post-create.sh                    # Initialization script
├── initialize.sh                     # Pre-creation setup
├── supervisord.conf                  # Process management (optional)
├── PROJECT_ANALYSIS.md              # Detailed project analysis
├── DX_ENHANCEMENTS.md               # Developer experience guide
└── SECURITY_BEST_PRACTICES.md       # Security guidelines

.vscode/
├── launch.json                       # Debug configurations
└── settings.json                     # Editor settings

Root:
├── pytest.ini                        # Test configuration
├── .coveragerc                       # Coverage configuration
├── .env                              # Environment defaults (tracked)
├── .env.local                        # Development overrides (gitignored)
└── web/
    ├── manage.py                     # Django CLI
    └── conftest.py                   # Pytest fixtures
```

---

## 🔧 Core Components

### 1. DevContainer Configuration
**File:** `.devcontainer/devcontainer.json`

- **Docker Compose:** Combines main + dev-specific services
- **VS Code Extensions:** 20+ pre-configured extensions
- **Port Forwarding:** All services accessible on localhost
- **Mounts:** SSH keys, Git config, Docker socket
- **Environment:** DEBUG=true, etc.

### 2. DevContainer Dockerfile
**File:** `.devcontainer/Dockerfile`

- **Base:** Python 3.10-slim (optimized for dev)
- **System deps:** PostgreSQL, WeasyPrint, Scapy dependencies
- **Python tools:** Black, isort, flake8, mypy, pytest, ipdb, etc.
- **Non-root user:** `app` user for security
- **Layer optimization:** Cached builds, minimal bloat

### 3. Compose Override
**File:** `.devcontainer/docker-compose.devcontainer.yml`

Adds/overrides services for development:
- **Django:** Runs with DEBUG=true, auto-creates superuser
- **Celery:** DEBUG worker with hot reload
- **Celery Beat:** Scheduler for tasks
- **Flower:** Celery monitoring UI
- **Mailhog:** Email testing (captures all emails)
- **Ollama:** Local LLM support

### 4. Initialization Script
**File:** `.devcontainer/post-create.sh`

Automatically runs after container creation:
1. Sets up environment variables
2. Installs pre-commit hooks
3. Creates .env.local if missing
4. Configures VS Code settings
5. Runs migrations
6. Creates superuser
7. Collects static files
8. Displays quick start guide

---

## 🛠️ Common Development Tasks

### Django Development

```bash
# Run development server
python manage.py runserver 0.0.0.0:8000

# Interactive shell
python manage.py shell_plus

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest web/tests/test_nmap.py -v

# Run tests matching pattern
pytest -k "test_model" -v

# Run with coverage report
pytest --cov=web --cov-report=html

# Run in parallel (faster)
pytest -n auto

# Run with debugger on failure
pytest --pdb
```

### Code Quality

```bash
# Format code
black web/
isort web/

# Check formatting
black --check web/

# Lint code
flake8 web/

# Type check
mypy web/api/

# Check imports
isort --check-only web/

# Generate report
flake8 web/ --statistics
```

### Debugging

**VS Code Debugger:**
1. Open Run view (Ctrl+Shift+D)
2. Select configuration (e.g., "Django: Runserver")
3. Press F5 or click play button
4. Set breakpoints by clicking line numbers
5. Inspect variables in Debug Console

**Python Debugger (pdb):**
```python
import pdb; pdb.set_trace()  # Breakpoint
# pdbpp auto-enhances this with colors, syntax highlight, etc.
```

**IPython Debugger:**
```python
from IPython import embed; embed()  # Enhanced interactive debugging
```

### Database Management

```bash
# Connect to PostgreSQL
psql -h db -U reconpoint -d reconpoint

# Backup database
pg_dump -h db -U reconpoint reconpoint > backup.sql

# Restore database
psql -h db -U reconpoint reconpoint < backup.sql

# Run raw SQL in Django shell
python manage.py dbshell
```

### Celery Management

```bash
# Start worker with debug logging
celery -A reconPoint worker -l DEBUG

# Start beat scheduler
celery -A reconPoint beat -l DEBUG --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Monitor with Flower
# Access: http://localhost:5555
```

---

## 🔌 Service URLs & Credentials

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| Django | http://localhost:8000 | - | - |
| Admin | http://localhost:8000/admin | reconpoint | reconpoint |
| Neo4j | http://localhost:7474 | neo4j | password |
| Flower | http://localhost:5555 | - | - |
| Mailhog | http://localhost:8025 | - | - |
| PostgreSQL | localhost:5432 | reconpoint | hE2a5@K&9nEY1fzgA6X |
| Redis | localhost:6379 | - | - |
| Ollama | http://localhost:11434 | - | - |

---

## 📊 Recommended VS Code Extensions

Pre-installed extensions:
- **Python:** ms-python.python
- **Pylance:** ms-python.vscode-pylance
- **Django:** batisteo.vscode-django
- **SQLTools:** mtxr.sqltools + mtxr.sqltools-driver-pg
- **REST Client:** humao.rest-client
- **GitLens:** eamodio.gitlens
- **Docker:** ms-azuretools.vscode-docker
- **SonarLint:** sonarsource.sonarlint-vscode

Additional recommended:
- Copilot (AI assistance)
- Thunder Client (Postman alternative)
- Git Graph (visual git history)

---

## 📚 Documentation Guides

### 1. Project Analysis
**File:** `.devcontainer/PROJECT_ANALYSIS.md`

Comprehensive analysis covering:
- Project structure & architecture
- Django apps and domain boundaries
- Dependency breakdown
- Configuration strategy
- Runtime services & infrastructure
- Testing infrastructure
- Security analysis
- Scalability recommendations
- Django version and upgrade path

### 2. DX Enhancements
**File:** `.devcontainer/DX_ENHANCEMENTS.md`

Developer experience guide including:
- Testing & code quality tools (pytest, coverage, black, isort, flake8, mypy)
- Django-specific tools (Debug Toolbar, Django Extensions, querycount)
- IDE integration & debugging
- Performance profiling (Django Silk, line_profiler, memory_profiler)
- Database tools & SQL
- API development & testing
- Logging & monitoring
- Environment management
- Git workflow optimization
- Quick reference & troubleshooting

### 3. Security Best Practices
**File:** `.devcontainer/SECURITY_BEST_PRACTICES.md`

Security guide covering:
- DevContainer security (non-root user, capabilities, SSH keys)
- Secrets management (env vars, hierarchy, credentials)
- Production parity (headers, database, logging, caching)
- Authentication & authorization (2FA, RBAC, JWT)
- Input validation & sanitization
- API security (authentication, rate limiting, permissions)
- Dependency security (scanning, updates, lock files)
- Celery security
- Monitoring & auditing
- Network security
- Incident response
- Security checklist

---

## ⚙️ Configuration Files

### devcontainer.json
Defines the complete development environment:
```json
{
  "dockerComposeFile": ["docker-compose.yml", "docker-compose.devcontainer.yml"],
  "service": "web",
  "remoteUser": "app",
  "customizations": { "vscode": { "extensions": [...], "settings": {...} } },
  "postCreateCommand": ".devcontainer/post-create.sh",
  "forwardPorts": [8000, 5432, 6379, 7474, 7687, 11434]
}
```

### pytest.ini
Test configuration with:
- Django settings module
- Test markers (unit, integration, api, celery, etc.)
- Coverage reporting
- Timeout handling
- Fixtures in conftest.py

### .coveragerc
Coverage exclusions and reporting settings

### launch.json
VS Code debug configurations:
- Django runserver
- Django shell
- Django tests
- Pytest (all tests, current file)
- Celery worker & beat
- Full stack (all services)

---

## 🔐 Environment Variables

### .env (Tracked - Public Defaults)
```bash
DEBUG=false
POSTGRES_DB=reconpoint
POSTGRES_USER=reconpoint
POSTGRES_PASSWORD=hE2a5@K&9nEY1fzgA6X
POSTGRES_HOST=db
POSTGRES_PORT=5432
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0
```

### .env.local (Gitignored - Development Overrides)
```bash
DEBUG=true
TEMPLATE_DEBUG=true
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
SECURE_SSL_REDIRECT=false
SESSION_COOKIE_SECURE=false
CSRF_COOKIE_SECURE=false
POSTGRES_PASSWORD=dev_password_change_me
```

**Why .env.local?**
- Development-specific overrides
- Never committed to git
- Machine-specific secrets
- Per-developer configuration

---

## 🐛 Troubleshooting

### Issue: Container fails to start
```bash
# Check Docker daemon
docker ps

# View container logs
docker-compose logs web

# Rebuild container
docker-compose build --no-cache web

# Full reset
docker-compose down -v
docker-compose up
```

### Issue: Database connection refused
```bash
# Ensure db container is running
docker-compose ps db

# Check PostgreSQL logs
docker-compose logs db

# Verify network
docker network ls
docker network inspect reconpoint_network
```

### Issue: Static files 404
```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify location
ls -la web/staticfiles/
```

### Issue: Tests fail with "no module named django"
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/workspaces/reconpoint/web:$PYTHONPATH

# Run from web directory
cd web && pytest
```

### Issue: Celery tasks not executing
```bash
# Verify Redis connection
redis-cli -h redis ping  # Should print: PONG

# Check Celery worker
celery -A reconPoint worker -l DEBUG

# Verify task configuration
python manage.py celery inspect active
```

### Issue: Debugger not stopping at breakpoints
```bash
# Ensure Debug=true
echo $DEBUG  # Should be 'true'

# Restart VS Code debugger
# F5 > Stop > F5

# Check breakpoint is set (red dot on line number)
```

---

## 📈 Performance Optimization

### Database Queries
```python
# Use select_related for ForeignKey
Scan.objects.select_related('user').all()

# Use prefetch_related for ManyToMany/reverse FK
Target.objects.prefetch_related('scans').all()

# Use only() to fetch specific fields
Scan.objects.only('id', 'name', 'created_at').all()
```

### Caching
```python
from django.core.cache import cache

# Cache expensive queries
def get_dashboard_stats():
    cached = cache.get('dashboard_stats')
    if cached:
        return cached
    
    stats = expensive_query()
    cache.set('dashboard_stats', stats, 3600)  # 1 hour
    return stats
```

### Celery Task Optimization
```python
# Set task time limits
@shared_task(time_limit=3600, soft_time_limit=3300)
def long_running_task():
    pass

# Use task batching
group([long_task.s(i) for i in range(100)]).apply_async()
```

---

## 🚢 Deployment Preparation

### Pre-deployment Checklist

```bash
# 1. Run all tests
pytest

# 2. Check code quality
black --check web/
isort --check-only web/
flake8 web/
mypy web/

# 3. Run security scan
bandit -r web/
safety check requirements.txt

# 4. Verify migrations
python manage.py makemigrations --check

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Check deployment settings
python manage.py check --deploy
```

### Environment Variables for Production
```bash
DEBUG=false
ALLOWED_HOSTS=example.com,api.example.com
SECRET_KEY=$(openssl rand -base64 50)
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
DATABASE_URL=postgresql://user:pass@prod-db:5432/db
REDIS_URL=rediss://user:pass@prod-redis:6380/1
```

---

## 📝 Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/my-feature

# Start container
# VS Code: Reopen in Container

# Make changes
# Tests run automatically via pre-commit

# Commit (pre-commit hooks run)
git add .
git commit -m "feat: my feature"  # Follows conventional commits

# Push and create PR
git push -u origin feature/my-feature
```

### 2. Testing
```bash
# Test single file
pytest web/tests/test_nmap.py -v

# Test by marker
pytest -m api -v

# Generate coverage
pytest --cov=web --cov-report=html

# Open report
open htmlcov/index.html
```

### 3. Code Review
```bash
# Check code style
black --check web/
isort --check-only web/
flake8 web/

# Type check
mypy web/

# Security scan
bandit -r web/
```

---

## 🤝 Contributing

### Before Submitting PR
1. Run full test suite: `pytest`
2. Check code quality: `black web/` && `flake8 web/`
3. Verify migrations: `python manage.py makemigrations --check`
4. Update documentation if needed
5. Add tests for new features (target 80%+ coverage)

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

Examples:
```
feat(api): add scan results endpoint
fix(auth): resolve JWT token expiration
docs(setup): update devcontainer guide
test(models): add comprehensive scan tests
```

---

## 📞 Support & Resources

### Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [VS Code DevContainers](https://code.visualstudio.com/docs/devcontainers/containers)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [isort Import Sorter](https://pycqa.github.io/isort/)
- [Flake8 Linter](https://flake8.pycqa.org/)
- [mypy Type Checker](https://www.mypy-lang.org/)

### Project-Specific
- See `.devcontainer/PROJECT_ANALYSIS.md` for architecture details
- See `.devcontainer/DX_ENHANCEMENTS.md` for tools & extensions
- See `.devcontainer/SECURITY_BEST_PRACTICES.md` for security guidelines

---

## 🎓 Learning Resources

### Django Best Practices
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Django for Beginners](https://djangoforbeginners.com/)
- [Full Stack Python - Django](https://www.fullstackpython.com/django.html)

### Testing
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)
- [pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

### DevOps/Deployment
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Django](https://kubernetes.io/)
- [DevOps Handbook](https://itrevolution.com/the-devops-handbook/)

---

## ✅ Checklist for Getting Started

- [ ] Clone/open repository
- [ ] Open in VS Code
- [ ] Install Remote Containers extension
- [ ] Reopen in container
- [ ] Wait for initialization
- [ ] Verify services running: `docker-compose ps`
- [ ] Access Django: http://localhost:8000
- [ ] Login to admin: http://localhost:8000/admin
- [ ] Run first test: `pytest web/tests/ -v`
- [ ] Format code: `black web/`
- [ ] Set breakpoint and debug: F5
- [ ] Read documentation guides
- [ ] Happy coding! 🚀

---

**Happy coding! If you have questions or issues, refer to the troubleshooting section or check the detailed documentation guides in `.devcontainer/`**

