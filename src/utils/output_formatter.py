from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box


class RepositoryOutputFormatter:
    
    @staticmethod
    def _format_date_to_brazilian(date_str: str) -> str:
        """Convert ISO date string (YYYY-MM-DD) to Brazilian format (DD/MM/YYYY)"""
        try:
            date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            return date_str
    
    @staticmethod
    def print_repositories(repos: List[Dict[str, Any]]) -> None:
        console = Console()
        
        console.print(f"\n🎯 REPOSITÓRIOS COLETADOS - TOTAL: {len(repos)}", 
                     style="bold cyan")
        
        table = Table(title="Detalhes dos Repositórios", box=box.ROUNDED, 
                     show_lines=True, header_style="bold magenta")
        
        table.add_column("Nº", justify="center", style="dim")
        table.add_column("Nome", style="cyan", no_wrap=False, overflow="fold")
        table.add_column("URL", style="blue", no_wrap=False, overflow="fold")
        table.add_column("Stars", justify="right", style="yellow")
        table.add_column("Linguagem", justify="center", style="green")
        table.add_column("Criado", justify="center", style="dim")
        table.add_column("Atualizado", justify="center", style="dim")
        table.add_column("Releases", justify="right", style="magenta")
        table.add_column("PRs", justify="right", style="magenta")
        table.add_column("Issues Abertas", justify="right", style="red")
        table.add_column("Issues Fechadas", justify="right", style="green")
        
        for i, repo in enumerate(repos, 1):
            table.add_row(
                str(i),
                repo['name'],
                repo['url'],
                f"{repo['stargazerCount']:,}",
                repo['primaryLanguage'],
                RepositoryOutputFormatter._format_date_to_brazilian(repo['createdAt']),
                RepositoryOutputFormatter._format_date_to_brazilian(repo['updatedAt']),
                f"{repo['releases_count']:,}",
                f"{repo['pullRequests_count']:,}",
                f"{repo['open_issues']:,}",
                f"{repo['closed_issues']:,}"
            )
        
        console.print(table)
    
    @staticmethod
    def print_summary(repos: List[Dict[str, Any]]) -> None:
        console = Console()
        
        languages = {}
        for repo in repos:
            lang = repo['primaryLanguage']
            languages[lang] = languages.get(lang, 0) + 1
        
        lang_table = Table(title="🔤 Top 10 Linguagens", box=box.ROUNDED,
                          header_style="bold cyan")
        lang_table.add_column("Linguagem", style="green")
        lang_table.add_column("Repositórios", justify="right", style="magenta")
        
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]:
            lang_table.add_row(lang, str(count))
        
        console.print(lang_table)
        
        total_releases = sum(repo['releases_count'] for repo in repos)
        total_prs = sum(repo['pullRequests_count'] for repo in repos)
        total_open_issues = sum(repo['open_issues'] for repo in repos)
        total_closed_issues = sum(repo['closed_issues'] for repo in repos)
        
        stats_table = Table(title="📊 Totais Gerais", box=box.ROUNDED,
                           header_style="bold cyan")
        stats_table.add_column("Métrica", style="cyan")
        stats_table.add_column("Valor", justify="right", style="yellow")
        
        stats_table.add_row("Releases", f"{total_releases:,}")
        stats_table.add_row("Pull Requests aceitas", f"{total_prs:,}")
        stats_table.add_row("Issues abertas", f"{total_open_issues:,}")
        stats_table.add_row("Issues fechadas", f"{total_closed_issues:,}")
        stats_table.add_row("Total de issues", f"{total_open_issues + total_closed_issues:,}")
        
        console.print(stats_table)
    
    @staticmethod
    def print_page_progress(page: int, total_pages: int, repos_this_page: int, 
                           total_repos: int) -> None:
        console = Console()
        console.print(f"📄 Coletando página {page}/{total_pages}...", style="bold blue")
        console.print(f"✅ Coletados {repos_this_page} repositórios desta página", 
                     style="green")
        console.print(f"📊 Total acumulado: {total_repos} repositórios", 
                     style="cyan")
    
    @staticmethod
    def print_fetch_start(method: str) -> None:
        console = Console()
        console.print(f"🚀 Iniciando coleta de 100 repositórios (10 por vez)...", 
                     style="bold yellow")
        console.print(f"📡 Método: {method}", style="cyan")
    
    @staticmethod
    def print_no_repos() -> None:
        console = Console()
        console.print("❌ Nenhum repositório foi coletado!", style="bold red")
    
    @staticmethod
    def print_save_success(filepath: str) -> None:
        console = Console()
        console.print(f"\n✅ Dados salvos em {filepath}", style="bold green")
    
    @staticmethod
    def print_json_hint() -> None:
        console = Console()
        console.print("\nℹ️  Use --json para salvar os dados em JSON", style="cyan")
    
    @staticmethod
    def print_error(error: str) -> None:
        console = Console()
        console.print(f"❌ {error}", style="bold red")
    
    @staticmethod
    def print_completion(count: int) -> None:
        console = Console()
        console.print(f"\n🎉 Processo concluído! {count} repositórios processados.", 
                     style="bold green")
