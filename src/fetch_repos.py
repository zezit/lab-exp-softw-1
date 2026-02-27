import os
import pathlib
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com/graphql"

def load_query():
    """Carrega a query GraphQL do arquivo."""
    query_path = pathlib.Path(__file__).parent / "query.graphql"
    with open(query_path, 'r') as f:
        return f.read()

def fetch_repositories():
    """Busca 100 repositórios usando a query paginada (10 em 10)."""
    
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN não encontrado. Configure o arquivo .env")
        return []
    
    query = load_query()
    all_repos = []
    cursor = None
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Iniciando coleta de 100 repositórios (10 por vez)...")
    
    for page in range(10):
        print(f"\n📄 Coletando página {page + 1}/10...")
        
        variables = {"cursor": cursor} if cursor else {}
        
        response = requests.post(
            GITHUB_API_URL,
            json={"query": query, "variables": variables},
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            break
        
        data = response.json()
        
        if "errors" in data:
            print(f"❌ Erros GraphQL: {data['errors']}")
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
                "primaryLanguage": repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else "Unknown",
                "releases_count": repo["releases"]["totalCount"],
                "pullRequests_count": repo["pullRequests"]["totalCount"],
                "open_issues": repo["openIssues"]["totalCount"],
                "closed_issues": repo["closedIssues"]["totalCount"]
            }
            repos_this_page.append(repo_data)
            all_repos.append(repo_data)
        
        print(f"✅ Coletados {len(repos_this_page)} repositórios desta página")
        print(f"📊 Total acumulado: {len(all_repos)} repositórios")
        
        if not search_results["pageInfo"]["hasNextPage"]:
            print("⚠️  Não há mais páginas disponíveis")
            break
            
        cursor = search_results["pageInfo"]["endCursor"]
    
    return all_repos

def print_repositories(repos):
    """Printa os repositórios no terminal conforme solicitado."""
    
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

def print_summary(repos):
    """Printa um resumo estatístico."""
    
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

def main() -> None:
    """Ponto de entrada - coleta e printa os 100 repositórios."""
    
    try:
        repos = fetch_repositories()
        
        if not repos:
            print("❌ Nenhum repositório foi coletado!")
            return
        
        print_repositories(repos)
        
        print_summary(repos)
        
        print(f"\n🎉 Processo concluído! {len(repos)} repositórios processados.")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()