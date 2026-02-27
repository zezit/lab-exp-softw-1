# LAB01 — Características de Repositórios Populares

**Disciplina:** Laboratório de Experimentação de Software  
**Curso:** Engenharia de Software  
**Professor:** Danilo de Quadros Maia Filho  
**Valor:** 15 pontos

---
## Integrantes

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/moraisjo">
        <img src="https://avatars.githubusercontent.com/u/92741380?v=4" width="100px;" alt="Joana Morais"/><br />
        <sub><b>Joana Morais</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/JoaoYM">
        <img src="https://avatars.githubusercontent.com/u/93276158?v=4" width="100px;" alt="João Pedro Aguiar"/><br />
        <sub><b>João Pedro Aguiar</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/zezit">
        <img src="https://avatars.githubusercontent.com/u/95448020?v=4" width="100px;" alt="José Dias"/><br />
        <sub><b>José Dias</b></sub>
      </a>
    </td>
  </tr>
</table>

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [docs/uso-query-graphql.md](docs/uso-query-graphql.md) | Como executar a query GraphQL via `gh` CLI ou requisição HTTP |

---

## Descrição

Este laboratório tem como objetivo estudar as principais características de sistemas populares open-source hospedados no GitHub. Por meio da API GraphQL do GitHub, serão coletados dados dos **1.000 repositórios com maior número de estrelas** para responder às seguintes questões de pesquisa:

| # | Questão de Pesquisa | Métrica |
|---|---|---|
| RQ01 | Sistemas populares são maduros/antigos? | Idade do repositório (data de criação) |
| RQ02 | Sistemas populares recebem muita contribuição externa? | Total de pull requests aceitas |
| RQ03 | Sistemas populares lançam releases com frequência? | Total de releases |
| RQ04 | Sistemas populares são atualizados com frequência? | Tempo desde a última atualização |
| RQ05 | Sistemas populares são escritos nas linguagens mais populares? | Linguagem primária do repositório |
| RQ06 | Sistemas populares possuem um alto percentual de issues fechadas? | Razão entre issues fechadas e total de issues |
| RQ07 *(bônus)* | Sistemas escritos em linguagens mais populares recebem mais contribuição, lançam mais releases e são mais atualizados? | RQ02, RQ03 e RQ04 segmentados por linguagem |

---

## Entregas

### Lab01S01 — Consulta GraphQL + Requisição Automática *(3 pontos)*
- Query GraphQL para buscar 100 repositórios com todos os campos necessários para as RQs.
- Script Python que realiza a requisição à API do GitHub e exibe os dados coletados.

### Lab01S02 — Paginação + CSV + Primeira Versão do Relatório *(3 pontos)*
- Paginação para coletar os 1.000 repositórios.
- Exportação dos dados para arquivo `.csv`.
- Primeira versão do relatório com hipóteses informais.

### Lab01S03 — Análise, Visualização e Relatório Final *(9 pontos)*
- Análise estatística (valores medianos, contagens por categoria).
- Geração de gráficos e visualizações.
- Relatório final com introdução, metodologia, resultados e discussão.

---

## Configuração do Ambiente

### Pré-requisitos Gerais

- **Python 3.10+**
- **Git**

O projeto possui dois métodos de coleta diferentes. Dependendo da sua escolha, você precisará de:
* **Para o Método 1:** [GitHub CLI (`gh`)](https://cli.github.com/) instalado na máquina.
* **Para o Método 2:** Um Personal Access Token (PAT) do GitHub (Classic) com permissão de leitura pública.

### Instalação e Preparação

```bash
# 1. Clone o repositório
git clone <url-do-repositório>
cd <nome-do-repositório>

# 2. Crie e ative um ambiente virtual
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 3. Instale as dependências do projeto (requests, python-dotenv, etc.)
pip install -r requirements.txt

```

---

## Como Executar

Para facilitar o uso, centralizamos a execução no arquivo `app.py`. A partir dele, um menu interativo permitirá escolher qual método de coleta você deseja utilizar.

No terminal (com o ambiente virtual ativado), na raiz do projeto, execute:

```bash
python app.py

```

### Configurações Específicas por Método

Antes de escolher a opção no menu, certifique-se de ter configurado o método desejado:

#### Opção 1: GitHub CLI (`gh`)

Este método utiliza sub-processos do Python para chamar comandos do GitHub CLI local.

* **Requisito:** É obrigatório ter o GitHub CLI instalado na sua máquina.
* **Autenticação:** Antes de rodar, abra o terminal e faça login digitando:
```bash
gh auth login

```


*(Siga os passos na tela para se autenticar pelo navegador).*

#### Opção 2: Requisição Direta à API (Requests) - *Recomendado*

Este método faz chamadas HTTP diretas pelo Python, dispensando a instalação do GitHub CLI.

* **Requisito:** Necessita de um token de acesso pessoal do GitHub e da biblioteca `python-dotenv`.
* **Autenticação:**
1. Crie uma cópia do arquivo `.env.example` e renomeie para `.env`:
```bash
cp .env.example .env

```


2. Abra o arquivo `.env` e adicione o seu token (sem aspas ou espaços):
```text
GITHUB_TOKEN=seu_token_aqui_ghp_xxxxxxxxxxxxxxxxx

```