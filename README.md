# Single-Agent-ADK-Data-Query-Agent

This repository implements the home assignment: a single-agent Google ADK project that answers filtering-only questions over `sensor_data.xlsx`.

## What the agent can answer

Supported filtering criteria:

- `location`
- `sensor_type`
- `value_range`
- `anomaly_label`

The tool applies **one criterion per call**. For a query like:

> Show gas anomalies in Zone 2 with value above 60

The agent should call:

1. `filter_records(location, "Zone 2")`
2. `filter_records(sensor_type, "gas", previous_results=...)`
3. `filter_records(anomaly_label, True, previous_results=...)`
4. `filter_records(value_range, {"min": 60}, previous_results=...)`

## Project setup

Install pixi if needed:

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

Install dependencies:

```bash
pixi install
```

Copy environment variables:

```bash
cp .env.example .env
```

Set `GOOGLE_API_KEY` in `.env` for ADK/Gemini usage.

## Run the local deterministic CLI

This does not require an LLM API key and is useful for debugging the assignment logic:

```bash
pixi run run
```

Example queries:

```text
Show gas readings in Area A
Show gas anomalies in Zone 2 with value above 60
Find vibration anomalies in Area A with value above 6
Show temperature sensors with values between 20 and 30
Show gas readings above 50 that are not anomalies
```

## Run with Google ADK

From the repository root:

```bash
pixi run adk-web
```

or:

```bash
pixi run adk-run
```

The ADK agent is defined in `sensor_filter_agent/agent.py` as `root_agent`.

## Test

```bash
pixi run test
```

## Assignment design decisions

- The ADK agent is single-agent only.
- There is exactly one dataset filtering tool: `filter_records`.
- The tool applies exactly one filtering criterion per call.
- Intermediate filtering has no row limit.
- Final display should show at most the first 20 records.
- Non-filtering requests are declined.
- Although the assignment text says `anomaly_label` uses boolean `True`, one valid example asks for readings that are **not anomalies**, so the implementation accepts both `True` and `False`.

## Execution-control experiment

Suggested configurations:

- Configuration A: low reasoning budget / single-shot behavior. In practice, this may fail on multi-filter queries because the model may try to combine criteria in one tool call.
- Configuration B: iterative behavior with enough steps for multi-condition questions. This is better for chained filters because each criterion requires a separate tool call.

See `reports/report.md` for details.

PYTHONPATH=. pixi run python -m sensor_filter_agent.cli
PYTHONPATH=. pixi run adk run sensor_filter_agent
