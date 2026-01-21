#!/bin/bash
set -e

# ============================================
# DevContainer Post-Create Initialization Script
# Runs after container is created
# ============================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ReconPoint DevContainer Post-Create Setup                ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# 1. Environment Setup
# ============================================
echo -e "\n${BLUE}[1/7]${NC} Setting up environment variables..."
cd /workspaces/reconpoint

# Create .env.local for development if not exists
if [ ! -f .env.local ]; then
    echo -e "${YELLOW}Creating .env.local...${NC}"
    cat > .env.local << 'EOF'
# Development overrides - local machine specific
# These values override .env for local development

DEBUG=true
TEMPLATE_DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1,*.local

# Local database connections
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=reconpoint_dev
POSTGRES_USER=reconpoint
POSTGRES_PASSWORD=dev_password_change_me

# Redis
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Security (disabled for development)
SECURE_SSL_REDIRECT=false
SESSION_COOKIE_SECURE=false
CSRF_COOKIE_SECURE=false

# Email backend (use console for dev)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Django superuser credentials (for auto-creation)
DJANGO_SUPERUSER_USERNAME=reconpoint
DJANGO_SUPERUSER_EMAIL=reconpoint@example.com
DJANGO_SUPERUSER_PASSWORD=reconpoint
EOF
    echo -e "${GREEN}✓ .env.local created${NC}"
else
    echo -e "${GREEN}✓ .env.local already exists${NC}"
fi

# ============================================
# 2. Pre-commit Hooks
# ============================================
echo -e "\n${BLUE}[2/7]${NC} Installing pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠ Pre-commit not found, installing...${NC}"
    pip install pre-commit
    pre-commit install
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
fi

# ============================================
# 3. Django Extensions
# ============================================
echo -e "\n${BLUE}[3/7]${NC} Installing Django extensions and utilities..."
pip install --quiet \
    django-extensions \
    django-debug-toolbar \
    ipython \
    ipdb

echo -e "${GREEN}✓ Django extensions installed${NC}"

# ============================================
# 4. IDE/Editor Configuration
# ============================================
echo -e "\n${BLUE}[4/7]${NC} Configuring IDE/Editor..."

# Create .vscode/settings.json if not exists
if [ ! -f .vscode/settings.json ]; then
    mkdir -p .vscode
    cat > .vscode/settings.json << 'EOF'
{
  "python.defaultInterpreterPath": "/usr/local/bin/python",
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": [
    "--max-line-length=88",
    "--extend-ignore=E203,W503"
  ],
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=88"],
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "django.pythonPath": "/usr/local/bin/python",
  "django.projectPath": "web",
  "editor.rulers": [88],
  "editor.wordWrap": "on",
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true
}
EOF
    echo -e "${GREEN}✓ VS Code settings created${NC}"
else
    echo -e "${GREEN}✓ VS Code settings already exist${NC}"
fi

# ============================================
# 5. Database & Static Files
# ============================================
echo -e "\n${BLUE}[5/7]${NC} Setting up database and static files..."

cd /workspaces/reconpoint/web

# Run migrations
echo -e "${YELLOW}Running migrations...${NC}"
python manage.py migrate --noinput || true

# Create superuser if it doesn't exist
echo -e "${YELLOW}Creating superuser...${NC}"
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='reconpoint').exists():
    User.objects.create_superuser('reconpoint', 'reconpoint@example.com', 'reconpoint')
    print("✓ Superuser 'reconpoint' created")
else:
    print("✓ Superuser already exists")
PYEOF

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput || true

echo -e "${GREEN}✓ Database and static files configured${NC}"

# ============================================
# 6. Code Quality Tools
# ============================================
echo -e "\n${BLUE}[6/7]${NC} Installing code quality tools..."
pip install --quiet \
    black \
    isort \
    flake8 \
    flake8-bugbear \
    mypy \
    pytest \
    pytest-django \
    pytest-cov \
    pytest-xdist \
    coverage

echo -e "${GREEN}✓ Code quality tools installed${NC}"

# ============================================
# 7. Summary & Next Steps
# ============================================
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ DevContainer Setup Complete!                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}Quick Start Guide:${NC}"
echo ""
echo -e "  ${GREEN}Development Server:${NC}"
echo "    python manage.py runserver 0.0.0.0:8000"
echo "    → Open http://localhost:8000"
echo ""
echo -e "  ${GREEN}Django Shell:${NC}"
echo "    python manage.py shell_plus"
echo ""
echo -e "  ${GREEN}Run Tests:${NC}"
echo "    pytest                    # All tests with coverage"
echo "    pytest web/tests/         # Specific test directory"
echo "    pytest -v -k test_name    # Single test by name"
echo "    pytest --pdb              # Stop on failures for debugging"
echo ""
echo -e "  ${GREEN}Code Formatting:${NC}"
echo "    black web/                # Format Python code"
echo "    isort web/                # Sort imports"
echo "    flake8 web/               # Lint code"
echo ""
echo -e "  ${GREEN}Debugging:${NC}"
echo "    • Use VS Code debug configurations (Run > Start Debugging)"
echo "    • Set breakpoints by clicking line numbers"
echo "    • Use pdb: import pdb; pdb.set_trace()"
echo ""
echo -e "  ${GREEN}Database:${NC}"
echo "    • PostgreSQL: localhost:5432"
echo "    • Neo4j Browser: http://localhost:7474"
echo "    • Redis Commander: redis:6379 (use redis-cli)"
echo ""
echo -e "  ${GREEN}Pre-commit Hooks:${NC}"
echo "    • Already installed and will run on git commit"
echo "    • Run manually: pre-commit run --all-files"
echo ""
echo -e "  ${GREEN}Useful Extensions:${NC}"
echo "    • Search Extensions and install: Python, Django, Docker, SQLTools"
echo ""

echo -e "\n${YELLOW}Default Credentials:${NC}"
echo "  Admin User: reconpoint"
echo "  Password: reconpoint"
echo "  URL: http://localhost:8000"
echo ""

echo -e "${BLUE}Troubleshooting:${NC}"
echo "  • Database not connecting? Ensure containers are running: docker ps"
echo "  • Migrations failing? Run: python manage.py migrate --fake-initial"
echo "  • Static files missing? Run: python manage.py collectstatic --noinput"
echo "  • Port conflicts? Change ports in docker-compose.devcontainer.yml"
echo ""

echo -e "${GREEN}Happy coding! 🚀${NC}\n"
