from typing import List, Dict, Any, Literal, cast
from .interfaces.repository_fetcher import RepositoryFetcher
from .repository_fetcher_http import HttpRepositoryFetcher
from .repository_fetcher_cli import CliRepositoryFetcher
from .utils.output_formatter import RepositoryOutputFormatter


class RepositoryManager:
    FETCHERS = {
        'http': HttpRepositoryFetcher,
        'cli': CliRepositoryFetcher,
    }
    
    def __init__(self, method: Literal['http', 'cli'] = 'http'):
        if method not in self.FETCHERS:
            raise ValueError(f"Unsupported method: {method}. Choose from: {list(self.FETCHERS.keys())}")
        
        self.method = method
        self.fetcher = self.FETCHERS[method]()
        self.output = RepositoryOutputFormatter()
    
    def fetch_repositories(self, pages: int = 10, save_json: bool = False) -> List[Dict[str, Any]]:
        return self.fetcher.fetch(pages=pages, save_json=save_json)
    
    def display_results(self, repos: List[Dict[str, Any]]) -> None:
        if not repos:
            self.output.print_no_repos()
            return
        
        self.output.print_repositories(repos)
        self.output.print_summary(repos)
        self.output.print_completion(len(repos))

def main(method: str = 'http', save_json: bool = False) -> None:
    try:
        if method not in RepositoryManager.FETCHERS:
            raise ValueError(f"Unsupported method: {method}. Choose from: {list(RepositoryManager.FETCHERS.keys())}")
        
        method_literal = cast(Literal['http', 'cli'], method)
        manager = RepositoryManager(method=method_literal)
        repos = manager.fetch_repositories(pages=10, save_json=save_json)
        manager.display_results(repos)
        
    except ValueError as e:
        RepositoryOutputFormatter.print_error(str(e))
    except Exception as e:
        RepositoryOutputFormatter.print_error(f"Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    method = sys.argv[1] if len(sys.argv) > 1 else 'http'
    save_json = '--json' in sys.argv
    
    main(method=method, save_json=save_json)
