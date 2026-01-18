# Security & Best Practices Guide for ReconPoint DevContainer

## Executive Summary

This guide covers security considerations specific to the DevContainer setup, production parity, and best practices for maintaining a secure development environment that mirrors production characteristics.

---

## 1. DevContainer Security

### 1.1 Non-Root User Setup ✅

**Current Implementation:**
```dockerfile
# DevContainer/Dockerfile
RUN groupadd -r app && useradd -r -g app app
USER app
```

**Benefits:**
- Prevents accidental system modifications
- Limits damage if process is compromised
- Mirrors production deployment patterns

**Volumes & Permissions:**
```bash
# Correct ownership setup
RUN chown -R app:app /workspaces

# No world-writable directories
```

### 1.2 Capabilities & Security Options

**Current configuration** in `devcontainer.json`:
```json
"runArgs": [
  "--cap-add=NET_ADMIN",
  "--cap-add=NET_RAW"
]
```

**Rationale:**
- `NET_ADMIN`: Required for network reconnaissance tools (nmap, scapy)
- `NET_RAW`: Needed for raw packet manipulation
- NOT running as privileged (preferred over --privileged)

**Production Note:** These capabilities should NOT be in production; use service accounts with specific permissions.

### 1.3 SSH Key Forwarding (Secure)

```json
"mounts": [
  "source=${localEnv:HOME}/.ssh,target=/root/.ssh,readonly"
]
```

**Security Best Practices:**
- ✅ Read-only mount (prevents container from modifying keys)
- ✅ SSH agent forwarding for git operations
- ✅ Keys never copied into image layers
- ✅ Automatic cleanup on container removal

**Usage:**
```bash
# SSH authentication inside container
ssh-add ~/.ssh/id_ed25519  # On host before dev container
git clone git@github.com:user/repo.git  # Inside container
```

### 1.4 Docker Socket Access

```json
"mounts": [
  "source=/var/run/docker.sock,target=/var/run/docker.sock"
]
```

**Security Implications:**
- ⚠️ Enables Docker-in-Docker capability
- Allows running containers from within DevContainer
- **Risk**: Container can escape to host
- **Mitigation**: Only enable if absolutely necessary

**Alternative:** Use Docker Buildkit for isolated builds

---

## 2. Secrets Management

### 2.1 Environment Variables Strategy

**DevContainer Configuration:**
```json
"remoteEnv": {
  "DEBUG": "true",
  "DJANGO_SETTINGS_MODULE": "reconPoint.settings",
  "PYTHONUNBUFFERED": "1"
}
```

**Key Security Points:**
- ✅ DEBUG never true in production
- ✅ Secrets NOT in remoteEnv (use .env.local)
- ✅ Variables accessible to running process only

### 2.2 Secrets Hierarchy

```
┌─ Priority (highest to lowest) ─────────────────┐
│                                                 │
│ 1. .env.local (gitignored, per-machine)        │
│ 2. docker-compose.devcontainer.yml env vars    │
│ 3. .env (tracked, defaults)                    │
│ 4. Settings.py defaults                        │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Setup:**
```bash
# .env - Tracked (public defaults)
DEBUG=false
POSTGRES_HOST=db

# .env.local - Gitignored (per-machine secrets)
# Never committed to version control
DEBUG=true
DATABASE_PASSWORD=dev_only_change_me
OPENAI_API_KEY=sk-...
```

**Verification:**
```bash
# Ensure .env.local is gitignored
grep ".env.local" .gitignore  # Should find it

