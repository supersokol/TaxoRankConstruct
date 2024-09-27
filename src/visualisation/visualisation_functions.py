import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

def add_concepts_to_graph_with_layers(taxonomy, concept, G, layer = 0, order = 0):
    order+=1
    ranks_list = []
    for ranks in taxonomy.taxonomical_ranks:
        try:
            ranks_list.append(ranks.split(',')[layer])
        except:
            pass
    children_stack = []
    for rank in ranks_list:
        target_children = [child for child in concept.children if child.taxonomical_rank == rank]
        if target_children:
            for child in target_children:
                G.add_node(child.name, order = order, layer=layer + 1)
                order+=1
                G.add_edge(concept.name, child.name, label=child.taxonomical_rank)
                children_stack.append(child)
                
    for child in children_stack:
            order = add_concepts_to_graph_with_layers(taxonomy, child, G, layer + 1, order)
            
    return order

def visualize_taxonomy_as_graph_spaced(taxonomy):
    G = nx.DiGraph()
    G.add_node(taxonomy.root.name,order = 0, layer=0)

    add_concepts_to_graph_with_layers(taxonomy, taxonomy.root, G)
    g = G
    max_layer = max([d['layer'] for n, d in g.nodes(data=True)])
    max_nodes_am = 0
    for i in range(0,max_layer+1):
        if len([n for n, d in g.nodes(data=True) if d['layer'] == i])>max_nodes_am:
            max_nodes_am = len([n for n, d in g.nodes(data=True) if d['layer'] == i])
    pos = nx.multipartite_layout(g, subset_key='layer')
    layer_0_node = [n for n, d in g.nodes(data=True) if d['layer'] == 0]
    # For layer '0', I want to sort nodes by the 'order' attribute:
    pos[layer_0_node[0]][1] = max_nodes_am*5

    target_layer = 1
    while target_layer <= max_layer:
        layer_nodes = [n for n, d in g.nodes(data=True) if d['layer'] == target_layer]
        sorted_layer_nodes = sorted(layer_nodes, key=lambda n: g.nodes[n]['order'])
        # Adjust the positions manually
        for i, node in enumerate(sorted_layer_nodes):
            pos[node][1] =  max_nodes_am/len(sorted_layer_nodes)*i*10  # This changes the vertical position (for a vertical layout)
        target_layer += 1
    plt.figure(figsize=(30, 15))
    # Draw the graph with the adjusted positions
    nx.draw(g, pos, with_labels=True, node_size=1500, node_color="lightblue", font_size=10, font_weight="bold", edge_color="gray")
    edge_labels = nx.get_edge_attributes(g, 'label')
    nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, font_size=10)
    plt.show()
    return g


