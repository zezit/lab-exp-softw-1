from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class RepositoryFetcher(ABC):
    
    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch repositories and return standardized data.
        
        Returns:
            List of repository dictionaries with standardized keys:
            - name: str
            - url: str
            - stargazerCount: int
            - createdAt: str (ISO format)
            - updatedAt: str (ISO format)
            - primaryLanguage: str
            - releases_count: int
            - pullRequests_count: int
            - open_issues: int
            - closed_issues: int
        """
        pass
    
    def _standardize_repository(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure all required fields are present in standardized format.
        
        Args:
            repo: Repository data dictionary
            
        Returns:
            Standardized repository dictionary
        """
        return {
            "name": repo.get("name", "Unknown"),
            "url": repo.get("url", ""),
            "stargazerCount": repo.get("stargazerCount", 0),
            "createdAt": repo.get("createdAt", ""),
            "updatedAt": repo.get("updatedAt", ""),
            "primaryLanguage": repo.get("primaryLanguage", "Unknown"),
            "releases_count": repo.get("releases_count", 0),
            "pullRequests_count": repo.get("pullRequests_count", 0),
            "open_issues": repo.get("open_issues", 0),
            "closed_issues": repo.get("closed_issues", 0),
        }
