import os
import json
import pathlib
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

from .interfaces.repository_fetcher import RepositoryFetcher
from .utils.output_formatter import RepositoryOutputFormatter

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com/graphql"


class HttpRepositoryFetcher(RepositoryFetcher):
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or GITHUB_TOKEN
        self.output = RepositoryOutputFormatter()
    
    def _load_query(self) -> str:
        query_path = pathlib.Path(__file__).parent / "query.graphql"
        with open(query_path, 'r') as f:
            return f.read()
    
    def fetch(self, pages: int = 10, save_json: bool = False) -> List[Dict[str, Any]]:
        if not self.token:
            self.output.print_error("GITHUB_TOKEN não encontrado. Configure o arquivo .env")
            return []
        
        query = self._load_query()
        all_repos = []
        cursor = None
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        self.output.print_fetch_start("HTTP API")
        
        for page in range(pages):
            variables = {"cursor": cursor} if cursor else {}
            
            response = requests.post(
                GITHUB_API_URL,
                json={"query": query, "variables": variables},
                headers=headers
            )
            
            if response.status_code != 200:
                self.output.print_error(f"Erro na API: {response.status_code}")
                print(f"Resposta: {response.text}")
                break
            
            data = response.json()
            
            if "errors" in data:
                self.output.print_error(f"Erros GraphQL: {data['errors']}")
                break
            
            search_results = data["data"]["search"]
            repos_this_page = []
            
            for edge in search_results["edges"]:
                repo = edge["node"]
                repo_data = {
                    "name": repo["name"],
                    "url": repo["url"],
                    "stargazerCount": repo["stargazerCount"],
                    "createdAt": repo["createdAt"],
                    "updatedAt": repo["updatedAt"],
                    "primaryLanguage": repo["primaryLanguage"]["name"] 
                        if repo["primaryLanguage"] else "Unknown",
                    "releases_count": repo["releases"]["totalCount"],
                    "pullRequests_count": repo["pullRequests"]["totalCount"],
                    "open_issues": repo["openIssues"]["totalCount"],
                    "closed_issues": repo["closedIssues"]["totalCount"]
                }
                standardized = self._standardize_repository(repo_data)
                repos_this_page.append(standardized)
                all_repos.append(standardized)
            
            self.output.print_page_progress(
                page + 1, pages, len(repos_this_page), len(all_repos)
            )
            
            if not search_results["pageInfo"]["hasNextPage"]:
                print("⚠️  Não há mais páginas disponíveis")
                break
            
            cursor = search_results["pageInfo"]["endCursor"]
        
        if save_json:
            self._save_json(all_repos)
        else:
            self.output.print_json_hint()
        
        return all_repos
    
    def _save_json(self, repos: List[Dict[str, Any]]) -> None:
        data_dir = pathlib.Path(__file__).parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        output_file = data_dir / "repos.json"
        
        repos_json = []
        for repo in repos:
            repos_json.append({
                "name": repo["name"],
                "stars": repo["stargazerCount"],
                "language": repo["primaryLanguage"],
                "url": repo["url"]
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(repos_json, f, indent=2)
        
        self.output.print_save_success(str(output_file))


def main(save_json: bool = False) -> None:
    try:
        fetcher = HttpRepositoryFetcher()
        repos = fetcher.fetch(pages=10, save_json=save_json)
        
        if not repos:
            RepositoryOutputFormatter.print_no_repos()
            return
        
        RepositoryOutputFormatter.print_repositories(repos)
        RepositoryOutputFormatter.print_summary(repos)
        RepositoryOutputFormatter.print_completion(len(repos))
        
    except Exception as e:
        RepositoryOutputFormatter.print_error(f"Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main(save_json=True)
