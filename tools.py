"""Herramientas de negocio con datos locales y cálculo decimal."""

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from langchain_core.tools import tool

DATA_PATH = Path(__file__).resolve().parent / "data" / "clientes.json"


def _data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


@tool
def buscar_cliente(cliente_id: str) -> str:
    """Busca nombre y correo de un cliente por su identificador, por ejemplo 101."""
    client = next((c for c in _data()["clientes"] if c["id"] == cliente_id), None)
    return json.dumps(client if client is not None else {"error": "Cliente no encontrado"},
                      ensure_ascii=False)


@tool
def buscar_pedidos(cliente_id: str) -> str:
    """Devuelve pedidos, importes y estados de un cliente por su identificador."""
    orders = [o for o in _data()["pedidos"] if o["cliente_id"] == cliente_id]
    return json.dumps(orders, ensure_ascii=False)


@tool
def sumar_importes(importes: list[str]) -> str:
    """Suma importes decimales exactos; recibe una lista de números como cadenas."""
    try:
        amounts = [Decimal(item) for item in importes]
    except InvalidOperation:
        return json.dumps({"error": "Importe decimal inválido"})
    return json.dumps({"total": str(sum(amounts, Decimal("0.00")))})


TOOLS = [buscar_cliente, buscar_pedidos, sumar_importes]
