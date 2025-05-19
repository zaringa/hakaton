import pandas as pd

class Edge:
    def __init__(self, speed, length):
        self.speed = speed
        self.length = length
        self.time = length / (speed * 1000 / 3600)
class Graph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, u, v, speed, length):
        if u not in self.graph:
            self.graph[u] = {}
        self.graph[u][v] = Edge(speed, length)

    def get_edge_data(self, u, v):
        return self.graph[u][v]

    def print_all_edges(self):
        for u in self.graph:
            for v in self.graph[u]:
                edge = self.graph[u][v]
                print(f"Ребро {u} -> {v}:")
                print(f"  Скорость: {edge.speed} км/ч")
                print(f"  Длина: {edge.length} м")
                print(f"  Время: {edge.time:.2f} сек")
                print()
    @classmethod
    def from_csv(cls, filename):
        graph = cls()

        df = pd.read_csv(filename, header=None, names=['u', 'v', 'length', 'speed'])
        
        for _, row in df.iterrows():
            graph.add_edge(row['u'], row['v'], row['speed'], row['length'])
        return graph
        

g = Graph.from_csv('svias.csv')

g.print_all_edges()