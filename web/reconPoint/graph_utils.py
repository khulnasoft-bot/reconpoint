from django.conf import settings
from neo4j import GraphDatabase


class AttackPathGraph:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def create_attack_path(self, subdomain_id, vuln_id):
        with self.driver.session() as session:
            session.run(
                "MERGE (s:Subdomain {id: $sub_id}) "
                "MERGE (v:Vulnerability {id: $vuln_id}) "
                "MERGE (s)-[:HAS_VULNERABILITY]->(v)",
                sub_id=subdomain_id,
                vuln_id=vuln_id,
            )

    def get_attack_paths(self, domain_id):
        with self.driver.session() as session:
            result = session.run(
                "MATCH (d:Domain {id: $domain_id})-[:HAS_SUBDOMAIN]->(s:Subdomain)-[:HAS_VULNERABILITY]->(v:Vulnerability) "
                "RETURN s.name, v.name, v.severity",
                domain_id=domain_id,
            )
            return [record for record in result]


# Usage example
# graph = AttackPathGraph()
# graph.create_attack_path(subdomain.id, vuln.id)
# paths = graph.get_attack_paths(domain.id)
