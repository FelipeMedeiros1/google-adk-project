# Google ADK Lab (GENAI104)

Este projeto documenta o passo a passo para executar o laboratorio
**Get Started with Agent Development Kit (ADK)** no Google Cloud/Qwiklabs.

## Objetivo

Neste lab, voce aprende a:

- Criar agentes com ADK.
- Usar Web UI, CLI e execucao programatica.
- Trabalhar com sessoes e Runner.
- Utilizar ferramentas como Google Search.
- Explorar uma arquitetura multi-agent.

## Pre-requisitos

- Conta Qwiklabs ativa.
- Acesso ao Google Cloud Console.
- Cloud Shell habilitado.

## Estrutura do Projeto

```text
google-adk-project/
+-- app_agent/
+-- my_google_search_agent/
+-- adk_project/
|   +-- app_agent/
|   +-- my_google_search_agent/
|   +-- adk_utils/
|   +-- llm_auditor/
|   +-- requirements.txt
+-- readme/
```

`my_google_search_agent` e o agente principal. Ele cria um `root_agent` usando
`google.adk.agents.Agent` e recebe a ferramenta `google_search`:

```python
tools=[google_search]
```

`app_agent` funciona como uma ponte para importar e expor o `root_agent` do
`my_google_search_agent`, ajudando o ADK a encontrar o agente corretamente.

## Fluxo Basico do Agente

O fluxo abaixo resume a trajetoria comum de uma interacao com agente no ADK:

```text
User Input
    |
    v
+---------+
|  Agent  |
+---------+
    |
    v
+------------------+
| Determine Intent |
+------------------+
    |
    v
+--------------+
|    Tools     |
| (Search/API) |
+--------------+
    |
    v
+----------------+
| Process Result |
+----------------+
    |
    v
Final Response
```

Esse fluxo tambem ajuda a entender a avaliacao de trajetoria, pois cada etapa
pode ser comparada com o comportamento esperado do agente.

## 1. Clonar o Projeto

No Cloud Shell:

```bash
cd ~
git clone https://github.com/Seu_Projeto/google-adk-project.git
cd google-adk-project/adk_project
```

Se o repositorio ja existir, atualize:

```bash
cd ~/google-adk-project
git pull
cd adk_project
```

## 2. Instalar Dependencias

```bash
export PATH=$PATH:"/home/${USER}/.local/bin"

python3 -m pip install google-adk[otel-gcp]==1.30.0
python3 -m pip install -r requirements.txt
```

## 3. Configurar Variaveis de Ambiente

```bash
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
export GOOGLE_CLOUD_LOCATION=global
export MODEL=gemini-3.5-flash
export ADK_TRACE_TO_CLOUD=1
```

O arquivo `.env` em `my_google_search_agent/` tambem pode ser usado pela UI e
pelo CLI do ADK.

Para habilitar tracing no Cloud Trace, adicione `ADK_TRACE_TO_CLOUD=1` ao
arquivo `.env`. Em materiais antigos do lab, essa variavel pode aparecer como
`AF_TRACE_TO_CLOUD=1`, mas a expectativa e migrar para `ADK_TRACE_TO_CLOUD=1`.

## 4. Executar a Web UI do ADK

Dentro de `google-adk-project/adk_project`, rode:

```bash
adk web \
  --allow_origins "regex:https://.*\.cloudshell\.dev" \
  --reload_agents
```

Abra o link gerado:

```text
http://127.0.0.1:8000
```

Na interface:

1. Selecione `my_google_search_agent`.
2. Clique em `New Session`.
3. Digite:

```text
What is the capital of France?
```

4. Aguarde a resposta.
5. Clique no icone do agente para inspecionar o evento.

Para parar a Web UI, volte ao terminal e pressione:

```text
CTRL + C
```

## 5. Execucao Programatica

A partir de `google-adk-project/adk_project`, execute:

```bash
PYTHONPATH=. python3 app_agent/agent.py
```

Saida esperada:

```text
User says: What is the capital of France?
The capital of France is Paris.
```

## 6. Executar o Agente via CLI

A partir de `google-adk-project/adk_project`, rode:

```bash
adk run my_google_search_agent
```

Depois, interaja com o agente:

```text
What are popular movies this year?
```

Para encerrar:

```text
exit
```

## 7. Rodar o LLM Auditor

Copie o `.env` para o agente auditor:

```bash
cp my_google_search_agent/.env llm_auditor/.env
```

Rode a interface novamente:

```bash
adk web \
  --allow_origins "regex:https://.*\.cloudshell\.dev" \
  --reload_agents
```

Na UI, selecione:

```text
llm_auditor
```

Teste com:

```text
Earth is further away from the Sun than Mars.
```

