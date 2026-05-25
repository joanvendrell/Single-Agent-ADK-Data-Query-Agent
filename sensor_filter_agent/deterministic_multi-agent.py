from __future__ import annotations

from google.adk.agents import Agent, SequentialAgent

from .tools import filter_records_adk


query_understanding_agent = Agent(
    name="query_understanding_agent",
    model="gemini-2.0-flash",
    instruction="""
You analyze user queries about sensor records.

Your job is to determine whether the user is asking a supported filtering question.

Supported filters are exactly:
- location
- sensor_type
- value_range
- anomaly_label

Unsupported requests include:
- counts
- averages
- aggregations
- charts
- statistics
- general conversation
- questions not about the uploaded sensor dataset

If the query is supported, identify the filters that should be applied.
If the query is unsupported, clearly say that it should be declined.

Do not call tools.
Output a compact structured explanation for the next agent.
""",
    output_key="query_analysis",
)


filter_execution_agent = Agent(
    name="filter_execution_agent",
    model="gemini-2.0-flash",
    instruction="""
You execute valid filtering requests over the sensor dataset.

You receive the previous agent's analysis in session state under:
query_analysis

You may answer ONLY filtering questions about sensor records.

Supported filters are exactly:
- location
- sensor_type
- value_range
- anomaly_label

You have one tool:
- filter_records_adk

The tool applies exactly one filter criterion per call.

For multi-condition requests, call filter_records_adk multiple times, passing the previous tool
result as previous_results each time.

If query_analysis says the request is unsupported, decline and do not call tools.

Do not perform counts, averages, aggregations, charts, or general conversation.
Return only the filtered records or a short decline message.
""",
    tools=[filter_records_adk],
)


root_agent = SequentialAgent(
    name="sensor_filter_root_agent",
    sub_agents=[
        query_understanding_agent,
        filter_execution_agent,
    ],
)