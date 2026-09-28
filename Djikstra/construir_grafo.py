# pip install networkx sumolib
import pickle
import networkx as nx
import sumolib
import matplotlib.pyplot as plt

NET_FILE = "marilia.net.xml"   

net = sumolib.net.readNet(NET_FILE)

G = nx.DiGraph()

# Nós = edges do SUMO (só as que carros podem usar)
for e in net.getEdges():
    if not e.allows("passenger"):
        continue
    tempo = e.getLength() / e.getSpeed()
    x1, y1 = e.getFromNode().getCoord()
    x2, y2 = e.getToNode().getCoord()
    G.add_node(
        e.getID(),
        length=e.getLength(),
        speed=e.getSpeed(),
        travel_time=tempo,
        from_xy=(x1, y1),
        to_xy=(x2, y2),
        emergency_only=False,   # novo: no futuro, calçadas terão True
    )

# Arestas = conexões permitidas (edge A -> edge B)
# Peso = tempo para percorrer a edge de destino
for e in net.getEdges():
    if e.getID() not in G:
        continue
    saidas = e.getOutgoing()
    saidas = saidas.keys() if isinstance(saidas, dict) else saidas
    for s in saidas:
        if s.getID() in G:
            G.add_edge(e.getID(), s.getID(), weight=G.nodes[s.getID()]["travel_time"])

print("Grafo construído!", flush=True)
print("Nós (edges):", G.number_of_nodes())
print("Arestas (conexões):", G.number_of_edges())

with open("marilia_grafo.pkl", "wb") as f:
    pickle.dump(G, f)


for n, d in G.nodes(data=True):
    (x1, y1), (x2, y2) = d["from_xy"], d["to_xy"]
    plt.plot([x1, x2], [y1, y2], color="gray", linewidth=0.5)

# Imagem
plt.axis("equal")
plt.title("Grafo de Marília (edges)")
plt.show()


# Verificação do grafo
print("\n--- Verificação ---", flush=True)

# 1) Comparar quantidade de edges do SUMO com os nós do grafo
print("Contando edges do SUMO...", flush=True)

n_sumo = sum(
    1 for e in net.getEdges()
    if e.allows("passenger")
)

print("Edges de carro no SUMO:", n_sumo)
print("Nós no grafo:", G.number_of_nodes())
print("Batem?", n_sumo == G.number_of_nodes())


# 2) Verificar conectividade
print("\nCalculando componentes...", flush=True)

componentes = list(nx.strongly_connected_components(G))

print("Componentes calculados!", flush=True)

maior = max(componentes, key=len)

pct = 100 * len(maior) / G.number_of_nodes()

print("Nº de componentes:", len(componentes))
print("Maior componente:", len(maior),
      f"({pct:.1f}% dos nós)")


# 3) Teste de rota com Dijkstra
print("\nCalculando rota de teste dentro da maior componente...", flush=True)

lista = list(maior)

a = lista[0]
b = lista[-1]

rota = nx.dijkstra_path(G, a, b, weight="weight")

print(
    "Rota de teste:", a, "->", b,
    "com", len(rota), "nós e", len(rota) - 1, "conexões"
)