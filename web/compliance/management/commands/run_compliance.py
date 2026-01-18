from django.core.management.base import BaseCommand
from compliance.engine import ComplianceEngine, RiskEngine
from dashboard.models import ComplianceReport

class Command(BaseCommand):
    help = 'Run compliance checks and risk assessments'

    def add_arguments(self, parser):
        parser.add_argument('organization', type=str, help='Organization name')
        parser.add_argument('--framework', type=str, default='SOC2',
                          choices=['SOC2', 'ISO27001', 'PCI_DSS', 'GDPR'],
                          help='Compliance framework to check')
        parser.add_argument('--risk-only', action='store_true',
                          help='Only run risk assessment')

    def handle(self, *args, **options):
        org = options['organization']
        framework = options['framework']
        risk_only = options['risk_only']

        if risk_only:
            self.stdout.write(f'Running risk assessment for {org}...')
            risk_engine = RiskEngine()
            risks = risk_engine.prioritize_vulnerabilities(org)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Risk assessment complete. Found {risks.count()} prioritized vulnerabilities.'
                )
            )
        else:
            self.stdout.write(f'Running {framework} compliance check for {org}...')

            compliance_engine = ComplianceEngine()
            report, findings = compliance_engine.run_compliance_check(org, framework)

            passed = len(findings.get('passed', []))
            failed = len(findings.get('failed', []))
            warnings = len(findings.get('warnings', []))

            self.stdout.write(
                self.style.SUCCESS(
                    f'Compliance check complete: {passed} passed, {warnings} warnings, {failed} failed'
                )
            )

            if failed > 0:
                self.stdout.write(
                    self.style.WARNING('Critical compliance issues found. Review report immediately.')
                )