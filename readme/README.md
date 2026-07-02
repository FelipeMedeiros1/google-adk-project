# Google ADK Lab (GENAI104)

Este projeto documenta o passo a passo para executar o laboratório
**Get Started with Agent Development Kit (ADK)** no Google Cloud/Qwiklabs.

## Objetivo

Neste laboratório, você aprende a:

- Criar agentes com o ADK.
- Usar a Web UI, a CLI e a execução programática.
- Trabalhar com sessões e `Runner`.
- Utilizar ferramentas como o Google Search.
- Explorar uma arquitetura multiagente.

## Pré-requisitos

- Conta Qwiklabs ativa.
- Acesso ao Google Cloud Console.
- Cloud Shell habilitado.
- Navegador Chrome ou janela anônima/privada para evitar conflito com contas pessoais do Google Cloud.

## Estrutura do Projeto

```text
google-adk-project/
+-- adk_project/
|   +-- adk_utils/
|   +-- app_agent/
|   +-- llm_auditor/
|   +-- my_google_search_agent/
|   +-- requirements.txt
+-- app_agent/
+-- llm_auditor/
+-- my_google_search_agent/
+-- readme/
```

O laboratório trabalha principalmente dentro de `adk_project/`. As pastas de agente na raiz são cópias auxiliares do mesmo código.

`my_google_search_agent` é o agente principal. Ele cria um `root_agent` usando `google.adk.agents.Agent` e recebe a ferramenta `google_search`:

```python
tools=[google_search]
```

`app_agent` executa o `root_agent` programaticamente usando `InMemoryRunner`.

## Fluxo Básico do Agente

O fluxo abaixo resume a trajetória comum de uma interação com um agente no ADK:

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

Esse fluxo também ajuda a entender a avaliação de trajetória, pois cada etapa pode ser comparada com o comportamento esperado do agente.

## 1. Obter o Código do Laboratório

No Cloud Shell, copie os arquivos fornecidos pelo Qwiklabs para o diretório inicial:

```bash
cd ~
gcloud storage cp -r gs://SEU_BUCKET_DO_LAB/* .
cd adk_project
```

Substitua `SEU_BUCKET_DO_LAB` pelo bucket exibido nas instruções do seu laboratório. Não salve credenciais temporárias do Qwiklabs no repositório.

Se estiver usando este repositório em vez do bucket do laboratório:

```bash
cd ~
git clone https://github.com/Seu_Projeto/google-adk-project.git
cd google-adk-project/adk_project
```

Se o repositório já existir, atualize:

```bash
cd ~/google-adk-project
git pull
cd adk_project
```

## 2. Instalar Dependências

```bash
export PATH=$PATH:"/home/${USER}/.local/bin"

python3 -m pip install google-adk[otel-gcp]==1.30.0 -r requirements.txt
```

## 3. Configurar Variáveis de Ambiente

Para uso no terminal atual:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
export GOOGLE_CLOUD_LOCATION=global
export MODEL=gemini-3.5-flash
```

Para a Web UI e a CLI do ADK, crie um arquivo `.env` dentro do diretório do agente:

```bash
cat << EOF > my_google_search_agent/.env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
GOOGLE_CLOUD_LOCATION=global
MODEL=gemini-3.5-flash
OTEL_SERVICE_NAME=adk-agent
OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
EOF
```

Essas variáveis indicam que o agente deve usar o Vertex AI, associam as chamadas ao projeto do laboratório e configuram telemetria para o OpenTelemetry quando a Web UI for executada com `--otel_to_cloud`.

## 4. Executar a Web UI do ADK

Dentro de `google-adk-project/adk_project`, rode:

```bash
adk web \
  --allow_origins "regex:https://.*\.cloudshell\.dev" \
  --otel_to_cloud \
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
I know the Summer Olympics are happening in 2028, please tell me which countries are participating and what events will be held.
```

4. Aguarde a resposta.
5. Clique no ícone do agente para inspecionar o evento e os metadados de grounding.

Para parar a Web UI, volte ao terminal e pressione:

```text
CTRL + C
```

## 5. Execução Programática

A partir de `google-adk-project/adk_project`, execute:

```bash
python3 app_agent/agent.py
```

Saída esperada:

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
What are some popular movies that have been released in India this year?
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
  --otel_to_cloud \
  --reload_agents
```

Se a porta `8000` ainda estiver ocupada, use outra porta:

