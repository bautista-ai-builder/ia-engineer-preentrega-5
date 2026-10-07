# Pre-entrega 5: agente con herramientas y memoria persistente

Agente LangGraph para consultas de clientes y pedidos. El modelo decide cuándo usar tres herramientas: `buscar_cliente`, `buscar_pedidos` y `sumar_importes`. `StateGraph(MessagesState)` conecta el nodo del modelo con `ToolNode` mediante `tools_condition`. `SqliteSaver` conserva el historial por `thread_id` entre procesos.

## Instalación

Requiere Python 3.12+. Crear un entorno virtual e instalar `requirements.txt`. Copiar `.env.example` a `.env` y completar `OPENAI_API_KEY`. La base `checkpoints.sqlite` y `.env` están ignorados por Git. Los datos de negocio de demostración son ficticios y están en `data/clientes.json`.

## Ejecución

```bash
python main.py --thread-id cliente-101
python main.py --thread-id cliente-101 "¿Cuántos pedidos tiene el cliente 101?"
python main.py --thread-id cliente-101 "¿Cómo se llama ese cliente?"
python demo.py
pytest -q
```

Repetir el mismo `thread_id` conserva el contexto; usar uno diferente abre una conversación independiente. `demo.py` realiza tres turnos sobre el cliente 101. El grafo limita a 20 pasos por turno para detectar bucles de herramientas. El modelo recibe los mensajes previos y los resultados reales de las herramientas; no se codificó una ruta fija por palabras clave. Los tests ejercitan herramientas, despacho y persistencia SQLite con un modelo falso, sin gasto de API.

**Seguridad de datos:** el corpus de ejemplo no contiene datos reales. No introducir claves o información personal sensible en la conversación de demostración porque SQLite conserva el historial en disco.
