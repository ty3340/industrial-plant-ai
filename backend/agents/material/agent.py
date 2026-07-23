"""Material Calculating agent — an agent over the recipe tool."""
from langchain.agents import create_agent

from shared.llm import get_model
from agents.material.tools import calculate_material_requirements

PROMPT = (
    "You are the Material Calculating agent for a batch plant. "
    "When asked about materials for a product, call calculate_material_requirements "
    "and report the litres of each raw material clearly."
)


def build_material_agent():
    return create_agent(
        model=get_model(),
        tools=[calculate_material_requirements],
        name="material_agent",
        system_prompt=PROMPT,
    )
