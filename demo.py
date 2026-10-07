"""Demostración de memoria entre turnos usando el mismo thread_id."""

import os

from agent import build_graph
from langgraph.checkpoint.sqlite import SqliteSaver

from main import run_turn


def main() -> None:
    db = os.getenv("CHECKPOINT_DB", "checkpoints.sqlite")
    with SqliteSaver.from_conn_string(db) as saver:
        graph = build_graph(checkpointer=saver)
        for question in (
            "¿Cuántos pedidos tiene el cliente 101 y cuál fue el total de todos ellos?",
            "¿Cómo se llama ese cliente?",
            "¿Cuánto sumaban sólo los pedidos pagados de ese mismo cliente?",
        ):
            print("Usuario:", question)
            print("Agente:", run_turn(graph, question, "demo-cliente-101"))
            print()


if __name__ == "__main__":
    main()
