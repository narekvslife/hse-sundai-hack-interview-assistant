# %%capture --no-stderr
# %pip install -U langgraph langsmith langchain-ollama

import getpass
import os
import multiprocessing
import queue
import subprocess
import sys
import time
import traceback
from typing import Annotated, List, TypedDict
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain import hub
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END, StateGraph, START
from langchain_core.tracers.context import tracing_v2_enabled
from langsmith import Client


MAX_ATTEMPTS = 10
EXECUTION_TIMEOUT_BUFFER = 1


multiprocessing.set_start_method("fork", force=True)


class TestCase(TypedDict):
    """Представляет один тестовый случай с входными и ожидаемыми выходными данными."""
    inputs: str
    outputs: str

class State(TypedDict):
    """Представляет состояние графа LangGraph."""
    messages: Annotated[list[AnyMessage], add_messages]
    test_cases: list[TestCase]
    runtime_limit: int
    status: str
    problem_level: str

class WritePythonTool(BaseModel):
    """Инструмент для написания Python кода."""
    reasoning: str = Field(..., description="Концептуальное решение.")
    pseudocode: str = Field(..., description="Детальный псевдокод на английском языке.")
    code: str = Field(..., description="Действительный Python 3 код, решающий проблему")

def _execute_python_code(program: str, input_data: str, timeout: float) -> tuple[str | None, str | None, int]:
    """Выполняет Python код в подпроцессе и возвращает stdout, stderr и код возврата."""
    try:
        process = subprocess.Popen(
            [sys.executable, "-c", program],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input=input_data, timeout=timeout)
        return stdout, stderr, process.returncode
    except subprocess.TimeoutExpired:
        if process:
            process.kill()
        return None, "Execution timed out.", -1
    except Exception as e:
        return None, traceback.format_exc(), -1

def _normalize_output(output: str | None) -> str:
    """Нормализует вывод, удаляя лишние пробелы."""
    return output.strip() if output is not None else ""

def check_code_correctness(program: str, input_data: str, expected_output: str, timeout: float) -> str:
    """Проверяет корректность Python кода, выполняя его на заданных входных данных."""
    q = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=_run_and_check_code, args=(q, program, input_data, expected_output, timeout)
    )
    process.start()
    print('start process')
    process.join(timeout=timeout + EXECUTION_TIMEOUT_BUFFER)

    if process.is_alive():
        process.terminate()
        process.join()
        result = "timed out"
    else:
        try:
            result = q.get_nowait()
        except queue.Empty:
            result = "failed: No result returned from subprocess."
        except Exception as e:
            result = f"failed: Error retrieving result from queue: {e}"

    q.close()
    q.join_thread()
    return result

def _run_and_check_code(q: multiprocessing.Queue, program: str, input_data: str, expected_output: str, timeout: float):
    """Выполняет код и помещает результат проверки в очередь."""
    # print('start checking code')
    stdout, stderr, returncode = _execute_python_code(program, input_data, timeout)

    if stderr and returncode != 0:
        # print('error while checking code')
        q.put(f"failed: {stderr}")
    elif stdout is not None:
        actual_output_normalized = _normalize_output(stdout)
        expected_output_normalized = _normalize_output(expected_output)
        if actual_output_normalized == expected_output_normalized:
            # print("Test passed")
            q.put("passed")
        else:
            # print('Found wrong test')
            q.put(f"wrong answer. Expected '{expected_output_normalized}', got '{actual_output_normalized}'")
    else:
        q.put("timed out")

class Solver:
    """Узел графа, отвечающий за генерацию Python кода с помощью LLM."""
    def __init__(self, llm: BaseChatModel, prompt: ChatPromptTemplate):
        self.runnable = prompt | llm.bind_tools([WritePythonTool])

    def __call__(self, state: State) -> dict:
        response = self.runnable.invoke({"messages": state["messages"]})
        return {"messages": [response]}

def _format_tool_error_message(ai_message: AIMessage, error_message: str) -> ToolMessage | HumanMessage:
    """Форматирует сообщение об ошибке, связанной с вызовом инструмента."""
    tool_call_id = ai_message.tool_calls[0].get("id") if ai_message.tool_calls else None
    if tool_call_id:
        return ToolMessage(content=error_message, tool_call_id=tool_call_id)
    else:
        return HumanMessage(content=error_message + " No tool call ID found.")

