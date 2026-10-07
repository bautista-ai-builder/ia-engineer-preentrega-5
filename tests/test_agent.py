from agent import build_graph
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from tools import buscar_cliente, buscar_pedidos, sumar_importes

from main import run_turn


def test_business_tools_return_grounded_data():
    assert '"nombre": "Ana"' in buscar_cliente.invoke({"cliente_id": "101"})
    assert '"P-1001"' in buscar_pedidos.invoke({"cliente_id": "101"})
    assert '"17000.50"' in sumar_importes.invoke({"importes": ["12500.50", "4500.00"]})


def test_graph_dispatches_tool_and_persists_thread(tmp_path):
    class Model:
        def bind_tools(self, tools):
            assert len(tools) == 3
            return self

        def invoke(self, messages):
            if isinstance(messages[-1], ToolMessage):
                return AIMessage(content="Cliente encontrado: " + messages[-1].content)
            if "¿Cómo se llama?" in messages[-1].content:
                prior = [m for m in messages if isinstance(m, HumanMessage)]
                return AIMessage(content=f"Recuerdo {len(prior)} turnos del cliente 101.")
            return AIMessage(content="", tool_calls=[{
                "name": "buscar_cliente", "args": {"cliente_id": "101"}, "id": "call-1"
            }])

    db = str(tmp_path / "checkpoints.sqlite")
    with SqliteSaver.from_conn_string(db) as saver:
        graph = build_graph(model=Model(), checkpointer=saver)
        first = run_turn(graph, "Busca al cliente 101", "thread-a")
        assert "Ana" in first
    with SqliteSaver.from_conn_string(db) as saver:
        graph = build_graph(model=Model(), checkpointer=saver)
        second = run_turn(graph, "¿Cómo se llama?", "thread-a")
        assert "2 turnos" in second
        assert graph.get_state({"configurable": {"thread_id": "thread-a"}}).values["messages"]
