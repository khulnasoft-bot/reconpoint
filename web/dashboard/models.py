from django.db import models
from reconPoint.definitions import *
from django.contrib.auth.models import User


class SearchHistory(models.Model):
	query = models.CharField(max_length=1000)

	def __str__(self):
		return self.query


class Project(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=500)
	slug = models.SlugField(unique=True)
	insert_date = models.DateTimeField()

	def __str__(self):
		return self.slug


class OpenAiAPIKey(models.Model):
	id = models.AutoField(primary_key=True)
	key = models.CharField(max_length=500)

	def __str__(self):
		return self.key
	

class OllamaSettings(models.Model):
	id = models.AutoField(primary_key=True)
	selected_model = models.CharField(max_length=500)
	use_ollama = models.BooleanField(default=True)

	def __str__(self):
		return self.selected_model


class NetlasAPIKey(models.Model):
	id = models.AutoField(primary_key=True)
	key = models.CharField(max_length=500)

	def __str__(self):
		return self.key
	

class ChaosAPIKey(models.Model):
	id = models.AutoField(primary_key=True)
	key = models.CharField(max_length=500)

	def __str__(self):
		return self.key
	

class HackerOneAPIKey(models.Model):
	id = models.AutoField(primary_key=True)
	username = models.CharField(max_length=500)
	key = models.CharField(max_length=500)

	def __str__(self):
		return self.username


class InAppNotification(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
	notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='system')
	status = models.CharField(max_length=10, choices=NOTIFICATION_STATUS_TYPES, default='info')
	title = models.CharField(max_length=255)
	description = models.TextField()
	icon = models.CharField(max_length=50) # mdi icon class name
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	redirect_link = models.URLField(max_length=255, blank=True, null=True)
	open_in_new_tab = models.BooleanField(default=False)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		if self.notification_type == 'system':
			return f"System wide notif: {self.title}"
		else:
			return f"Project wide notif: {self.project.name}: {self.title}"
		
	@property
	def is_system_wide(self):
		# property to determine if the notification is system wide or project specific
		return self.notification_type == 'system'


class UserPreferences(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	bug_bounty_mode = models.BooleanField(default=True)
	
	def __str__(self):
		return f"{self.user.username}'s preferences"


class ComplianceReport(models.Model):
    REPORT_TYPES = [
        ('SOC2', 'SOC 2'),
        ('ISO27001', 'ISO 27001'),
        ('PCI_DSS', 'PCI DSS'),
        ('GDPR', 'GDPR'),
        ('HIPAA', 'HIPAA'),
    ]

    organization = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_date = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    status = models.CharField(max_length=20, default='draft')  # draft, approved, expired
    findings = models.JSONField(default=dict)  # Store compliance findings
    remediation_plan = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['organization', 'report_type']),
            models.Index(fields=['status', 'valid_until']),
        ]


class ComplianceCheck(models.Model):
    SEVERITY_LEVELS = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    framework = models.CharField(max_length=20)  # SOC2, ISO27001, etc.
    automated = models.BooleanField(default=True)
    check_logic = models.TextField()  # Python code or rule definition
    last_run = models.DateTimeField(null=True, blank=True)
    pass_count = models.IntegerField(default=0)
    fail_count = models.IntegerField(default=0)


class AssetCriticality(models.Model):
    CRITICALITY_LEVELS = [
        ('very_high', 'Very High'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('very_low', 'Very Low'),
    ]

    subdomain = models.OneToOneField('startScan.Subdomain', on_delete=models.CASCADE)
    business_value = models.IntegerField(default=5)  # 1-10 scale
    data_sensitivity = models.IntegerField(default=5)  # 1-10 scale
    criticality_score = models.FloatField(default=0)  # Calculated score
    criticality_level = models.CharField(max_length=10, choices=CRITICALITY_LEVELS, default='medium')
    assessed_date = models.DateTimeField(auto_now=True)
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def calculate_criticality(self):
        # Simple scoring algorithm
        score = (self.business_value * 0.6) + (self.data_sensitivity * 0.4)
        self.criticality_score = score

        if score >= 8:
            self.criticality_level = 'very_high'
        elif score >= 6:
            self.criticality_level = 'high'
        elif score >= 4:
            self.criticality_level = 'medium'
        elif score >= 2:
            self.criticality_level = 'low'
        else:
            self.criticality_level = 'very_low'

        self.save()


class AttackPath(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    entry_point = models.ForeignKey('startScan.Subdomain', on_delete=models.CASCADE, related_name='attack_entry_points')
    target_asset = models.ForeignKey('startScan.Subdomain', on_delete=models.CASCADE, related_name='attack_targets')
    steps = models.JSONField(default=list)  # List of attack steps
    risk_score = models.FloatField(default=0)
    exploitability = models.CharField(max_length=20, default='low')  # low, medium, high
    impact = models.CharField(max_length=20, default='low')  # low, medium, high
    created_date = models.DateTimeField(auto_now_add=True)
    discovered_by = models.CharField(max_length=50, default='system')  # system, manual, ai

    class Meta:
        indexes = [
            models.Index(fields=['risk_score', 'exploitability']),
            models.Index(fields=['entry_point', 'target_asset']),
        ]


class RiskPrioritization(models.Model):
    PRIORITY_LEVELS = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Info'),
    ]

    vulnerability = models.OneToOneField('startScan.Vulnerability', on_delete=models.CASCADE)
    asset_criticality = models.ForeignKey(AssetCriticality, on_delete=models.CASCADE)
    exploitability_score = models.FloatField(default=0)  # CVSS-like scoring
    business_impact = models.FloatField(default=0)
    overall_risk_score = models.FloatField(default=0)
    priority_level = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    remediation_effort = models.CharField(max_length=20, default='medium')  # low, medium, high
    sla_days = models.IntegerField(default=30)  # Days to remediate
    calculated_date = models.DateTimeField(auto_now=True)

    def calculate_risk(self):
        # Risk = (Asset Criticality + Exploitability + Business Impact) / 3
        self.overall_risk_score = (self.asset_criticality.criticality_score + self.exploitability_score + self.business_impact) / 3

        if self.overall_risk_score >= 8:
            self.priority_level = 'critical'
        elif self.overall_risk_score >= 6:
            self.priority_level = 'high'
        elif self.overall_risk_score >= 4:
            self.priority_level = 'medium'
        elif self.overall_risk_score >= 2:
            self.priority_level = 'low'
        else:
            self.priority_level = 'info'

        self.save()
