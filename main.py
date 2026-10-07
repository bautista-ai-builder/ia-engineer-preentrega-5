"""CLI persistente; cada conversación se identifica con --thread-id."""

import argparse
import os
from pathlib import Path

from agent import build_graph
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()


def run_turn(graph, text: str, thread_id: str) -> str:
    if not thread_id.strip():
        raise ValueError("thread_id no puede estar vacío")
    result = graph.invoke({"messages": [HumanMessage(content=text)]},
                          config={"configurable": {"thread_id": thread_id}},
                          recursion_limit=20)
    return str(result["messages"][-1].content)


def main() -> None:
    parser = argparse.ArgumentParser(description="Agente con herramientas y memoria persistente")
    parser.add_argument("--thread-id", required=True, help="ID estable de la conversación")
    parser.add_argument(
        "--db", type=Path, default=Path(os.getenv("CHECKPOINT_DB", "checkpoints.sqlite"))
    )
    parser.add_argument("question", nargs="*", help="Pregunta única; sin argumento abre chat")
    args = parser.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    with SqliteSaver.from_conn_string(str(args.db)) as saver:
        graph = build_graph(checkpointer=saver)
        if args.question:
            print(run_turn(graph, " ".join(args.question), args.thread_id))
            return
        print(f"Conversación {args.thread_id}. Escribe salir para terminar.")
        while True:
            try:
                question = input("Tú> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if question.lower() in {"salir", "exit", "quit"}:
                break
            if question:
                print("Agente>", run_turn(graph, question, args.thread_id))


if __name__ == "__main__":
    main()