# List secrets in environment
env | grep -E "SECRET|PASSWORD|KEY|TOKEN"  # Verify no production secrets exposed
```

### 2.3 Database Credentials

**Development:**
```bash
POSTGRES_PASSWORD=dev_password_change_me  # In .env.local
```

**Production Equivalent:**
```bash
# Should use:
# - AWS Secrets Manager / Google Secret Manager
# - HashiCorp Vault
# - Kubernetes Secrets
# - Sealed Secrets (for GitOps)
# - Environment-specific rotation policies
```

**Current setup in docker-compose.devcontainer.yml:**
```yaml
environment:
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # From .env or .env.local
```

### 2.4 API Keys & LLM Secrets

**Development:**
```bash
# .env.local
OPENAI_API_KEY=sk-...  # Development key with rate limits
NEO4J_PASSWORD=password  # Development default
```

**Production Security:**
```python
# settings.py
import os
from pathlib import Path

if not DEBUG:
    # Production: require strong credentials
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY must be set in production")
    
    # Verify key format/rotation
    if not OPENAI_API_KEY.startswith('sk-'):
        raise ValueError("Invalid OpenAI API key format")
```

---

## 3. Production Parity

### 3.1 Security Headers Configuration

**Current settings.py:**
```python
SESSION_COOKIE_SECURE = True              # HTTPS only
SESSION_COOKIE_HTTPONLY = True            # No JavaScript access
SECURE_HSTS_SECONDS = 31536000            # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

**DevContainer Override:**
```bash
# .env.local
SESSION_COOKIE_SECURE=false      # Allow HTTP in dev
CSRF_COOKIE_SECURE=false         # Allow HTTP in dev
SECURE_SSL_REDIRECT=false        # Don't redirect to HTTPS
```

**Important:** These overrides ensure development works over HTTP while preserving production settings.

### 3.2 Database Security Settings

**Production-Ready (Current):**
```python
'OPTIONS': {
    'sslmode': 'prefer',           # Upgrade to SSL if available
    'keepalives': 1,               # TCP keepalives
    'keepalives_idle': 30,         # 30s idle timeout
    'keepalives_interval': 10,     # 10s interval
    'keepalives_count': 5,         # 5 retries
},
'CONN_MAX_AGE': 60,               # Connection pooling
```

**Development (Same):**
```python
# No changes needed for development
# Using same config ensures parity
```

**Recommended Production Improvements:**
```python
if not DEBUG:
    DATABASES['default']['OPTIONS']['sslmode'] = 'require'  # Enforce SSL
    DATABASES['default']['OPTIONS']['sslrootcert'] = '/etc/ssl/certs/ca-certificates.crt'
    DATABASES['default']['CONN_MAX_AGE'] = 300  # Higher for prod
```

### 3.3 Logging in Development vs Production

**Development (Verbose):**
```python
if DEBUG:
    LOGGING['root']['level'] = 'DEBUG'
    LOGGING['handlers']['console'] = {
        'class': 'logging.StreamHandler',
        'formatter': 'verbose'
    }
```

**Production (Restricted):**
```python
if not DEBUG:
    LOGGING['root']['level'] = 'WARNING'
    LOGGING['handlers']['syslog'] = {
        'class': 'logging.handlers.SysLogHandler',
        'formatter': 'structured'
    }
```

### 3.4 Cache Security

**Development (In-memory):**
```python
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }
    }
```

**Production (Redis with auth):**
```python
if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'rediss://user:password@redis.prod:6380/1',  # SSL + auth
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'ssl_certfile': '/etc/ssl/certs/ca.pem',
                    'ssl_keyfile': '/etc/ssl/private/key.pem',
                    'max_connections': 50,
                }
            }
        }
    }
```

---

## 4. Authentication & Authorization

### 4.1 User Management (Development)

**Auto-created superuser:**
```bash
# In post-create.sh
python manage.py shell << 'EOF'
User.objects.create_superuser('reconpoint', 'email@example.com', 'reconpoint')
EOF
```

**Security Note:**
- ✅ Development-only default password
- ⚠️ Never use in production
- ✅ Changed via Django admin or management command

**Production Setup:**
```bash
# Use environment-specific credentials
python manage.py createsuperuser  # Interactive (no defaults)

# Or from env (CI/CD):
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@prod.com \
DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 32) \
python manage.py createsuperuser --noinput
```