def evaluate_code(state: State) -> dict:
    """Узел графа, отвечающий за выполнение и оценку сгенерированного кода."""
    test_cases = state["test_cases"]
    runtime_limit = state["runtime_limit"]
    ai_message: AIMessage = state["messages"][-1]

    if not isinstance(ai_message, AIMessage) or not ai_message.tool_calls:
        error_content = "No valid code submission found in the last message. Please try again using the 'writePython' tool."
        return {"messages": [HumanMessage(content=error_content)]}

    try:
        tool_call = ai_message.tool_calls[0]
        if tool_call['name'] != WritePythonTool.__name__:
            raise ValueError(f"Expected tool {WritePythonTool.__name__}, got {tool_call['name']}")
        code = tool_call["args"]["code"]
    except (IndexError, KeyError, Exception) as e:
        error_message = f"Failed to parse code from tool call: {repr(e)}. Ensure you are using the 'writePython' tool correctly with 'reasoning', 'pseudocode', and 'code' arguments."
        return {"messages": [_format_tool_error_message(ai_message, error_message)]}

    num_test_cases = len(test_cases)
    succeeded_count = 0
    test_results = []

    print("\n--- Evaluating Code ---")
    print(f"Code:\n```python\n{code}\n```")
    print(f"Running {num_test_cases} test case(s)...")

    for i, test_case in enumerate(test_cases):
        input_data = test_case["inputs"]
        expected_output = test_case["outputs"]
        print(f"Test {i+1}: Input='{input_data}', Expected='{expected_output}'")
        test_result = check_code_correctness(code, input_data, expected_output, runtime_limit)
        print(f"Test {i+1} Result: {test_result}")
        test_results.append(test_result)
        if test_result == "passed":
            succeeded_count += 1

    pass_rate = succeeded_count / num_test_cases if num_test_cases > 0 else 0.0
    print(f"--- Evaluation Complete: {succeeded_count}/{num_test_cases} passed ---")

    if pass_rate == 1.0:
        print("All tests passed! Status set to success.")
        return {"status": "success"}
    else:
        responses = "\n".join(
            [f"<test id={i}>\nInput:\n{tc['inputs']}\nExpected Output:\n{tc['outputs']}\nResult: {r}\n</test>"
             for i, (tc, r) in enumerate(zip(test_cases, test_results))]
        )
        response = f"Incorrect submission. Please review the feedback and respond with updated code.\nPass rate: {succeeded_count}/{num_test_cases}\nTest Results:\n{responses}"
        formatted_message = ToolMessage(content=response + "\nMake all fixes using the writePython tool.",
                                        tool_call_id=ai_message.tool_calls[0].get("id") if ai_message.tool_calls else None)
        return {"messages": [formatted_message]}

def should_continue(state: State) -> str:
    """Определяет, следует ли продолжать цикл решения."""
    if state.get("status") == "success":
        return END
    if len(state.get("messages", [])) > MAX_ATTEMPTS:
        print("Reached maximum attempts.")
        return END
    return "solver"

# --- Graph Definition ---
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert Python programmer. Write Python code to solve the user's problem in format solution function, input data. Structure your response using the 'writePython' tool, including reasoning, pseudocode, and the final Python code."),
        ("placeholder", "{messages}"),
    ]
)

llm = ChatOllama(model="qwen2.5-coder:32b", temperature=0)
solver = Solver(llm, prompt)

builder = StateGraph(State)
builder.add_node("solver", solver)
builder.add_node("evaluate", evaluate_code)
builder.add_conditional_edges(START, should_continue, {END: END, "solver": "solver"}) # Условный переход от START
builder.add_edge("solver", "evaluate")
builder.add_conditional_edges("evaluate", should_continue, {END: END, "solver": "solver"})

graph = builder.compile()

# --- Testing with a Simple Sum Task ---
if __name__ == '__main__':
    print("\n--- Testing with a Simple Palindrome Task ---")

    task_description = """
    Given an integer x, return true if x is a palindrome, and false otherwise.
    """

    simple_test_cases = [
        TestCase(inputs="121", outputs="true"),
        TestCase(inputs="-121", outputs="false"),
        TestCase(inputs="10", outputs="false"), # Исправлен ожидаемый вывод для 10
    ]

    input_state = State(
        messages=[HumanMessage(content=task_description)],
        test_cases=simple_test_cases,
        runtime_limit=2,
        status="in_progress",
        problem_level="easy",
    )

    # client = Client(hide_inputs=False, hide_outputs=False) # Simpler task, no need to hide
    print("\n--- Running Graph ---")
    events = graph.stream(input_state, {"recursion_limit": MAX_ATTEMPTS + 2}) # Учитываем начальное сообщение и возможные итерации
    for event in events:
        # print(f"Event: {event}")
        for node, value in event.items():
            if node != "__end__":
                print(f"\n--- Output from Node: {node} ---")
                messages = value.get("messages")
                status = value.get("status")
                # if messages:
                    # last_message = messages[-1]
                    # print(f"Type: {type(last_message).__name__}")
                    # if hasattr(last_message, 'content'):
                        # print(f"Content: {str(last_message.content)}")
                    # if hasattr(last_message, 'tool_calls'):
                        # print(f"Tool Calls: {last_message.tool_calls}")
                # if status:
                    # print(f"Status Updated: {status}")

    print("\n--- Graph Execution Finished ---")