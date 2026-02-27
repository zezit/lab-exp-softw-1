import subprocess
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from .interfaces.repository_fetcher import RepositoryFetcher
from .utils.output_formatter import RepositoryOutputFormatter

SCRIPT_DIR = Path(__file__).parent
QUERY_FILE = SCRIPT_DIR / "query.graphql"
DATA_DIR = SCRIPT_DIR.parent / "data"


class CliRepositoryFetcher(RepositoryFetcher):
    
    def __init__(self):
        self.output = RepositoryOutputFormatter()
    
    def fetch(self, pages: int = 10, save_json: bool = False) -> List[Dict[str, Any]]:
        if not QUERY_FILE.exists():
            self.output.print_error(f"O arquivo não foi encontrado em {QUERY_FILE}")
            return []
        
        cursor = "null"
        all_repos = []
        
        self.output.print_fetch_start("GitHub CLI")
        
        for page in range(1, pages + 1):
            data = self._run_gh_query(cursor)
            
            if 'data' not in data:
                self.output.print_error(f"Erro na resposta da API: {data}")
                break
            
            repos_this_page = []
            for repo_edge in data['data']['search']['edges']:
                node = repo_edge['node']
                repo_data = {
                    "name": node['name'],
                    "url": node['url'],
                    "stargazerCount": node['stargazerCount'],
                    "createdAt": node.get('createdAt', ''),
                    "updatedAt": node.get('updatedAt', ''),
                    "primaryLanguage": (node.get('primaryLanguage') or {}).get('name', 'Unknown'),
                    "releases_count": node.get('releases', {}).get('totalCount', 0),
                    "pullRequests_count": node.get('pullRequests', {}).get('totalCount', 0),
                    "open_issues": node.get('openIssues', {}).get('totalCount', 0),
                    "closed_issues": node.get('closedIssues', {}).get('totalCount', 0)
                }
                standardized = self._standardize_repository(repo_data)
                repos_this_page.append(standardized)
                all_repos.append(standardized)
            
            self.output.print_page_progress(page, pages, len(repos_this_page), len(all_repos))
            
            page_info = data['data']['search']['pageInfo']
            if not page_info['hasNextPage']:
                print("⚠️  Não há mais páginas disponíveis")
                break
            
            cursor = page_info['endCursor']
            time.sleep(1)  # Rate limiting
        
        if save_json:
            self._save_json(all_repos)
        else:
            self.output.print_json_hint()
        
        return all_repos
    
    def _run_gh_query(self, cursor: str) -> Dict[str, Any]:
        query_content = QUERY_FILE.read_text(encoding="utf-8")
        
        cmd = [
            'gh', 'api', 'graphql',
            '--field', f'query={query_content}',
            '--field', f'cursor={cursor}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    
    def _save_json(self, repos: List[Dict[str, Any]]) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        output_file = DATA_DIR / 'repos.json'
        
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
        fetcher = CliRepositoryFetcher()
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
