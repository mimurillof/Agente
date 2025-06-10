#!/usr/bin/env python
# src/agente_prueba/main.py
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
# Importa las nuevas funciones para cargar la configuración
from agente_prueba.crew import get_agents_config, get_tasks_config

def run():
    """
    Ejecuta el crew de investigación de IA.
    """
    brave_api_key = os.getenv("BRAVE_API_KEY")
    if not brave_api_key:
        print("Error: La variable de entorno BRAVE_API_KEY no está configurada.")
        return

    # Configurar el servidor MCP para Brave Search
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-brave-search"
        ],
        env={"BRAVE_API_KEY": brave_api_key}
    )

    # El MCPServerAdapter debe estar activo durante la ejecución del crew
    with MCPServerAdapter(server_params) as mcp_tools:
        print(f"Herramientas MCP disponibles: {[tool.name for tool in mcp_tools]}")

        # Cargar configuraciones de agentes y tareas
        agents_config = get_agents_config()
        tasks_config = get_tasks_config()

        # 1. Crear agentes explícitamente
        researcher = Agent(
            **agents_config['researcher'],
            tools=mcp_tools  # Inyectar las herramientas directamente aquí
        )

        reporting_analyst = Agent(**agents_config['reporting_analyst'])

        # 2. Crear tareas explícitamente y asignar los agentes
        research_task_details = tasks_config['research_task'].copy()
        research_task_details.pop('agent', None) # Eliminar la referencia de agente de la configuración
        research_task = Task(
            **research_task_details,
            agent=researcher # Asignar la instancia de agente creada
        )

        reporting_task_details = tasks_config['reporting_task'].copy()
        reporting_task_details.pop('agent', None) # Eliminar la referencia de agente de la configuración
        reporting_task = Task(
            **reporting_task_details,
            agent=reporting_analyst # Asignar la instancia de agente creada
        )

        # 3. Crear el Crew con los agentes y tareas
        crew = Crew(
            agents=[researcher, reporting_analyst],
            tasks=[research_task, reporting_task],
            process=Process.sequential,
            verbose=True
        )

        # Ejecutar el crew
        print("\nIniciando la investigación...")
        result = crew.kickoff()
        print("\n\nResultado final del Crew:")
        print(result)

if __name__ == "__main__":
    run()