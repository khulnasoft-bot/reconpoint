
import openai
import re
from reconPoint.common_func import get_open_ai_key, parse_llm_vulnerability_report
from reconPoint.definitions import VULNERABILITY_DESCRIPTION_SYSTEM_MESSAGE, ATTACK_SUGGESTION_GPT_SYSTEM_PROMPT, OLLAMA_INSTANCE
from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from dashboard.models import OllamaSettings


class LLMVulnerabilityReportGenerator:

	def __init__(self, logger):
		selected_model = OllamaSettings.objects.first()
		self.model_name = selected_model.selected_model if selected_model else 'gpt-3.5-turbo'
		self.use_ollama = selected_model.use_ollama if selected_model else False
		self.openai_api_key = None
		self.logger = logger
	
	def get_vulnerability_description(self, description):
		"""Generate Vulnerability Description using GPT.

		Args:
			description (str): Vulnerability Description message to pass to GPT.

		Returns:
			(dict) of {
				'description': (str)
				'impact': (str),
				'remediation': (str),
				'references': (list) of urls
			}
		"""
		self.logger.info(f"Generating Vulnerability Description for: {description}")
		if self.use_ollama:
			prompt = VULNERABILITY_DESCRIPTION_SYSTEM_MESSAGE + "\nUser: " + description
			prompt = re.sub(r'\t', '', prompt)
			self.logger.info(f"Using Ollama for Vulnerability Description Generation")
			llm = Ollama(
				base_url=OLLAMA_INSTANCE, 
				model=self.model_name
			)
			response_content = llm.invoke(prompt)
			# self.logger.info(response_content)
		else:
			self.logger.info(f'Using OpenAI API for Vulnerability Description Generation')
			openai_api_key = get_open_ai_key()
			if not openai_api_key:
				return {
					'status': False,
					'error': 'OpenAI API Key not set'
				}
			try:
				prompt = re.sub(r'\t', '', VULNERABILITY_DESCRIPTION_SYSTEM_MESSAGE)
				openai.api_key = openai_api_key
				gpt_response = openai.ChatCompletion.create(
				model=self.model_name,
				messages=[
						{'role': 'system', 'content': prompt},
						{'role': 'user', 'content': description}
					]
				)

				response_content = gpt_response['choices'][0]['message']['content']
			except Exception as e:
				return {
					'status': False,
					'error': str(e)
				}
			
		response = parse_llm_vulnerability_report(response_content)

		if not response:
			return {
				'status': False,
				'error': 'Failed to parse LLM response'
			}

		return {
			'status': True,
			'description': response.get('description', ''),
			'impact': response.get('impact', ''),
			'remediation': response.get('remediation', ''),
			'references': response.get('references', []),
		}


class LLMAttackSuggestionGenerator:

	def __init__(self, logger):
		selected_model = OllamaSettings.objects.first()
		self.model_name = selected_model.selected_model if selected_model else 'gpt-3.5-turbo'
		self.use_ollama = selected_model.use_ollama if selected_model else False
		self.openai_api_key = None
		self.logger = logger

	def get_attack_suggestion(self, user_input):
		'''
			user_input (str): input for gpt
		'''
		if self.use_ollama:
			self.logger.info(f"Using Ollama for Attack Suggestion Generation")
			prompt = ATTACK_SUGGESTION_GPT_SYSTEM_PROMPT + "\nUser: " + user_input	
			prompt = re.sub(r'\t', '', prompt)
			llm = Ollama(
				base_url=OLLAMA_INSTANCE, 
				model=self.model_name
			)
			response_content = llm.invoke(prompt)
			self.logger.info(response_content)
		else:
			self.logger.info(f'Using OpenAI API for Attack Suggestion Generation')
			openai_api_key = get_open_ai_key()
			if not openai_api_key:
				return {
					'status': False,
					'error': 'OpenAI API Key not set'
				}
			try:
				prompt = re.sub(r'\t', '', ATTACK_SUGGESTION_GPT_SYSTEM_PROMPT)
				openai.api_key = openai_api_key
				gpt_response = openai.ChatCompletion.create(
				model=self.model_name,
				messages=[
						{'role': 'system', 'content': prompt},
						{'role': 'user', 'content': user_input}
					]
				)
				response_content = gpt_response['choices'][0]['message']['content']
			except Exception as e:
				return {
					'status': False,
					'error': str(e),
					'input': user_input
				}
		return {
			'status': True,
			'description': response_content,
			'input': user_input
		}


class ReconAgent:
    def __init__(self, logger):
        selected_model = OllamaSettings.objects.first()
        self.use_ollama = selected_model.use_ollama if selected_model else False
        self.model_name = selected_model.selected_model if selected_model else 'gpt-3.5-turbo'
        self.logger = logger

        if self.use_ollama:
            self.llm = Ollama(base_url=OLLAMA_INSTANCE, model=self.model_name)
        else:
            openai_api_key = get_open_ai_key()
            self.llm = ChatOpenAI(model_name=self.model_name, openai_api_key=openai_api_key)

        # Enhanced tools for advanced recon
        self.tools = [
            Tool(
                name="SubdomainDiscovery",
                func=self.mock_subdomain_discovery,
                description="Discover subdomains for a given domain"
            ),
            Tool(
                name="VulnerabilityScan",
                func=self.mock_vuln_scan,
                description="Scan for vulnerabilities on a subdomain"
            ),
            Tool(
                name="AttackPathAnalysis",
                func=self.analyze_attack_paths,
                description="Analyze potential attack paths between assets"
            ),
            Tool(
                name="RiskAssessment",
                func=self.assess_risk,
                description="Assess overall risk of discovered assets"
            ),
            Tool(
                name="ComplianceCheck",
                func=self.check_compliance,
                description="Check compliance status against frameworks"
            ),
        ]

        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent="zero-shot-react-description",
            verbose=True,
            max_iterations=5
        )

    def mock_subdomain_discovery(self, domain):
        # Placeholder: In real implementation, call actual discovery
        return f"Discovered subdomains for {domain}: sub1.{domain}, sub2.{domain}"

    def mock_vuln_scan(self, subdomain):
        # Placeholder: Call actual scan
        return f"Scanned {subdomain}: Found XSS vulnerability"

    def analyze_attack_paths(self, domain):
        """Analyze potential attack paths in the domain"""
        from reconPoint.graph_utils import AttackPathGraph

        graph = AttackPathGraph()
        try:
            paths = graph.get_attack_paths(domain)
            graph.close()
            return f"Found {len(paths)} potential attack paths in {domain}"
        except Exception as e:
            return f"Error analyzing attack paths: {str(e)}"

    def assess_risk(self, domain):
        """Comprehensive risk assessment"""
        from compliance.engine import RiskEngine

        engine = RiskEngine()
        risks = engine.prioritize_vulnerabilities(domain)

        high_risks = risks.filter(priority_level__in=['critical', 'high'])
        return f"Risk assessment for {domain}: {high_risks.count()} high-priority issues found"

    def check_compliance(self, domain):
        """Check compliance status"""
        from compliance.engine import ComplianceEngine

        engine = ComplianceEngine()
        report, findings = engine.run_compliance_check(domain, 'SOC2')

        failed_checks = len(findings.get('failed', []))
        return f"Compliance check for {domain}: {failed_checks} failed checks"

    def run_autonomous_recon(self, target_domain):
        """Run fully autonomous reconnaissance with AI decision making"""
        prompt = f"""
        Perform comprehensive reconnaissance on {target_domain}.
        Follow this workflow:
        1. Discover subdomains
        2. Analyze attack paths between discovered assets
        3. Assess overall risk profile
        4. Check compliance status
        5. Prioritize findings based on risk and compliance impact

        Make intelligent decisions about which tools to use and when to stop.
        """

        try:
            result = self.agent.run(prompt)
            return {'status': True, 'result': result}
        except Exception as e:
            return {'status': False, 'error': str(e)}

    def run_recon(self, target_domain):
        """Legacy method for backward compatibility"""
        return self.run_autonomous_recon(target_domain)
		