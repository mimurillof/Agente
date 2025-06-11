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
    
    # Configurar el servidor Yahoo Finance
    yahoo_server_params = StdioServerParameters(
        command="uv",
        args=[
            "run",
            "--with",
            "mcp",
            "--with",
            "yfinance",
            "mcp",
            "run",
            "mcp_yahoo_finance.py"
        ],
        env={
            "APPDATA": "C:\\Users\\mikia\\AppData\\Roaming",
            "HOMEDRIVE": "C:",
            "HOMEPATH": "\\Users\\mikia",
            "LOCALAPPDATA": "C:\\Users\\mikia\\AppData\\Local",
            "PATH": "C:\\Users\\mikia\\AppData\\Local\\npm-cache\\_npx\\5a9d879542beca3a\\node_modules\\.bin;C:\\Users\\mikia\\mcp-tutorial\\node_modules\\.bin;C:\\Users\\mikia\\node_modules\\.bin;C:\\Users\\node_modules\\.bin;C:\\node_modules\\.bin;C:\\Program Files\\nodejs\\node_modules\\npm\\node_modules\\@npmcli\\run-script\\lib\\node-gyp-bin;C:\\Users\\mikia\\mcp-tutorial\\.venv\\Scripts;C:\\Users\\mikia\\bin;C:\\Program Files\\Git\\mingw64\\bin;C:\\Program Files\\Git\\usr\\local\\bin;C:\\Program Files\\Git\\usr\\bin;C:\\Program Files\\Git\\usr\\bin;C:\\Program Files\\Git\\mingw64\\bin;C:\\Program Files\\Git\\usr\\bin;C:\\Users\\mikia\\bin;C:\\WINDOWS\\system32;C:\\WINDOWS;C:\\WINDOWS\\System32\\Wbem;C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0;C:\\WINDOWS\\System32\\OpenSSH;C:\\Program Files\\Git\\cmd;C:\\Program Files\\nodejs;C:\\Program Files\\Docker\\Docker\\resources\\bin;C:\\Users\\mikia\\AppData\\Local\\Programs\\cursor\\resources\\app\\bin;C:\\Program Files\\NVIDIA Corporation\\NVIDIA App\\NvDLISR;C:\\Users\\mikia\\.local\\bin;C:\\Users\\mikia\\AppData\\Local\\Programs\\Trae\\bin;C:\\Users\\mikia\\AppData\\Local\\Microsoft\\WindowsApps;C:\\Users\\mikia\\AppData\\Local\\Programs\\Microsoft VS Code\\bin;C:\\Users\\mikia\\AppData\\Local\\GitHubDesktop\\bin;C:\\Users\\mikia\\AppData\\Roaming\\npm;C:\\Users\\mikia\\AppData\\Local\\Programs\\cursor\\resources\\app\\bin;C:\\Program Files\\Git\\usr\\bin\\vendor_perl;C:\\Program Files\\Git\\usr\\bin\\core_perl",
            "PROCESSOR_ARCHITECTURE": "AMD64",
            "SYSTEMDRIVE": "C:",
            "SYSTEMROOT": "C:\\WINDOWS",
            "TEMP": "C:\\Users\\mikia\\AppData\\Local\\Temp",
            "USERNAME": "mikia",
            "USERPROFILE": "C:\\Users\\mikia",
            **os.environ
        }
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
                    print("\nIniciando el análisis financiero...")
                    result = crew.kickoff()
                    print("\n\nResultado final del Análisis Financiero:")
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
                print("\nIniciando el análisis financiero (solo con Exa)...")
                result = crew.kickoff()
                print("\n\nResultado final del Análisis Financiero:")
                print(result)

    except Exception as e:
        print(f"Error conectando a los servidores MCP: {e}")
        print("Asegúrate de que los servidores MCP estén ejecutándose y sean accesibles con las configuraciones correctas.")

if __name__ == "__main__":
    run()