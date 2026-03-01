from abc import abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import time
from src.interfaces.repository_fetcher import RepositoryFetcher
from src.utils.output_formatter import RepositoryOutputFormatter

class BaseRepositoryFetcher(RepositoryFetcher):
    def __init__(self):
        self.output = RepositoryOutputFormatter()
        
        # Define a raiz do projeto (subindo de src/core/interfaces para a raiz)
        # Caminho absoluto para evitar erros de diretório de execução
        self.base_path = Path(__file__).resolve().parent.parent.parent.parent
        
        # Mapeia os arquivos conforme a nova estrutura sugerida
        self.query_file = self.base_path / "src" / "infrastructure" / "graphql" / "query.graphql"
        self.data_dir = self.base_path / "data"

    def _get_query_content(self) -> str:
        if not self.query_file.exists():
            raise FileNotFoundError(f"Arquivo de query não encontrado em: {self.query_file}")
        return self.query_file.read_text(encoding="utf-8")

    @abstractmethod
    def _execute_request(self, query: str, cursor: Optional[str]) -> Dict[str, Any]:
        """Cada subclasse implementa sua forma de requisitar (CLI ou HTTP)"""
        pass

    def fetch(self, pages: int = 10, save_json: bool = False) -> List[Dict[str, Any]]:
        query_content = self._get_query_content()
        all_repos = []
        cursor = None
        
        self.output.print_fetch_start(self.__class__.__name__)

        for page in range(1, pages + 1):
            data = self._execute_request(query_content, cursor)
            
            # 1. Validação de segurança da resposta raiz
            if data is None:
                self.output.print_error("Falha crítica: a resposta da API retornou None.")
                break

            if 'data' not in data or data.get('data') is None or data['data'].get('search') is None:
                err = data.get('errors', 'Resposta malformada ou erro de permissão')
                self.output.print_error(f"Erro na resposta: {err}")
                break

            search_results = data['data']['search']
            repos_this_page = []

            for edge in search_results.get('edges', []):
                node = edge.get('node')
                if not node: continue # Pula se o nó estiver vazio
                
                # 2. Extração segura
                repo_data = self._parse_node(node)
                
                # 3. Padronização segura (aqui costuma morar o perigo)
                try:
                    standardized = self._standardize_repository(repo_data)
                    repos_this_page.append(standardized)
                    all_repos.append(standardized)
                except Exception as e:
                    self.output.print_error(f"Erro ao padronizar repositório {repo_data.get('name')}: {e}")
                    continue

            self.output.print_page_progress(page, pages, len(repos_this_page), len(all_repos))

            page_info = search_results.get('pageInfo', {})
            if not page_info.get('hasNextPage'):
                break
            
            cursor = page_info.get('endCursor')
            time.sleep(0.5)

        if save_json: self._save_json(all_repos)
        return all_repos

    def _parse_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai dados tratando todos os possíveis campos nulos do GraphQL"""
        return {
            "name": node.get('name', 'N/A'),
            "url": node.get('url', ''),
            "stargazerCount": node.get('stargazerCount', 0),
            "createdAt": node.get('createdAt', ''),
            "updatedAt": node.get('updatedAt', ''),
            "primaryLanguage": (node.get('primaryLanguage') or {}).get('name', 'Unknown'),
            "releases_count": (node.get('releases') or {}).get('totalCount', 0),
            "pullRequests_count": (node.get('pullRequests') or {}).get('totalCount', 0),
            "open_issues": (node.get('openIssues') or {}).get('totalCount', 0),
            "closed_issues": (node.get('closedIssues') or {}).get('totalCount', 0)
        }

    def _save_json(self, repos: List[Dict[str, Any]]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        output_file = self.data_dir / 'repos.json'
        
        simplified = [
            {"name": r["name"], "stars": r["stargazerCount"], 
             "language": r["primaryLanguage"], "url": r["url"]} 
            for r in repos
        ]
        
        output_file.write_text(json.dumps(simplified, indent=2), encoding='utf-8')
        self.output.print_save_success(str(output_file))