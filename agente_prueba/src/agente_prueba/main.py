#!/usr/bin/env python
# src/latest_ai_development/main.py
import os
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
from agente_prueba.crew import LatestAiDevelopmentCrew

def run():
    """
    Ejecuta el crew de investigación de IA.
    """
    brave_api_key = os.getenv("BRAVE_API_KEY")
    if not brave_api_key:
        print("Error: BRAVE_API_KEY environment variable not set. This is required for the researcher agent to work.")
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

    # Inicializar el crew
    crew_instance = LatestAiDevelopmentCrew()

    # Configurar las herramientas MCP para el investigador
    with MCPServerAdapter(server_params) as mcp_tools:
        print(f"Herramientas MCP disponibles: {[tool.name for tool in mcp_tools]}")
        
        # Verificar que la herramienta de búsqueda web esté disponible
        search_tools = [tool for tool in mcp_tools if "brave_web_search" in tool.name.lower()]
        if not search_tools:
            print("Error: No se encontró la herramienta de búsqueda web (brave_web_search)")
            return
            
        print("Herramienta de búsqueda web encontrada y configurada correctamente")
        crew_instance.researcher_tools = mcp_tools

        # Ejecutar el crew
        print("\nIniciando la investigación...")
        result = crew_instance.crew().kickoff()
        print("\n\nResultado final del Crew:")
        print(result)

if __name__ == "__main__":
    run()