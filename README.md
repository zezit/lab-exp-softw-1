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

### Pré-requisitos

- Python 3.10+
- Token de acesso pessoal do GitHub (com permissão de leitura pública)

### Instalação

```bash
# Clone o repositório
git clone <url-do-repositório>
cd <nome-do-repositório>

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env e adicione seu token do GitHub
```
