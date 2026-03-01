import sys
from src.services.fetcher_factory import RepositoryFetcherFactory
from src.services.repository_manager import RepositoryManager
from src.utils.output_formatter import RepositoryOutputFormatter

def display_menu(options: list):
    print("=" * 60)
    print(" 🚀 LABORATÓRIO 01 - COLETOR DE REPOSITÓRIOS GITHUB ")
    print("=" * 60)
    print("\nEscolha o método de coleta:")
    
    # Geramos o menu dinamicamente com base na Factory
    for i, method in enumerate(options, 1):
        label = "🐙 GitHub CLI (gh)" if method == 'cli' else "🌐 Requisição Direta (API)"
        print(f"  [{i}] {label}")
    
    print("\n  [0] Sair")
    print("-" * 60)

def run_collection(method: str, save_json: bool):
    """Encapsula a execução para limpar o loop principal"""
    try:
        print("\n" + "=" * 40)
        print(f"Iniciando coleta via {method.upper()}...")
        print("=" * 40 + "\n")
        
        # Uso da Factory + Manager conforme o novo padrão SOLID
        fetcher = RepositoryFetcherFactory.create(method)
        manager = RepositoryManager(fetcher)
        
        repos = manager.fetch_repositories(pages=10, save_json=save_json)
        manager.display_results(repos)
        
    except Exception as e:
        RepositoryOutputFormatter.print_error(f"Erro na execução: {e}")

def main(save_json=False):
    # Obtemos os métodos disponíveis na Factory (OCP na prática!)
    available_methods = RepositoryFetcherFactory.get_available_methods()
    
    while True:
        display_menu(available_methods)
        choice = input("\n👉 Digite a opção: ").strip()

        if choice == '0':
            print("\n👋 Encerrando. Até logo!")
            break
            
        if choice.isdigit() and 1 <= int(choice) <= len(available_methods):
            selected_method = available_methods[int(choice) - 1]
            run_collection(selected_method, save_json)
            break # Ou remova o break para permitir múltiplas coletas
        else:
            print(f"\n❌ Opção inválida! Digite de 1 a {len(available_methods)} ou 0.")

if __name__ == "__main__":
    should_save = "--json" in sys.argv
    try:
        main(save_json=should_save)
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário. Saindo...")
        sys.exit(0)