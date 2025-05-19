import pandas as pd
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt

class Edge:
    def __init__(self, speed, length, priority):
        self.speed = speed
        self.length = length
        self.priority = priority
        self.weight = 1 / (self.length / (self.speed * 1000 / 3600)) if (self.length / (self.speed * 1000 / 3600))> 0 else 0
        self.used_in_iteration = None

class Graph:
    def __init__(self):
        self.graph = defaultdict(dict)
        self.all_edges = []
        self.node_connections = defaultdict(list)

    def add_edge(self, u, v, speed, length, priority):
        edge = Edge(speed, length, priority)
        self.graph[u][v] = edge
        self.all_edges.append((u, v, edge))
        self.node_connections[u].append(v)
        self.node_connections[v].append(u)

    def find_best_path(self, start_node, used_edges=None):
        """Находит путь с максимальным весом, начиная с заданной вершины."""
        if used_edges is None:
            used_edges = set()

        best_path = None
        best_weight = 0

        def explore_path(current_node, current_path, current_weight):
            """Рекурсивная функция для исследования путей."""
            nonlocal best_path, best_weight

            if len(current_path) > 1 and current_weight > best_weight:
                best_path = current_path[:]  # Копируем путь
                best_weight = current_weight

            for neighbor in self.node_connections[current_node]:
                if neighbor not in self.graph[current_node]: 
                    continue
                edge = self.graph[current_node][neighbor]
                if (current_node, neighbor) not in used_edges and neighbor not in current_path:
                    used_edges.add((current_node, neighbor))
                    explore_path(neighbor, current_path + [neighbor], current_weight + edge.weight)
                    used_edges.remove((current_node, neighbor))

        explore_path(start_node, [start_node], 0)
        return best_path, best_weight


    def build_sequential_paths(self):
        """Строит последовательность путей по приоритетам."""
        sorted_edges = sorted(self.all_edges, key=lambda x: x[2].priority, reverse=True)
        used_edges = set() 
        sequential_paths = []

        while True:
            found_path = False
            for u, v, edge in sorted_edges:
                if (u, v) not in used_edges and (v, u) not in used_edges:
                    best_path, total_weight = self.find_best_path(u, used_edges)

                    if best_path and len(best_path) > 1:
                        found_path = True
                        sequential_paths.append((best_path, (edge.length / (edge.speed * 1000 / 3600))))
                        for i in range(len(best_path) - 1):
                            used_edges.add((best_path[i], best_path[i+1]))
                            used_edges.add((best_path[i+1], best_path[i]))
            if not found_path:
                break

        return sequential_paths

    @classmethod
    def from_csv(cls, filename):
        graph = cls()
        df = pd.read_csv(filename, header=None,
                         names=['u', 'v', 'length', 'speed', 'priority'])

        for i, row in df.iterrows():
            graph.add_edge(row['u'], row['v'], row['speed'], row['length'], row['priority'])
        return graph

    def visualize_graph(self, paths=None):
        """Визуализирует граф с помощью networkx."""
        G = nx.Graph()
        for u, v, edge in self.all_edges:
            G.add_edge(u, v, weight=edge.weight)

        pos = nx.spring_layout(G)  # определяем layout графа

        # Рисуем граф
        nx.draw_networkx_nodes(G, pos, node_size=700)
        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")

        # Если переданы пути, выделяем их
        if paths:
            for path, _ in paths:
                edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
                nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color="red", width=2)

        plt.title("Graph Visualization")
        plt.axis("off")
        plt.show()


# Пример использования
g = Graph.from_csv('svias.csv')
sequential_paths = g.build_sequential_paths()
g.visualize_graph(sequential_paths)
