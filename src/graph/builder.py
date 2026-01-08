import asyncio
from strands.multiagent import GraphBuilder
from .nodes import (
    product_researcher_node,
    persona_generator_node,
    interview_planner_node,
    analyst_node
)
from .interview_node import interview_moderator_node

def build_graph():
    builder = GraphBuilder()

    builder.add_node(product_researcher_node, "product_researcher")
    builder.add_node(persona_generator_node, "persona_generator")
    builder.add_node(interview_planner_node, "interview_planner")
    builder.add_node(interview_moderator_node, "interview_moderator")
    builder.add_node(analyst_node, "analyst")

    # Set entry point and edges
    builder.set_entry_point("product_researcher")
    builder.add_edge("product_researcher", "persona_generator")
    builder.add_edge("persona_generator", "interview_planner")
    
    builder.add_edge("interview_planner", "interview_moderator")
    builder.add_edge("interview_moderator", "analyst") #, condition=should_proceed_to_supervisor)

    builder.set_max_node_executions(50)

    graph = builder.build()
    return graph
