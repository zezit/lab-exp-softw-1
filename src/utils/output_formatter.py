from typing import List, Dict, Any


class RepositoryOutputFormatter:
    
    @staticmethod
    def print_repositories(repos: List[Dict[str, Any]]) -> None:
        print(f"\n" + "="*80)
        print(f"🎯 REPOSITÓRIOS COLETADOS - TOTAL: {len(repos)}")
        print(f"="*80)
        
        for i, repo in enumerate(repos, 1):
            print(f"\n{i:3d}. {repo['name']}")
            print(f"     URL: {repo['url']}")
            print(f"     Stars: {repo['stargazerCount']:,}")
            print(f"     Linguagem: {repo['primaryLanguage']}")
            print(f"     Criado em: {repo['createdAt'][:10]}")
            print(f"     Última atualização: {repo['updatedAt'][:10]}")
            print(f"     Releases: {repo['releases_count']:,}")
            print(f"     Pull Requests aceitas: {repo['pullRequests_count']:,}")
            print(f"     Issues abertas: {repo['open_issues']:,}")
            print(f"     Issues fechadas: {repo['closed_issues']:,}")
            
            if i % 10 == 0 and i < len(repos):
                print(f"\n{'-'*50} [{i} de {len(repos)}] {'-'*50}")
    
    @staticmethod
    def print_summary(repos: List[Dict[str, Any]]) -> None:
        print(f"\n" + "="*80)
        print(f"📈 RESUMO ESTATÍSTICO")
        print(f"="*80)
        
        languages = {}
        for repo in repos:
            lang = repo['primaryLanguage']
            languages[lang] = languages.get(lang, 0) + 1
        
        print(f"\n🔤 Top 10 Linguagens:")
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {lang}: {count} repositórios")
        
        total_releases = sum(repo['releases_count'] for repo in repos)
        total_prs = sum(repo['pullRequests_count'] for repo in repos)
        total_open_issues = sum(repo['open_issues'] for repo in repos)
        total_closed_issues = sum(repo['closed_issues'] for repo in repos)
        
        print(f"\n📊 Totais Gerais:")
        print(f"   Releases: {total_releases:,}")
        print(f"   Pull Requests aceitas: {total_prs:,}")
        print(f"   Issues abertas: {total_open_issues:,}")
        print(f"   Issues fechadas: {total_closed_issues:,}")
        print(f"   Total de issues: {total_open_issues + total_closed_issues:,}")
    
    @staticmethod
    def print_page_progress(page: int, total_pages: int, repos_this_page: int, 
                           total_repos: int) -> None:
        print(f"\n📄 Coletando página {page}/{total_pages}...")
        print(f"✅ Coletados {repos_this_page} repositórios desta página")
        print(f"📊 Total acumulado: {total_repos} repositórios")
    
    @staticmethod
    def print_fetch_start(method: str) -> None:
        print(f"🚀 Iniciando coleta de 100 repositórios (10 por vez)...")
        print(f"📡 Método: {method}")
    
    @staticmethod
    def print_no_repos() -> None:
        print("❌ Nenhum repositório foi coletado!")
    
    @staticmethod
    def print_save_success(filepath: str) -> None:
        print(f"\n✅ Dados salvos em {filepath}")
    
    @staticmethod
    def print_json_hint() -> None:
        print("\nℹ️  Use --json para salvar os dados em JSON")
    
    @staticmethod
    def print_error(error: str) -> None:
        print(f"❌ {error}")
    
    @staticmethod
    def print_completion(count: int) -> None:
        print(f"\n🎉 Processo concluído! {count} repositórios processados.")