O sistema deve corrigir automaticamente a afirmacao.

## 8. Metodos de Avaliacao do ADK

O ADK fornece duas formas principais de avaliacao:

- `Using a test file`: cria arquivos de teste individuais, em que cada arquivo
  representa uma interacao simples entre agente e modelo dentro de uma sessao.
- `Using an evalset file`: usa um dataset dedicado chamado `evalset` para
  avaliar interacoes entre agente e modelo de forma mais organizada e
  reutilizavel.

Use arquivos de teste para cenarios pequenos e pontuais. Use `evalset` quando
quiser manter varios casos de avaliacao em um conjunto estruturado.

## 9. Aba Eval da Web UI

A aba `Eval` da ADK Dev UI permite criar e executar avaliacoes diretamente pela
interface web.

Nessa aba, voce pode:

- Criar um arquivo de conjunto de avaliacao (`eval set`).
- Salvar a sessao atual como um caso de avaliacao.
- Carregar sessoes salvas anteriormente e adiciona-las ao conjunto de avaliacao.
- Executar avaliacoes, por exemplo depois de alterar ou criar uma nova versao do
  agente.

Cada caso de avaliacao pode ter um ou mais turnos de conversa. Depois de rodar a
avaliacao, a UI mostra o resultado de cada caso, permitindo comparar o
comportamento do agente antes e depois de mudancas.

## 10. Como Rodar Avaliacoes

O ADK permite executar avaliacoes de tres formas principais:

- `Web UI (adk web)`: avalia agentes interativamente pela interface web.
- `Programmatically (pytest)`: integra avaliacoes ao pipeline de testes usando
  `pytest` e arquivos de teste.
- `Command Line Interface (adk eval)`: executa avaliacoes diretamente pelo
  terminal usando um arquivo de conjunto de avaliacao existente.

Exemplo programatico com `pytest`:

```python
from google.adk.evaluation.agent_evaluator import AgentEvaluator


def test_with_single_test_file():
    """Testa a habilidade basica do agente usando um arquivo de sessao."""
    AgentEvaluator.evaluate(
        "tests.integration.fixture.home_automation_agent",
        "tests/integration/fixture/home_automation_agent/simple_test.test.json",
    )
```

Nesse formato, o teste chama `AgentEvaluator.evaluate(...)`, informa o modulo do
agente e aponta para um arquivo `.test.json` que representa uma interacao de
avaliacao.

Exemplo pela linha de comando:

```bash
adk eval my_google_search_agent/__init__.py caminho/para/test.evalset.json
```

## 11. Avaliacao da Resposta Final

Na etapa de avaliacao, o ADK compara a resposta gerada pelo agente com uma
resposta de referencia definida no dataset de avaliacao.

A metrica `response_match_score` indica o quanto a resposta do agente corresponde
a resposta esperada. O teste passa quando o score atinge o valor minimo
configurado e falha quando fica abaixo desse limite.

## 12. Avaliacao de Trajetoria e Uso de Ferramentas

O ADK tambem pode avaliar a trajetoria executada pelo agente, comparando valores
esperados com valores reais das etapas realizadas durante a execucao.

Essa avaliacao pode verificar se o agente seguiu corretamente etapas como:

- `determine_intent`
- `use_tool`
- `review_results`
- `report_generation`

A metrica `tool_trajectory_avg_score` representa o quanto a trajetoria real do
agente corresponde a trajetoria esperada. O teste passa quando esse score atinge
o valor minimo configurado e falha quando fica abaixo desse limite.

Tipos comuns de avaliacao de trajetoria:

- `Exact match`: exige uma correspondencia perfeita com a trajetoria ideal.
- `In-order match`: exige as acoes corretas na ordem correta, permitindo acoes
  extras.
- `Any-order match`: exige as acoes corretas em qualquer ordem, permitindo
  acoes extras.
- `Precision`: mede a relevancia e a corretude das acoes previstas.
- `Recall`: mede quantas acoes essenciais foram capturadas na previsao.
- `Single-tool use`: verifica se uma acao ou ferramenta especifica foi usada.

## 13. Finalizacao

Depois de completar os passos:

1. Volte para o Qwiklabs.
2. Clique em `Check my progress`.

## Observacoes

- Cada pasta de agente precisa ter `__init__.py` e `agent.py`.
- O ADK procura um objeto chamado `root_agent` dentro de `agent.py`.
- Se ocorrer erro de importacao, confirme se voce esta executando o comando a
  partir da raiz correta do projeto.
- Para rodar dentro de `adk_project`, use `cd ~/google-adk-project/adk_project`.
- Para rodar a copia da raiz, use `cd ~/google-adk-project`.
