# DevContainer Quick Reference Card

## 🚀 Start Development (2 steps)

1. **Cmd+Shift+P** → "Reopen in Container"
2. Wait ~3 minutes for setup to complete

## 🌐 Access Services

```
Django:        http://localhost:8000
Admin:         http://localhost:8000/admin (reconpoint/reconpoint)
Neo4j:         http://localhost:7474
Flower:        http://localhost:5555
Mailhog:       http://localhost:8025
```

## 📝 Django Commands

```bash
runserver              python manage.py runserver 0.0.0.0:8000
shell_plus             python manage.py shell_plus --ipython
makemigrations         python manage.py makemigrations
migrate                python manage.py migrate
createsuperuser        python manage.py createsuperuser
collectstatic          python manage.py collectstatic --noinput
test                   python manage.py test
```

## ✅ Testing

```bash
pytest                 # All tests + coverage
pytest file.py         # Specific file
pytest -k test_name    # By pattern
pytest --pdb           # Debugger on fail
pytest -n auto         # Parallel
```

## 🛠️ Code Quality

```bash
black web/             # Format code
isort web/             # Sort imports
flake8 web/            # Lint
mypy web/              # Type check
pre-commit run -a      # All hooks
```

## 🐛 Debugging

**VS Code:**
- Ctrl+Shift+D (Run view)
- Select configuration
- F5 (Start)
- Click line number for breakpoint

**Python:**
```python
import pdb; pdb.set_trace()
from IPython import embed; embed()
```

## 🗄️ Database

```bash
psql -h db -U reconpoint -d reconpoint
pg_dump -h db -U reconpoint reconpoint > backup.sql
psql -h db -U reconpoint reconpoint < backup.sql
```

## 🔄 Celery

```bash
celery -A reconPoint worker -l DEBUG
celery -A reconPoint beat -l DEBUG
# Monitor: http://localhost:5555
```

## 🔧 Hot Reload

- **Django:** Auto-reloads on file change
- **Celery:** Restart with `Ctrl+C` then `celery... worker`
- **Tests:** Auto-discover on file change with pytest-watch

```bash
pip install pytest-watch
ptw
```

## 📂 Key Files

```
.devcontainer/
  README.md                       ← Full guide (START HERE)
  PROJECT_ANALYSIS.md            ← Architecture & structure
  DX_ENHANCEMENTS.md            ← Tools & extensions
  SECURITY_BEST_PRACTICES.md    ← Security guidelines
  devcontainer.json              ← Main config
  Dockerfile                     ← Image definition
  post-create.sh                 ← Auto-setup script

.vscode/
  launch.json                    ← Debug configurations
  settings.json                  ← Editor settings

web/
  conftest.py                    ← Pytest fixtures
  manage.py                      ← Django CLI

pytest.ini                       ← Test config
.coveragerc                      ← Coverage config
.env                            ← Defaults (tracked)
.env.local                      ← Overrides (gitignored)
```

## 🔐 Secrets

```bash
# Tracked (public defaults)
cat .env

# Development overrides (gitignored)
cat .env.local
```

## 🐳 Docker Commands

```bash
docker-compose ps              # List services
docker-compose logs web        # View logs
docker-compose down            # Stop all
docker-compose restart web     # Restart service
docker-compose build --no-cache web  # Rebuild
```

## 📊 Performance

```python
# Query optimization
Scan.objects.select_related('user')
Target.objects.prefetch_related('scans')

# Caching
from django.core.cache import cache
cache.set('key', value, 3600)
```

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Container won't start | `docker-compose down -v && docker-compose up` |
| DB connection fails | `docker-compose logs db` |
| Static files 404 | `python manage.py collectstatic` |
| Tests fail | `export PYTHONPATH=/workspaces/reconpoint/web` |
| Debugger not working | Ensure DEBUG=true, F5 to restart |

## 💡 Pro Tips

- **Right-click file** → Run Tests (Pytest extension)
- **Ctrl+K Ctrl+I** → Show parameter hints
- **F8** → Go to next error
- **Shift+Alt+F** → Format document
- **Ctrl+Shift+P** → Command palette (everything!)
- **Ctrl+;** → Toggle terminal
- **Ctrl+J** → Toggle debug console

## 📚 Documentation

- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- Pytest: https://docs.pytest.org/
- VS Code: https://code.visualstudio.com/docs

## 🎯 Typical Development Session

```bash
# 1. Reopen in container (Cmd+Shift+P)

# 2. Run tests
pytest

# 3. Start dev server (F5 → Django: Runserver)

# 4. Open http://localhost:8000 in browser

# 5. Make changes (auto-reload)

# 6. Set breakpoints and debug (F5)

# 7. Format before commit
black web/ && isort web/ && flake8 web/

# 8. Commit with pre-commit hooks
git commit -m "feat: my feature"
```

## 📞 Need Help?

1. **First time?** → Read `.devcontainer/README.md`
2. **Architecture questions?** → See `PROJECT_ANALYSIS.md`
3. **Tools & extensions?** → Check `DX_ENHANCEMENTS.md`
4. **Security concerns?** → Review `SECURITY_BEST_PRACTICES.md`
5. **Stuck?** → Check Troubleshooting section above

---

**Remember:** Press `Ctrl+Shift+P` to access any command! 🎯