```bash
adk web --port 8001
```

Na UI, selecione:

```text
llm_auditor
```

Teste com:

```text
Double check this: Earth is further away from the Sun than Mars.
```

O sistema deve corrigir automaticamente a afirmação.

## 8. Métodos de Avaliação do ADK

O ADK fornece formas de avaliação para verificar a resposta final e a trajetória executada pelo agente.

- `Using a test file`: cria arquivos de teste individuais, em que cada arquivo representa uma interação simples entre agente e modelo dentro de uma sessão.
- `Using an evalset file`: usa um conjunto de avaliação dedicado para avaliar interações entre agente e modelo de forma mais organizada e reutilizável.

Use arquivos de teste para cenários pequenos e pontuais. Use `evalset` quando quiser manter vários casos de avaliação em um conjunto estruturado.

## 9. Aba Eval da Web UI

A aba `Eval` da ADK Dev UI permite criar e executar avaliações diretamente pela interface web.

Nessa aba, você pode:

- Criar um conjunto de avaliação.
- Salvar a sessão atual como um caso de avaliação.
- Carregar sessões salvas anteriormente e adicioná-las ao conjunto de avaliação.
- Executar avaliações depois de alterar ou criar uma nova versão do agente.

Cada caso de avaliação pode ter um ou mais turnos de conversa. Depois de rodar a avaliação, a UI mostra o resultado de cada caso, permitindo comparar o comportamento do agente antes e depois de mudanças.

## 10. Como Rodar Avaliações

O ADK permite executar avaliações de três formas principais:

- `Web UI (adk web)`: avalia agentes interativamente pela interface web.
- `Programmatically (pytest)`: integra avaliações ao pipeline de testes usando `pytest` e arquivos de teste.
- `Command Line Interface (adk eval)`: executa avaliações diretamente pelo terminal usando um conjunto de avaliação existente.

Exemplo programático com `pytest`:

```python
from google.adk.evaluation.agent_evaluator import AgentEvaluator


def test_with_single_test_file():
    """Testa a habilidade básica do agente usando um arquivo de sessão."""
    AgentEvaluator.evaluate(
        "tests.integration.fixture.home_automation_agent",
        "tests/integration/fixture/home_automation_agent/simple_test.test.json",
    )
```

Exemplo pela linha de comando:

```bash
adk eval my_google_search_agent caminho/para/test.evalset.json
```

## 11. Avaliação da Resposta Final

Na etapa de avaliação, o ADK compara a resposta gerada pelo agente com uma resposta de referência definida no conjunto de avaliação.

A métrica `response_match_score` indica o quanto a resposta do agente corresponde à resposta esperada. O teste passa quando o score atinge o valor mínimo configurado e falha quando fica abaixo desse limite.

## 12. Avaliação de Trajetória e Uso de Ferramentas

O ADK também pode avaliar a trajetória executada pelo agente, comparando valores esperados com valores reais das etapas realizadas durante a execução.

Essa avaliação pode verificar se o agente seguiu corretamente etapas como:

- `determine_intent`
- `use_tool`
- `review_results`
- `report_generation`

A métrica `tool_trajectory_avg_score` representa o quanto a trajetória real do agente corresponde à trajetória esperada. O teste passa quando esse score atinge o valor mínimo configurado e falha quando fica abaixo desse limite.

Tipos comuns de avaliação de trajetória:

- `Exact match`: exige uma correspondência perfeita com a trajetória ideal.
- `In-order match`: exige as ações corretas na ordem correta, permitindo ações extras.
- `Any-order match`: exige as ações corretas em qualquer ordem, permitindo ações extras.
- `Precision`: mede a relevância e a correção das ações previstas.
- `Recall`: mede quantas ações essenciais foram capturadas na previsão.
- `Single-tool use`: verifica se uma ação ou ferramenta específica foi usada.

## 13. Finalização

Depois de completar os passos:

1. Volte para o Qwiklabs.
2. Clique em `Check my progress`.

## Observações

- Cada pasta de agente precisa ter `__init__.py` e `agent.py`.
- O ADK procura um objeto chamado `root_agent` dentro de `agent.py`.
- Se ocorrer erro de importação, confirme se você está executando o comando a partir da raiz correta do projeto.
- Para rodar dentro de `adk_project`, use `cd ~/google-adk-project/adk_project`.
- Se usar as cópias da raiz, execute os comandos a partir de `~/google-adk-project`.