### 4.2 Two-Factor Authentication (Production-Ready) ✅

Already configured:
```python
INSTALLED_APPS += ['django_otp', 'django_otp.plugins.otp_totp', 'two_factor']
```

**In production:**
1. Enforce 2FA for admin users
2. Implement TOTP time-based OTP
3. Backup codes for account recovery
4. SMS backup option (optional)

### 4.3 Role-Based Access Control ✅

Configured via `django-role-permissions`:
```python
ROLEPERMISSIONS_MODULE = 'reconPoint.roles'
```

**Security Considerations:**
- ✅ Granular permissions defined in roles
- ✅ Middleware enforces access control
- ✅ Development: Test all permission combinations
- ✅ Production: Audit role assignments regularly

---

## 5. Input Validation & Sanitization

### 5.1 Django Built-in Protections

**CSRF Protection:**
```python
CSRF_COOKIE_SECURE = True  # (or False in dev)
CSRF_COOKIE_HTTPONLY = True

# All POST/PUT/DELETE requests require CSRF token
# Django forms auto-include: {% csrf_token %}
# DRF includes CSRF via middleware
```

**SQL Injection Prevention:**
```python
# ✅ GOOD - ORM handles escaping
from django.db import models
Target.objects.filter(name__icontains=user_input)  # Safe

# ❌ AVOID - Raw SQL
Target.objects.raw(f'SELECT * FROM targets WHERE name = {user_input}')  # Dangerous
```

**XSS Prevention:**
```python
# ✅ GOOD - Django auto-escapes in templates
{{ user_input }}  {# Automatically escaped #}

# ✅ GOOD - Explicit safe marking when needed
{{ trusted_html|safe }}  {# Only for trusted content #}

# ❌ AVOID - Raw HTML from user
{{ user_input|safe }}  {# Dangerous #}
```

### 5.2 DRF Serializer Validation

```python
from rest_framework import serializers

class ScanSerializer(serializers.ModelSerializer):
    # Field-level validation
    target = serializers.CharField(max_length=255, min_length=3)
    
    # Custom validation
    def validate_target(self, value):
        if not is_valid_domain(value):  # Custom validator
            raise serializers.ValidationError("Invalid domain format")
        return value
    
    class Meta:
        model = Scan
        fields = ['target', 'engine']
```

**Security Validation Workflow:**
```python
# Always validate in serializers, not views
class ScanViewSet(viewsets.ModelViewSet):
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate
        # Validation errors prevent database operations
```

### 5.3 File Upload Security

**Current configuration:**
```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 100000000  # 100MB
FILE_UPLOAD_PERMISSIONS = 0o644  # rw-r--r--
```

**Recommendations:**
```python
if not DEBUG:
    # Production security
    FILE_UPLOAD_MAX_MEMORY_SIZE = 50000000  # Reduce in prod
    
    # Whitelist allowed file types
    ALLOWED_UPLOAD_TYPES = ['.txt', '.pdf', '.csv', '.yaml']
    
    # Scan uploaded files for malware (optional)
    # Use: django-defender, django-clamav
```

**Upload View Example:**
```python
def validate_uploaded_file(uploaded_file):
    # Check file extension
    if not uploaded_file.name.lower().endswith(tuple(ALLOWED_UPLOAD_TYPES)):
        raise ValidationError("File type not allowed")
    
    # Check file size
    if uploaded_file.size > FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError("File too large")
    
    # Optionally scan for malware
    scan_file_for_malware(uploaded_file)
    
    return True
```

---

## 6. API Security

### 6.1 Authentication (DRF)

**Current Configuration:**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Recommended
        # or
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}
```

**JWT Token Setup (Recommended):**
```bash
pip install djangorestframework-simplejwt
```

```python
# settings.py
INSTALLED_APPS += ['rest_framework_simplejwt']

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # Short-lived
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),   # Refresh token
    'ROTATE_REFRESH_TOKENS': True,                  # Rotate on use
    'ALGORITHM': 'HS256',                           # Secure algorithm
    'SIGNING_KEY': SECRET_KEY,
}
```

```python
# urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

