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
    Ejecuta el crew de análisis financiero.
    """
    # Configurar el servidor Exa
    exa_server_params = StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@smithery/cli@latest",
            "run",
            "exa",
            "--key",
            "15c33ff2-ff20-4e8d-a415-d2a9f4da8b33"
        ]
    )
    
    path_to_yahoo_server = "C:/Users/mikia/mcp-tutorial/mcp_yahoo_finance.py"
    
    # Configurar el servidor Yahoo Finance
    yahoo_server_params = StdioServerParameters(
        command="python",
        args=[path_to_yahoo_server], # Pasamos la ruta correcta como argumento
        env=dict(os.environ)
    )

    # Usar ambos servidores MCP - inicializamos con el servidor principal (Exa)
    try:
        with MCPServerAdapter(exa_server_params) as exa_tools:
            # Intentar también el servidor Yahoo Finance en un contexto separado
            try:
                with MCPServerAdapter(yahoo_server_params) as yahoo_tools:
                    # Combinar las herramientas de ambos servidores
                    all_tools = list(exa_tools) + list(yahoo_tools)
                    print(f"Herramientas MCP disponibles: {[tool.name for tool in all_tools]}")
                    
                    # Cargar configuraciones de agentes y tareas
                    agents_config = get_agents_config()
                    tasks_config = get_tasks_config()                    # 1. Crear agentes explícitamente
                    researcher = Agent(
                        **agents_config['financial_researcher'],
                        tools=all_tools  # Inyectar todas las herramientas
                    )

                    reporting_analyst = Agent(**agents_config['financial_reporter'])

                    # 2. Crear tareas explícitamente y asignar los agentes
                    research_task_details = tasks_config['financial_research_task'].copy()
                    research_task_details.pop('agent', None)
                    research_task = Task(
                        **research_task_details,
                        agent=researcher
                    )

                    reporting_task_details = tasks_config['financial_reporting_task'].copy()
                    reporting_task_details.pop('agent', None)
                    reporting_task = Task(
                        **reporting_task_details,
                        agent=reporting_analyst
                    )

                    # 3. Crear el Crew con los agentes y tareas
                    crew = Crew(
                        agents=[researcher, reporting_analyst],
                        tasks=[research_task, reporting_task],
                        process=Process.sequential,
                        verbose=True
                    )                    # Ejecutar el crew
                    print("/nIniciando el análisis financiero...")
                    result = crew.kickoff()
                    print("/n/nResultado final del Análisis Financiero:")
                    print(result)
                    
            except Exception as yahoo_error:
                print(f"Error con el servidor Yahoo Finance: {yahoo_error}")
                print("Continuando solo con el servidor Exa...")
                
                # Fallback: usar solo las herramientas de Exa
                print(f"Herramientas MCP disponibles (solo Exa): {[tool.name for tool in exa_tools]}")
                
                # Cargar configuraciones de agentes y tareas
                agents_config = get_agents_config()
                tasks_config = get_tasks_config()                # 1. Crear agentes explícitamente
                researcher = Agent(
                    **agents_config['financial_researcher'],
                    tools=exa_tools  # Solo herramientas de Exa
                )

                reporting_analyst = Agent(**agents_config['financial_reporter'])

                # 2. Crear tareas explícitamente y asignar los agentes
                research_task_details = tasks_config['financial_research_task'].copy()
                research_task_details.pop('agent', None)
                research_task = Task(
                    **research_task_details,
                    agent=researcher
                )

                reporting_task_details = tasks_config['financial_reporting_task'].copy()
                reporting_task_details.pop('agent', None)
                reporting_task = Task(
                    **reporting_task_details,
                    agent=reporting_analyst
                )

                # 3. Crear el Crew con los agentes y tareas
                crew = Crew(
                    agents=[researcher, reporting_analyst],
                    tasks=[research_task, reporting_task],
                    process=Process.sequential,
                    verbose=True
                )                # Ejecutar el crew
                print("/nIniciando el análisis financiero (solo con Exa)...")
                result = crew.kickoff()
                print("/n/nResultado final del Análisis Financiero:")
                print(result)

    except Exception as e:
        print(f"Error conectando a los servidores MCP: {e}")
        print("Asegúrate de que los servidores MCP estén ejecutándose y sean accesibles con las configuraciones correctas.")

if __name__ == "__main__":
    run()