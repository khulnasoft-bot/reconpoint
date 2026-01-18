from django.db import models
from django.utils import timezone
from dashboard.models import ComplianceReport, ComplianceCheck
from startScan.models import Vulnerability, Subdomain
from targetApp.models import Domain
import json


class ComplianceEngine:
    """Automated compliance checking engine for various frameworks"""

    def __init__(self):
        self.frameworks = {
            'SOC2': self._soc2_checks,
            'ISO27001': self._iso27001_checks,
            'PCI_DSS': self._pci_dss_checks,
            'GDPR': self._gdpr_checks,
        }

    def run_compliance_check(self, organization, framework):
        """Run compliance checks for an organization"""
        if framework not in self.frameworks:
            raise ValueError(f"Unsupported framework: {framework}")

        check_function = self.frameworks[framework]
        findings = check_function(organization)

        # Create or update compliance report
        report, created = ComplianceReport.objects.get_or_create(
            organization=organization,
            report_type=framework,
            status='draft',
            defaults={'valid_until': timezone.now() + timezone.timedelta(days=365)}
        )

        report.findings = findings
        report.save()

        return report, findings

    def _soc2_checks(self, organization):
        """SOC 2 compliance checks"""
        findings = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

        # Check for exposed admin panels
        admin_subdomains = Subdomain.objects.filter(
            target_domain__project__name__icontains=organization,
            http_url__icontains='admin'
        )

        if admin_subdomains.exists():
            findings['failed'].append({
                'check': 'Admin Panel Exposure',
                'severity': 'high',
                'description': f'Found {admin_subdomains.count()} exposed admin panels',
                'remediation': 'Implement proper access controls and monitoring'
            })

        # Check for unencrypted communications
        http_only = Subdomain.objects.filter(
            target_domain__project__name__icontains=organization,
            http_url__startswith='http://'
        ).exclude(http_url__contains='https://')

        if http_only.exists():
            findings['warnings'].append({
                'check': 'Unencrypted Communications',
                'severity': 'medium',
                'description': f'Found {http_only.count()} endpoints using HTTP only',
                'remediation': 'Implement HTTPS everywhere'
            })

        # Check for high-severity vulnerabilities
        high_vulns = Vulnerability.objects.filter(
            target_domain__project__name__icontains=organization,
            severity__in=[3, 4, 5]  # high, critical
        )

        if high_vulns.exists():
            findings['failed'].append({
                'check': 'High-Severity Vulnerabilities',
                'severity': 'critical',
                'description': f'Found {high_vulns.count()} high-severity vulnerabilities',
                'remediation': 'Immediate remediation required'
            })

        return findings

    def _iso27001_checks(self, organization):
        """ISO 27001 compliance checks"""
        findings = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

        # Check for asset inventory completeness
        domains = Domain.objects.filter(project__name__icontains=organization)
        total_subdomains = Subdomain.objects.filter(
            target_domain__in=domains
        ).count()

        if total_subdomains < 10:  # Arbitrary threshold
            findings['warnings'].append({
                'check': 'Asset Inventory Completeness',
                'severity': 'medium',
                'description': 'Limited asset discovery - may indicate incomplete inventory',
                'remediation': 'Perform comprehensive asset discovery'
            })

        # Check for regular scanning
        recent_scans = domains.filter(
            start_scan_date__gte=timezone.now() - timezone.timedelta(days=90)
        )

        if recent_scans.count() < domains.count() * 0.8:  # 80% scanned recently
            findings['failed'].append({
                'check': 'Regular Security Assessments',
                'severity': 'high',
                'description': 'Not all assets scanned within last 90 days',
                'remediation': 'Implement regular automated scanning'
            })

        return findings

    def _pci_dss_checks(self, organization):
        """PCI DSS compliance checks"""
        findings = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

        # Check for card data exposure patterns
        card_keywords = ['card', 'payment', 'ccv', 'cvv', 'pan']
        exposed_endpoints = Subdomain.objects.filter(
            target_domain__project__name__icontains=organization
        ).filter(
            models.Q(page_title__icontains='card') |
            models.Q(content_type__icontains='card') |
            models.Q(http_url__regex=r'card|payment|cvv')
        )

        if exposed_endpoints.exists():
            findings['failed'].append({
                'check': 'Card Data Exposure',
                'severity': 'critical',
                'description': f'Potential card data exposure in {exposed_endpoints.count()} endpoints',
                'remediation': 'Immediate investigation and remediation required'
            })

        return findings

    def _gdpr_checks(self, organization):
        """GDPR compliance checks"""
        findings = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

        # Check for data processing disclosures
        privacy_pages = Subdomain.objects.filter(
            target_domain__project__name__icontains=organization,
            http_url__icontains='privacy'
        )

        if not privacy_pages.exists():
            findings['failed'].append({
                'check': 'Privacy Policy',
                'severity': 'high',
                'description': 'No privacy policy page found',
                'remediation': 'Publish comprehensive privacy policy'
            })

        # Check for cookie consent mechanisms
        cookie_pages = Subdomain.objects.filter(
            target_domain__project__name__icontains=organization,
            http_url__icontains='cookie'
        )

        if not cookie_pages.exists():
            findings['warnings'].append({
                'check': 'Cookie Consent',
                'severity': 'medium',
                'description': 'No cookie policy page found',
                'remediation': 'Implement cookie consent mechanism'
            })

        return findings


class RiskEngine:
    """Advanced risk prioritization engine"""

    def calculate_asset_criticality(self, subdomain):
        """Calculate asset criticality based on multiple factors"""
        from dashboard.models import AssetCriticality

        criticality, created = AssetCriticality.objects.get_or_create(
            subdomain=subdomain,
            defaults={'business_value': 5, 'data_sensitivity': 5}
        )

        # Factor in vulnerability count and severity
        vulns = subdomain.get_vulnerabilities
        vuln_score = sum(v.severity for v in vulns) / max(len(vulns), 1)

        # Factor in endpoint count
        endpoint_count = subdomain.get_endpoint_count

        # Factor in technologies (higher for sensitive tech)
        sensitive_tech = ['wordpress', 'joomla', 'drupal', 'php', 'mysql']
        tech_score = 1
        if any(tech.name.lower() in sensitive_tech for tech in subdomain.technologies.all()):
            tech_score = 3

        # Calculate business value
        criticality.business_value = min(10, vuln_score + endpoint_count/10 + tech_score)
        criticality.data_sensitivity = min(10, vuln_score + tech_score)

        criticality.calculate_criticality()
        return criticality

    def prioritize_vulnerabilities(self, organization):
        """Prioritize vulnerabilities based on risk scoring"""
        from dashboard.models import RiskPrioritization

        vulns = Vulnerability.objects.filter(
            target_domain__project__name__icontains=organization
        )

        for vuln in vulns:
            asset_crit = self.calculate_asset_criticality(vuln.subdomain)

            prioritization, created = RiskPrioritization.objects.get_or_create(
                vulnerability=vuln,
                defaults={'asset_criticality': asset_crit}
            )

            # Calculate exploitability (simplified CVSS-like)
            prioritization.exploitability_score = vuln.severity * 2

            # Business impact based on asset criticality
            prioritization.business_impact = asset_crit.criticality_score

            prioritization.calculate_risk()

        return RiskPrioritization.objects.filter(
            vulnerability__target_domain__project__name__icontains=organization
        ).order_by('-overall_risk_score')