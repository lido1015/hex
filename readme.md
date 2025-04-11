# AI para Hex con Conjuntos Disjuntos y Heurística de Evaluación

## Introducción  
Este repositorio implementa una IA para el juego de Hex utilizando el algoritmo **Alpha-Beta** con poda, mejorado con una heurística personalizada. El código destaca por el uso de:  
- **Estructura de Conjuntos Disjuntos (Union-Find)** para verificar conectividad eficiente.  
- **Heurística basada en Dijkstra** para evaluar estados del tablero.  

---

## Componentes Clave

### HexDisjointSet: Conjuntos Disjuntos para Conectividad

- **Seguimiento eficiente de conexiones**:  
  Estructura Union-Find que agrupa dinámicamente celdas en componentes conectados.
- **Nodos virtuales para bordes**:
  - Jugador 1 (🔴): Usa nodos `0` (izquierdo) y `1` (derecho).
  - Jugador 2 (🔵): Usa nodos `2` (superior) y `3` (inferior).
- **Actualización automática**: Al colocar una ficha, une celdas adyacentes y bordes relevantes.
- **Verificación de victoria en O(1)**:  
  Comprueba si los bordes virtuales están conectados (Ej: `_root(0) == _root(1)` para Jugador 1).

### 2. Función de Evaluación Heurística  
- **Objetivo**: Estimar movimientos mínimos necesarios para conectar los bordes.  
- **Algoritmo**:  
  - **Dijkstra Modificado**:  
    - Prioriza celdas ocupadas por el jugador (costo `0`) o vacías (costo `+1`).  
    - Calcula la ruta más corta (en movimientos) para conectar los bordes.  
  - **Puntuación**:  
    - `puntuación = movimientos_oponente - movimientos_jugador`  
    - Valores altos indican ventaja para la IA.  

---

## Notas de Uso  
- **Compatibilidad con HexBoard**:  
  - El código asume una clase `HexBoard` con métodos como `place_piece`, `get_possible_moves` y `check_connection`.  
  - Se incluye una implementación básica, pero puede reemplazarse con cualquier otra.  
- **Configuración de la IA**:  
  - Profundidad de búsqueda fija (`cutoff=2`). Ajustar para equilibrio velocidad/eficacia.  
  - La heurística es eficiente y evita exploraciones exhaustivas del tablero.  

---

## Detalles Técnicos  
- **Optimizaciones en Conjuntos Disjuntos**:  
  - *Compresión de camino* y *unión por rango* para operaciones en tiempo casi constante.  
- **Eficiencia de la Heurística**:  
  - Dijkstra prioriza caminos prometedores, reduciendo costos computacionales.  

---

## Dependencias  
- Python 3.10+  
- `copy` (para clonar tableros).  
- `heapq` (para la cola de prioridad en la heurística).  

---


