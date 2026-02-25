# collect_with_cli.py
import subprocess
import json
import time

def run_gh_query(cursor):
    cmd = [
        'gh', 'api', 'graphql',
        '--field', f'query={open("query.graphql").read()}',
        '--field', f'cursor={cursor}'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def main():
    cursor = "null"
    all_repos = []
    
    for page in range(1, 11):  # 10 páginas x 10 = 100 repos
        print(f"\n=== Página {page} ===")
        
        data = run_gh_query(cursor)
        repos = data['data']['search']['edges']
        
        for repo in repos:
            node = repo['node']
            all_repos.append({
                'name': node['name'],
                'stars': node['stargazerCount'],
                'language': node['primaryLanguage']['name'] if node['primaryLanguage'] else 'N/A',
                'url': node['url']
            })
            print(f"{len(all_repos):3d}. {node['name']} - {node['stargazerCount']:,} stars")
        
        # Próxima página
        page_info = data['data']['search']['pageInfo']
        if not page_info['hasNextPage']:
            break
        cursor = page_info['endCursor']
        time.sleep(1)
    
    print(f"\nTotal: {len(all_repos)} repositórios coletados!")
    
    # Salvar em arquivo
    with open('../data/repos.json', 'w') as f:
        json.dump(all_repos, f, indent=2)
    print("Dados salvos em ../data/repos.json")

if __name__ == "__main__":
    main()