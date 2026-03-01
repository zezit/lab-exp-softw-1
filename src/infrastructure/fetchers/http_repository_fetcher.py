import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any, Optional
from src.core.interfaces.repository_fetcher import BaseRepositoryFetcher

class HttpRepositoryFetcher(BaseRepositoryFetcher):
    def __init__(self, token: Optional[str] = None):
        super().__init__()
        
        # Garante que o load_dotenv encontre o arquivo na raiz do projeto
        env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)
        
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.api_url = "https://api.github.com/graphql"

    def _execute_request(self, query: str, cursor: Optional[str]) -> Dict[str, Any]:
        if not self.token:
            return {"errors": "GITHUB_TOKEN não configurado no .env", "data": None}

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # O GraphQL diferencia 'null' (CLI) de None (JSON)
        variables = {"cursor": cursor} if cursor else {"cursor": None}
        
        try:
            response = requests.post(
                self.api_url,
                json={"query": query, "variables": variables},
                headers=headers
            )
            # Retorna o JSON independente do status para tratarmos no BaseFetcher
            return response.json()
        except Exception as e:
            return {"errors": str(e), "data": None}