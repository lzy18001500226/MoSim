# OpenTelemetry로 실행 검사하기[[inspecting-runs-with-opentelemetry]]

[[open-in-colab]]

> [!TIP]
> 에이전트 구축이 처음이라면 먼저 [에이전트 소개](../conceptual_guides/intro_agents)와 [안내서](../guided_tour)를 읽어보세요.

## 에이전트 실행을 로깅하는 이유는?[[why-log-your-agent-runs?]]

에이전트 실행을 디버깅하는 것은 복잡한 작업입니다.

실행이 제대로 진행되었는지 확인하기 어렵습니다. 에이전트 워크플로우는 설계상 예측 불가능하기 때문입니다(만약 예측 가능했다면 일반적인 코드를 사용했을 것입니다).

실행 과정을 살펴보는 것도 쉽지 않습니다. 다단계 에이전트는 콘솔을 로그로 빠르게 채우는 경향이 있으며, 대부분의 오류는 단순한 "LLM의 실수" 유형으로, LLM이 다음 단계에서 더 나은 코드나 도구 호출을 작성하여 스스로 교정합니다.

따라서 나중에 검사하고 모니터링할 수 있도록 계측을 통해 에이전트 실행을 기록하는 것이 프로덕션 환경에서는 필수입니다!

에이전트 실행을 계측하기 위해 [OpenTelemetry](https://opentelemetry.io/) 표준을 도입했습니다.

즉, 계측 코드를 실행한 후 에이전트를 평소처럼 실행하면 모든 내용이 플랫폼에 자동으로 로깅됩니다. 다양한 OpenTelemetry 백엔드에서 이를 구현하는 방법의 예시를 아래에 제시합니다.

플랫폼에서의 실제 모습은 다음과 같습니다.

<div class="flex justify-center">
    <img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/smolagents/inspect_run_phoenix.gif"/>
</div>

## Arize AI Phoenix로 텔레메트리 설정[[setting-up-telemetry-with-arize-ai-phoenix]]

먼저 필요한 패키지를 설치합니다. 여기서는 로그를 수집하고 검사하기에 좋은 솔루션인 [Arize AI의 Phoenix](https://github.com/Arize-ai/phoenix)를 설치하지만, 이 과정에는 다른 OpenTelemetry 호환 플랫폼을 활용할 수도 있습니다.

```shell
pip install 'smolagents[telemetry,toolkit]'
```

다음 단계로 수집기를 백그라운드에서 실행합니다.

```shell
python -m phoenix.server.main serve
```

마지막으로 `SmolagentsInstrumentor`를 설정하여 에이전트를 추적하고 Phoenix 기본 엔드포인트로 해당 추적 데이터를 전송합니다.

```python
from phoenix.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

register()
SmolagentsInstrumentor().instrument()
```
이제 에이전트를 실행할 수 있습니다!

```py
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    WebSearchTool,
    VisitWebpageTool,
    InferenceClientModel,
)

model = InferenceClientModel()

search_agent = ToolCallingAgent(
    tools=[WebSearchTool(), VisitWebpageTool()],
    model=model,
    name="search_agent",
    description="This is an agent that can do web search.",
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[search_agent],
)
manager_agent.run(
    "If the US keeps its 2024 growth rate, how many years will it take for the GDP to double?"
)
```
끝입니다!
이제 `http://0.0.0.0:6006/projects/`로 이동하여 실행 결과를 확인할 수 있습니다!

<img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/smolagents/inspect_run_phoenix.png">

CodeAgent가 관리하는 ToolCallingAgent를 호출하여(참고로 관리되는 에이전트는 CodeAgent가 될 수도 있습니다) 미국 2024년 성장률을 웹에서 검색하도록 요청한 것을 확인할 수 있습니다. 이후 관리되는 에이전트가 결과를 보고하면, 관리자 에이전트가 이 정보를 활용하여 경제 배증 시간을 계산했습니다! 흥미롭죠?

## 🪢 Langfuse로 텔레메트리 설정[[setting-up-telemetry-with-🪢-langfuse]]

이 부분은 `SmolagentsInstrumentor`를 사용하여 **Langfuse**로 Hugging Face **smolagents**를 모니터링하고 디버깅하는 방법을 보여줍니다.

> **Langfuse란?** [Langfuse](https://langfuse.com)는 LLM 엔지니어링을 위한 오픈소스 플랫폼입니다. AI 에이전트를 위한 추적 및 모니터링 기능을 제공하여 개발자가 제품을 디버깅하고, 분석하고, 최적화할 수 있도록 도와줍니다. Langfuse는 네이티브 통합, OpenTelemetry, SDK를 통해 다양한 도구와 프레임워크와 통합됩니다.

### 1단계: 의존성 설치[[step-1:-install-dependencies]]

```python
%pip install langfuse 'smolagents[telemetry]' openinference-instrumentation-smolagents
```

### 2단계: 환경 변수 설정[[step-2:-set-up-environment-variables]]

Langfuse API 키를 설정하고 Langfuse로 추적을 보내도록 OpenTelemetry 엔드포인트를 구성하세요. [Langfuse Cloud](https://cloud.langfuse.com)에 가입하거나 [Langfuse를 자체 호스팅](https://langfuse.com/self-hosting)하여 Langfuse API 키를 얻으세요.

또한 [Hugging Face 토큰](https://huggingface.co/settings/tokens) (`HF_TOKEN`)을 환경 변수로 추가하세요.

```python
import os
# 프로젝트 설정 페이지(https://cloud.langfuse.com)에서 프로젝트 키를 가져옵니다.
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com" # 🇪🇺 유럽 지역
# os.environ["LANGFUSE_HOST"] = "https://us.cloud.langfuse.com" # 🇺🇸 미국 지역

# Hugging Face 토큰을 입력합니다.
os.environ["HF_TOKEN"] = "hf_..."
```

환경 변수가 설정되면 이제 Langfuse 클라이언트를 초기화할 수 있습니다. `get_client()`는 환경 변수에 제공된 자격 증명을 사용하여 Langfuse 클라이언트를 초기화합니다.

```python
from langfuse import get_client

langfuse = get_client()

# 연결을 확인합니다.
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")
```

### 3단계: `SmolagentsInstrumentor` 초기화[[step-3:-initialize-the-`smolagentsinstrumentor`]]

애플리케이션 코드를 실행하기 전에 `SmolagentsInstrumentor`를 초기화하세요.

```python
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

SmolagentsInstrumentor().instrument()
```

### 4단계: smolagent 실행[[step-4:-run-your-smolagent]]

```python
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    WebSearchTool,
    VisitWebpageTool,
    InferenceClientModel,
)

model = InferenceClientModel(
    model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
)

search_agent = ToolCallingAgent(
    tools=[WebSearchTool(), VisitWebpageTool()],
    model=model,
    name="search_agent",
    description="This is an agent that can do web search.",
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[search_agent],
)
manager_agent.run(
    "How can Langfuse be used to monitor and improve the reasoning and decision-making of smolagents when they execute multi-step tasks, like dynamically adjusting a recipe based on user feedback or available ingredients?"
)
```

### 5단계: Langfuse에서 추적 보기[[step-5:-view-traces-in-langfuse]]

에이전트를 실행한 후, Langfuse의 smolagents 애플리케이션에서 생성된 추적 정보를 확인할 수 있습니다. AI 에이전트의 디버깅과 최적화에 도움이 되는 LLM 상호작용의 상세한 세부 과정을 살펴볼 수 있습니다.

![smolagents example trace](https://langfuse.com/images/cookbook/integration-smolagents/smolagent_example_trace.png)

_[Langfuse의 추적 예시](https://cloud.langfuse.com/project/cloramnkj0002jz088vzn1ja4/traces/ce5160f9bfd5a6cd63b07d2bfcec6f54?timestamp=2025-02-11T09%3A25%3A45.163Z&display=details)_
