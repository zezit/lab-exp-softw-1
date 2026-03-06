from typing import List, Dict, Any
from ..interfaces.repository_fetcher import RepositoryFetcher
from ..utils.output_formatter import RepositoryOutputFormatter

class RepositoryManager:
    def __init__(self, fetcher: RepositoryFetcher):
        self.fetcher = fetcher
        self.output = RepositoryOutputFormatter()
    
    def fetch_repositories(self, pages: int = 10, save_json: bool = False, save_csv: bool = False) -> List[Dict[str, Any]]:
        return self.fetcher.fetch(pages=pages, save_json=save_json, save_csv=save_csv)
    
    def display_results(self, repos: List[Dict[str, Any]]) -> None:
        if not repos:
            self.output.print_no_repos()
            return
        
        self.output.print_repositories(repos)
        self.output.print_summary(repos)
        self.output.print_completion(len(repos))