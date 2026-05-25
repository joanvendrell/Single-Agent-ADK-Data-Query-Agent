from google.adk.agents import Agent
from .tools import filter_records_adk

"""
Example of agent.py but using multiple agents.
"""

query_understanding_agent = Agent(
    name="query_understanding_agent",
    model="gemini-2.0-flash",
    instruction="""
    You analyze user queries about sensor records.
    Identify whether the query is a supported filtering query.
    Supported filters are:
    - location
    - sensor_type
    - value_range
    - anomaly_label

    Do not call tools. Only explain which filters are needed.
    """,
)

filter_execution_agent = Agent(
    name="filter_execution_agent",
    model="gemini-2.0-flash",
    instruction="""
    You execute filtering requests over the sensor dataset.
    You may only use filter_records_adk.
    For multi-condition filters, call the tool once per condition.
    """,
    tools=[filter_records_adk],
)

root_agent = Agent(
    name="sensor_filter_root_agent",
    model="gemini-2.0-flash",
    instruction="""
    You are the coordinator.

    First, use the query_understanding_agent to understand whether the user
    is asking a supported filtering question.

    Then, if the request is valid, use the filter_execution_agent to apply
    the filters.

    If the user asks for counts, averages, charts, aggregations, or general
    conversation, decline.
    """,
    sub_agents=[
        query_understanding_agent,
        filter_execution_agent,
    ],
)