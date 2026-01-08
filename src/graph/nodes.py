import os
from pathlib import Path
from strands import Agent, tool
from strands_tools import file_write
from src.prompts.template import apply_prompt_template

def product_researcher_node():
    agent = Agent(
        system_prompt=apply_prompt_template(prompt_name="product_researcher", prompt_context={}),
        tools=[file_write]
    )

def persona_generator_node():
    agent = Agent(
        system_prompt=apply_prompt_template(prompt_name="persona_generator", prompt_context={}),
        tools=[file_write]
    )

def interview_planner_node():
    agent = Agent(
        system_prompt=apply_prompt_template(prompt_name="interview_planner", prompt_context={}),
        tools=[file_write]
    )

def analyst_node():
    agent = Agent(
        system_prompt=apply_prompt_template(prompt_name="analyst", prompt_context={}),
        tools=[file_write]
    )
