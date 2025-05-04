
from dataclasses import Field
import os 
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END

from settings import EXTRACT_PROBLEM_DESCRIPTION_PROMPT, SOLVE_PROBLEM_PROMPT


from dotenv import load_dotenv

load_dotenv()


class State(MessagesState):
    initial_text: str = Field(default="")


def build_agent_graph(self):

    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    model_name = os.environ.get("MODEL_NAME", "qwen2.5-coder:14b")

    llm = ChatOllama(model=model_name, base_url=ollama_host)

    def extract_problem_description(state: State) -> State:
        """Evaluate if we have enough information to answer"""

        evaluation_prompt = EXTRACT_PROBLEM_DESCRIPTION_PROMPT

        response = llm.invoke(state["messages"] + [HumanMessage(content=evaluation_prompt)])

        return {"messages": state["messages"] + [response]}

    def solve_problem(state: State) -> State:
        """Solve the problem"""

        prompt = SOLVE_PROBLEM_PROMPT
        
        response = llm.invoke(state["messages"] + [SystemMessage(content=prompt)])

        return {"messages": state["messages"] + [response]}

    graph_definition = StateGraph(State)
    graph_definition.add_node("extract_problem_description_node", extract_problem_description)
    graph_definition.add_node("solve_problem_node", solve_problem)

    graph_definition.add_edge(START, "extract_problem_description_node")
    graph_definition.add_conditional_edges("extract_problem_description_node", solve_problem)
    graph_definition.add_edge("solve_problem_node", END)

    return graph_definition