### 6.2 Rate Limiting

**Install:**
```bash
pip install djangorestframework-api-key
```

**Configure:**
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',      # Anonymous: 100 requests/hour
        'user': '1000/hour',     # Authenticated: 1000 requests/hour
    }
}
```

**Custom throttling:**
```python
from rest_framework.throttling import BaseThrottle

class ScanThrottle(BaseThrottle):
    """Allow 10 scans per hour per user."""
    
    def allow_request(self, request, view):
        cache_key = f'scans_{request.user.id}'
        request_count = cache.get(cache_key, 0)
        
        if request_count >= 10:
            return False
        
        cache.set(cache_key, request_count + 1, 3600)  # 1 hour
        return True
```

### 6.3 Permissions & Authorization

```python
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """Only owners can modify their objects."""
    
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class ScanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Scan.objects.all()
    
    def get_queryset(self):
        # Users only see their own scans
        if self.request.user.is_staff:
            return Scan.objects.all()
        return Scan.objects.filter(owner=self.request.user)
```

---

## 7. Dependency Security

### 7.1 Security Scanning

**Install:**
```bash
pip install bandit safety
```

**Scan for vulnerabilities:**
```bash
# Bandit - code security issues
bandit -r web/

# Safety - known vulnerabilities in dependencies
safety check requirements.txt
```

**Integration with pre-commit:**
```yaml
# .pre-commit-config.yaml
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.5
  hooks:
    - id: bandit
      args: ['-r', 'web/']
```

### 7.2 Dependency Updates

**Check for updates:**
```bash
pip list --outdated
pip-audit -r requirements.txt
```

**Security updates (automatic):**
```bash
# Use Dependabot or similar
# Configure in GitHub: Settings > Code and analysis > Dependabot
```

### 7.3 Lock File Management

**Generate lock file:**
```bash
pip freeze > requirements.lock
```

**Production deployment:**
```bash
pip install -r requirements.lock  # Pin exact versions
```

---

## 8. Celery Security

### 8.1 Task Security

**Current configuration:**
```python
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
```

**Production Security:**
```python
if not DEBUG:
    # Use SSL/TLS for Redis
    CELERY_BROKER_URL = "rediss://user:password@redis.prod:6380/0"
    CELERY_RESULT_BACKEND = "rediss://user:password@redis.prod:6380/0"
    
    # Enable message signing
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_BROKER_USE_SSL = True
    CELERY_RESULT_BACKEND_USE_SSL = True
```

### 8.2 Task Validation

```python
from celery import Task

class SecureTask(Task):
    """Base task with security checks."""
    
    def before_start(self, task_id, args, kwargs):
        # Validate task arguments
        if not self.validate_args(args, kwargs):
            raise SecurityError("Invalid task arguments")
    
    def validate_args(self, args, kwargs):
        # Custom validation
        return True
```

---

## 9. Monitoring & Auditing

### 9.1 Security Event Logging

```python
import logging

security_logger = logging.getLogger('security')

def log_security_event(event_type, user, details):
    """Log security-relevant events."""
    security_logger.warning(f"{event_type}: User={user}, Details={details}")

# Usage
log_security_event('FAILED_LOGIN', username, {'ip': request.META['REMOTE_ADDR']})
log_security_event('PERMISSION_DENIED', user, {'resource': 'admin_panel'})
log_security_event('DATA_EXPORT', user, {'records': 1000})
```

### 9.2 Audit Trail

Add to models:
```python
class AuditMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    
    class Meta:
        abstract = True

# Usage
class Scan(AuditMixin):
    target = models.CharField(max_length=255)
```

---

## 10. Network Security

### 10.1 Docker Network Isolation

**Current compose setup:**
```yaml
networks:
  reconpoint_network:
    name: reconpoint_network
