import sys
from src import collect_with_cli
from src import fetch_repos

def display_menu():
    print("=" * 60)
    print(" 🚀 LABORATÓRIO 01 - COLETOR DE REPOSITÓRIOS GITHUB ")
    print("=" * 60)
    print("\nEscolha qual método você deseja utilizar para a coleta:\n")
    print("  [1] 🐙 GitHub CLI (gh)")
    print("      Requer o GitHub CLI instalado e autenticado na máquina.")
    print("\n  [2] 🌐 Requisição Direta à API (Requests)")
    print("      Requer um GITHUB_TOKEN configurado no arquivo .env.")
    print("\n  [0] Sair")
    print("-" * 60)

def main():
    while True:
        display_menu()
        choice = input("\n👉 Digite o número da opção desejada: ").strip()

        if choice == '1':
            print("\n" + "=" * 40)
            print("Iniciando coleta via GitHub CLI...")
            print("=" * 40 + "\n")
            collect_with_cli.main()
            break
            
        elif choice == '2':
            print("\n" + "=" * 40)
            print("Iniciando coleta via Requisição Direta (API)...")
            print("=" * 40 + "\n")
            fetch_repos.main()
            break
            
        elif choice == '0':
            print("\n👋 Encerrando o programa. Até logo!")
            sys.exit(0)
            
        else:
            print("\n❌ Opção inválida! Por favor, digite 1, 2 ou 0.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Execução interrompida pelo usuário. Saindo...")
        sys.exit(0)