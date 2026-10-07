"""Agente LangGraph con selección autónoma de herramientas y memoria SQLite."""

import os

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from tools import TOOLS

load_dotenv()
SYSTEM = SystemMessage(content=(
    "Eres un asistente de pedidos. Decide por ti mismo cuándo llamar herramientas. "
    "Usa buscar_cliente para datos de identidad, buscar_pedidos para pedidos y "
    "sumar_importes para cálculos monetarios. No inventes clientes, pedidos ni montos. "
    "Recuerda lo conversado en este thread_id. Si falta el ID del cliente, pídelo. "
    "Responde en español e indica si un dato proviene de una herramienta."
))


def default_model():
    from langchain_openai import ChatOpenAI

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Falta OPENAI_API_KEY en .env")
    return ChatOpenAI(model=os.getenv("CHAT_MODEL", "gpt-4o-mini"), temperature=0)


def build_graph(*, model=None, checkpointer=None):
    selected = model if model is not None else default_model()
    bound_model = selected.bind_tools(TOOLS)

    def call_model(state: MessagesState):
        reply = bound_model.invoke([SYSTEM, *state["messages"]])
        return {"messages": [reply]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", call_model)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition, {"tools": "tools", END: END})
    builder.add_edge("tools", "assistant")
    return builder.compile(checkpointer=checkpointer)
