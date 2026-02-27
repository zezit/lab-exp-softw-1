import subprocess
import json
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
QUERY_FILE = SCRIPT_DIR / "query.graphql"
DATA_DIR = SCRIPT_DIR.parent / "data"

def run_gh_query(cursor):
    query_content = QUERY_FILE.read_text(encoding="utf-8")
    
    cmd = [
        'gh', 'api', 'graphql',
        '--field', f'query={query_content}',
        '--field', f'cursor={cursor}'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def main(save_json=False):
    if not QUERY_FILE.exists():
        print(f"❌ Erro: O arquivo não foi encontrado em {QUERY_FILE}")
        return

    cursor = "null"
    all_repos = []
    
    for page in range(1, 11):
        print(f"\n=== Página {page} ===")
        
        data = run_gh_query(cursor)
        
        if 'data' not in data:
            print("❌ Erro na resposta da API:", data)
            break
            
        repos = data['data']['search']['edges']
        
        for repo in repos:
            node = repo['node']
            all_repos.append({
                'name': node['name'],
                'stars': node['stargazerCount'],
                'language': node['primaryLanguage']['name'] if node.get('primaryLanguage') else 'N/A',
                'url': node['url']
            })
            print(f"{len(all_repos):3d}. {node['name']} - {node['stargazerCount']:,} stars")
        
        page_info = data['data']['search']['pageInfo']
        if not page_info['hasNextPage']:
            break
        cursor = page_info['endCursor']
        time.sleep(1)
    
    print(f"\nTotal: {len(all_repos)} repositórios coletados!")
    
    if save_json:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        output_file = DATA_DIR / 'repos.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_repos, f, indent=2)
        print(f"✅ Dados salvos em {output_file}")
    else:
        print("ℹ️  Use --json para salvar os dados em JSON")

if __name__ == "__main__":
    main()