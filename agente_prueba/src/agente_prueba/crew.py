# src/latest_ai_development/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
# MCPServerAdapter and StdioServerParameters will be used in main.py
# from crewai_tools import MCPServerAdapter # No longer used directly here
# from mcp import StdioServerParameters # No longer used directly here
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Optional
import yaml
import os
from pathlib import Path

@CrewBase
class LatestAiDevelopmentCrew:
    """Crew para investigación y análisis de desarrollos en IA"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "config"
        self.agents_config = self._load_config("agents.yaml")
        self.tasks_config = self._load_config("tasks.yaml")
        self.researcher_tools: Optional[List] = None

    def _load_config(self, filename: str) -> dict:
        """Carga la configuración desde un archivo YAML"""
        config_path = self.config_dir / filename
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @agent
    def researcher(self) -> Agent:
        """Crea el agente investigador"""
        tools = self.researcher_tools or []
        return Agent(
            **self.agents_config['researcher'],
            tools=tools
        )

    @agent
    def reporting_analyst(self) -> Agent:
        """Crea el agente analista de reportes"""
        return Agent(**self.agents_config['reporting_analyst'])

    @task
    def research_task(self) -> Task:
        """Crea la tarea de investigación"""
        return Task(**self.tasks_config['research_task'])

    @task
    def reporting_task(self) -> Task:
        """Crea la tarea de reporte"""
        return Task(**self.tasks_config['reporting_task'])

    @crew
    def crew(self) -> Crew:
        """Crea y configura el crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )