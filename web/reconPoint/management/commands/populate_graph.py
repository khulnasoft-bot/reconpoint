from django.core.management.base import BaseCommand

from reconPoint.graph_utils import AttackPathGraph
from startScan.models import Subdomain, Vulnerability


class Command(BaseCommand):
    help = "Populate Neo4j graph with attack paths"

    def handle(self, *args, **options):
        graph = AttackPathGraph()
        try:
            # Create domain nodes (simplified)
            for sub in Subdomain.objects.all():
                for vuln in sub.get_vulnerabilities:
                    graph.create_attack_path(sub.id, vuln.id)
            self.stdout.write(self.style.SUCCESS("Graph populated successfully"))
        finally:
            graph.close()
