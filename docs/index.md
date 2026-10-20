# F1 - OpenF1 Python SDK

Bem-vindo à documentação oficial do **`f1`**, o SDK Python moderno, fortemente tipado e resiliente projetado para consumo e análise analítica de dados da [OpenF1 API](https://openf1.org/).

---

## Destaques do Projeto

- **18 Endpoints Mapeados:** Acesso total a telemetria (`car_data`), cronometragem volta a volta (`laps`), posições, rádios de comunicação, clima, resultados homologados e campeonatos de pilotos e construtores.
- **Modelagem Pydantic v2:** Validação em runtime com schemas fortemente tipados, serialização nativa e autocompletion no seu editor.
- **Resiliência de Rede:** Cliente HTTP com retry e backoff exponencial automático para erros transitórios (429, 500, 502, 503, 504) e controle de timeouts.
- **Integração com Pandas:** Conversão simplificada para `pandas.DataFrame` e suporte transparente ao formato CSV nativo da API.
- **Dashboard Interativo com Streamlit:** Interface visual completa com telemetria, tempos de volta, meteorologia e rádio das equipes.
- **Engenharia de Software Rigorosa:** Projeto estruturado sob o layout `src/`, formatação com Ruff, suíte de testes com cobertura mínima de 50% e documentação MkDocs Material.

---

## Exemplo Rápido de Uso

```python
from f1 import OpenF1Client
from f1.utils import to_dataframe

# Inicializa o cliente OpenF1
client = OpenF1Client()

# Consulta pilotos participantes da última sessão
drivers = client.get_drivers(session_key="latest")
for driver in drivers:
    print(f"#{driver.driver_number:02d} | {driver.full_name} ({driver.team_name})")

# Consulta telemetria de alta frequência com filtro de velocidade
telemetry = client.get_car_data(
    session_key=9159,
    driver_number=55,
    speed__gte=315,
)

# Converte para DataFrame analítico
df = to_dataframe(telemetry)
print(df[["speed", "rpm", "throttle", "brake"]].describe())
```

---

## Navegação Rápida

- [Instalação e Setup](setup.md): Como preparar seu ambiente local usando pyenv e Poetry.
- [Arquitetura](architecture.md): Organização interna das camadas `core`, `clients` e `utils`.
- [Referência da API](api_reference.md): Catálogo completo dos 18 endpoints e seus métodos no cliente.
- [Testes e Qualidade](testing.md): Procedimentos para rodar a suíte de testes com medição de cobertura e linter Ruff.