```

**Benefits:**
- ✅ Services isolated from host network
- ✅ Only exposed ports are reachable
- ✅ Inter-service communication via DNS

### 10.2 Port Exposure

**DevContainer (localhost only):**
```yaml
ports:
  - "127.0.0.1:8000:8000"  # Django
  - "127.0.0.1:5432:5432"  # PostgreSQL
```

**Production (explicit, no localhost):**
```yaml
# Use load balancer/reverse proxy instead
# Never expose database ports directly
```

### 10.3 Firewall Rules

**Development (liberal):**
```bash
ALLOWED_HOSTS = "*"
```

**Production (restrictive):**
```bash
ALLOWED_HOSTS = [
    "reconpoint.example.com",
    "api.reconpoint.example.com",
]
```

---

## 11. Incident Response

### 11.1 Security Event Response

```bash
# 1. Check logs
grep -r "ERROR\|CRITICAL" logs/

# 2. Identify affected data
python manage.py dbshell
SELECT COUNT(*) FROM auth_user WHERE last_login > NOW() - INTERVAL '1 hour';

# 3. Isolate if needed
docker-compose down  # Stop services

# 4. Backup data
pg_dump -h db -U reconpoint > backup_incident.sql

# 5. Investigate
docker-compose logs web
```

### 11.2 Password Reset

```bash
# If credentials compromised
python manage.py changepassword reconpoint
```

---

## 12. Security Checklist

### Before Development
- [ ] Copy `.env` to `.env.local`
- [ ] Change default database password
- [ ] Verify `.env.local` is gitignored
- [ ] Enable pre-commit hooks: `pre-commit install`
- [ ] Scan dependencies: `safety check`

### During Development
- [ ] Use HTTPS (configure in settings)
- [ ] Validate all user input
- [ ] Don't commit secrets to git
- [ ] Run security linters: `bandit -r web/`
- [ ] Use authenticated API endpoints
- [ ] Enable CSRF protection
- [ ] Implement proper permissions

### Before Production
- [ ] Set `DEBUG = false`
- [ ] Change `SECRET_KEY`
- [ ] Update `ALLOWED_HOSTS`
- [ ] Enable SSL/TLS
- [ ] Set strong database password
- [ ] Rotate API keys
- [ ] Enable 2FA
- [ ] Run full security audit
- [ ] Review logs for errors/warnings
- [ ] Test all authentication mechanisms

### Production Operations
- [ ] Monitor logs for suspicious activity
- [ ] Rotate secrets regularly
- [ ] Patch dependencies promptly
- [ ] Backup database regularly
- [ ] Test disaster recovery
- [ ] Implement rate limiting
- [ ] Enable audit logging
- [ ] Review access logs weekly

---

## 13. Additional Resources

### Security Documentation
- [Django Security](https://docs.djangoproject.com/en/4.2/topics/security/)
- [DRF Security](https://www.django-rest-framework.org/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

### Tools & Services
- [BANDIT - Python security](https://bandit.readthedocs.io/)
- [Safety - Dependency vulnerabilities](https://safety.readthedocs.io/)
- [OWASP ZAP - Web app scanning](https://www.zaproxy.org/)
- [Snyk - Vulnerability scanning](https://snyk.io/)

### Best Practices
- [Secure SDLC](https://cheatsheetseries.owasp.org/)
- [DevSecOps](https://www.devsecops.org/)
- [Cloud Security Best Practices](https://cloud.google.com/security/best-practices)

---

## Summary

This DevContainer setup balances **development convenience** with **production security**:

| Aspect | Development | Production |
|--------|-------------|-----------|
| DEBUG | ✅ true | ❌ false |
| HTTPS | ❌ optional | ✅ required |
| Secrets | 💾 .env.local | 🔐 Secrets manager |
| Permissions | 🟢 liberal | 🔴 restrictive |
| Logging | 📢 verbose | 🔍 structured |
| Updates | ⏰ manual | 🤖 automated |

Follow this guide, enable security tools, and maintain vigilance during development.

