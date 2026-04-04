# IA para Hex: Implementación con MiniMax

## Descripción

Este proyecto implementa un agente inteligente para el juego de Hex utilizando algoritmos de búsqueda adversarial con poda Alpha-Beta, optimizado mediante una estructura de datos Union-Find para verificación de conectividad y una función heurística basada en el algoritmo de Dijkstra para evaluación de estados. El sistema está diseñado para tableros de tamaño variable, con estrategias adaptativas de profundidad de búsqueda para mantener tiempos de respuesta razonables.

## Componentes Principales

### 1. HexDisjointSet
Implementación de Union-Find para detección eficiente de conexiones:
- **Nodos Virtuales**: 4 nodos adicionales para representar bordes del tablero
  - Nodo 0: Borde izquierdo (Jugador 1)
  - Nodo 1: Borde derecho (Jugador 1)
  - Nodo 2: Borde superior (Jugador 2)
  - Nodo 3: Borde inferior (Jugador 2)
- Las operaciones de unión y búsqueda se optimizan con compresión de camino y unión por rango, permitiendo verificaciones de conectividad en tiempo casi constante.


### 2. SmartPlayer
Agente IA que implementa búsqueda minimax con poda Alpha-Beta:
- **Profundidad Adaptativa**: Ajusta la profundidad máxima según tamaño del tablero, movimientos restantes y tiempo disponible
- **Control de Tiempo**: Monitoreo continuo durante la búsqueda para evitar timeouts (límite de 4.8 segundos por movimiento)

## Algoritmos Implementados

### 1. Búsqueda Alpha-Beta
Implementación del algoritmo minimax con poda para reducir el espacio de búsqueda:
- Explora el árbol de juego de manera eficiente, podando ramas que no afectan la decisión óptima
- Utiliza valores α y β para mantener cotas superior e inferior del valor del nodo

### 2. Heurística de Evaluación
Función heurística basada en distancia mínima a la victoria:
- Calcula movimientos mínimos necesarios para que cada jugador conecte sus bordes
- Puntuación: diferencia entre movimientos del oponente y del jugador
- Valores positivos favorecen al jugador evaluado

### 3. Dijkstra Modificado para Distancia Mínima
Adaptación del algoritmo de Dijkstra para calcular caminos óptimos en el tablero:
- Asigna costos a celdas: 0 para celdas propias, 1 para vacías, infinito para oponentes
- Encuentra el camino de menor costo desde un borde inicial hasta el borde opuesto

### 4. Función de Corte Adaptativo
La función cutoff ajusta dinámicamente la profundidad máxima de búsqueda basándose en:
- Tamaño del tablero (más profundidad para tableros pequeños)
- Proporción de movimientos restantes (más profundidad en fases finales)
- Restricciones de tiempo para asegurar respuestas oportunas








