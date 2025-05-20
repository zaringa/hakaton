import pandas as pd
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from dataclasses import dataclass
class Edge:
    def init(self, speed, length, priority):
        self.speed = speed
        self.length = length
        self.priority = priority
        self.time = self.length / (self.speed * 1000 / 3600)  # Время в секундах
        self.weight = 1 / self.time if self.time > 0 else 0


@dataclass
class DataSets:
    stri: list[str]
    inut: list[str]


class Graph:
    def init(self):
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
        """Находит путь с максимальным весом и возвращает время для каждого участка"""
        if used_edges is None:
            used_edges = set()

        best_path = None
        best_times = []
        best_weight = 0

        def explore_path(current_node, current_path, current_times, current_weight):
            nonlocal best_path, best_times, best_weight

            if len(current_path) > 1 and current_weight > best_weight:
                best_path = current_path.copy()
                best_times = current_times.copy()
                best_weight = current_weight

            for neighbor in self.node_connections[current_node]:
                if neighbor not in self.graph[current_node]:
                    continue
                edge = self.graph[current_node][neighbor]
                if (current_node, neighbor) not in used_edges and neighbor not in current_path:
                    used_edges.add((current_node, neighbor))
                    explore_path(neighbor, 
                               current_path + [neighbor],
                               current_times + [edge.time],
                               current_weight + edge.weight)
                    used_edges.remove((current_node, neighbor))

        explore_path(start_node, [start_node], [], 0)
        return best_path, best_times

    def build_sequential_paths(self):
        """Строит последовательность путей с временем для каждого участка"""
        sorted_edges = sorted(self.all_edges, key=lambda x: x[2].priority, reverse=True)
        used_edges = set()
        sequential_paths = []

        while True:
            found_path = False
            for u, v, edge in sorted_edges:
                if (u, v) not in used_edges and (v, u) not in used_edges:
                    best_path, times = self.find_best_path(u, used_edges)
                    if best_path and len(best_path) > 1:
                        found_path = True
                        sequential_paths.append((best_path, times))
                        for i in range(len(best_path) - 1):
                            used_edges.add((best_path[i], best_path[i+1]))
                            used_edges.add((best_path[i+1], best_path[i]))
                        break
            if not found_path:
                break

        return sequential_paths

    @classmethod
    def from_csv(cls, filename):
        graph = cls()
        df = pd.read_csv(filename, header=None,
                         names=['u', 'v', 'length', 'speed', 'priority'])
        for _, row in df.iterrows():
            graph.add_edge(row['u'], row['v'], row['speed'], row['length'], row['priority'])
        return graph

    def print_paths(self, paths):
        """Выводит маршруты в заданном формате"""
        for i, (path, times) in enumerate(paths, 1):
            path_str = " -> ".join(path)
            time_str = " + ".join(f"{t:.1f}s" for t in times)
            print(f"Маршрут: {path_str}")
            print(f"Время по участкам: {time_str}\n")

    def visualize_graph(self, paths=None):
        """Визуализирует граф с выделенными путями"""
        G = nx.Graph()
        for u, v, edge in self.all_edges:
            G.add_edge(u, v, weight=edge.time)

        pos = nx.spring_layout(G)
        
        nx.draw_networkx_nodes(G, pos, node_size=700)
        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_labels(G, pos, font_size=10)
        
        if paths:
            for path, _ in paths:
                edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
                nx.draw_networkx_edges(G, pos, edgelist=edges, 
                                      edge_color="red", width=2)

        plt.title("Визуализация графа")
        plt.axis("off")
        plt.show()

# Пример использования
g = Graph.from_csv('svias.csv')
clic = DataSets 
sequential_paths = g.build_sequential_paths()

# Выводим результаты в нужном формате
g.print_paths(sequential_paths)

# Визуализация графа
g.visualize_graph(sequential_paths)