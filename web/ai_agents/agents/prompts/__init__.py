"""Prompt management for reconPoint AI Agents."""

import os
from jinja2 import Environment, FileSystemLoader, Template

PROMPT_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(PROMPT_DIR))

def render_prompt(template_name: str, **kwargs) -> str:
    """Render a Jinja2 prompt template."""
    template = env.get_template(template_name)
    return template.render(**kwargs)

# Shorthand for common prompts
pa_crew = env.get_template("pa_crew.jinja")
pa_agent = env.get_template("pa_agent.jinja")
pa_assist = env.get_template("pa_assist.jinja")
