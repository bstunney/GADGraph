# Riya, Ben

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

def fetch_connected_nodes(G, node , weight_param, seen = None):
    """
    get all neighbors of node of interest
    :param G: graph object
    :param node: int for node id of interest
    :param weight_param: float value for node edge connection threshold
    :param seen: list of nodes for subgraph
    :return: seen: list of nodes for subgraph
    """

    # seen is set for nodes
    seen = set([node])

    # add all immediate neighbors to node
    for neighbor in G.neighbors(node):
        if neighbor not in seen:
            if float(G[node][neighbor]['weight']) >= weight_param:
                seen.add(neighbor)

    # return all nodes in subgraph
    return list(seen)

def recursive_search(G, node, min_num, seen = None):
    """
    recursively get connected nodes if num edges is greater than min_num
    :param G: graph object
    :param node: int value for node of interest
    :param min_num: int minimum number of edges from node
    :param seen: set of nodes added to subgraph
    :return: seen: set of nodes in subgraph
    """

    # seen is new set of nodes if not recurred yet
    if seen == None:
        seen = set([node])

    # add all nodes that have min_num or greater edges
    for neighbor in G.neighbors(node):
        if neighbor not in seen:
            if len(list(G.neighbors(neighbor))) > int(min_num):

                # recurse if node has min_num or greater edges
                seen.add(neighbor)
                recursive_search(G, neighbor,min_num, seen)

    # return subgraph nodes
    return seen

def find_similar_genes(G):
    """
    gets n similar genes to node of interest
    :param G: graph object
    :return:
    """

    # get gene number for similar genes and number of genes to return
    gene_num = int(input("Enter a gene number: "))
    num_genes = int(input("Enter # of similar genes to return: "))

    # get neighbors of node
    lst = fetch_connected_nodes(G, gene_num, 0.6)

    # get all diseases associated with gene of interest
    all_diseases = []
    for disease in lst:
        try:
            all_diseases.append(G.nodes[disease]["diseaseName"])
        except:
            all_diseases.append("disease #" + str(disease))

    # present info abt gene of interest
    print("Requested gene #" + str(gene_num))
    print("Disease associations:", all_diseases)
    print()
    print("Below are the",num_genes,"genes with the highest number of similar disease associations.")
    print("-------------------------------------------")

    cnt = Counter()
    sim_diseases = {}

    # get and count diseases associated with all other genes
    for other_node in list(G.nodes):

        if other_node != gene_num and G.nodes[other_node]["type"] == "gene":
            other_lst = fetch_connected_nodes(G, other_node, 0.6)

            num_matching = len(set(lst) & set(other_lst))
            if list(set(lst) & set(other_lst)) != []:
                sim_diseases[other_node] = list(set(lst) & set(other_lst))
            cnt[other_node] = num_matching

    # present n most similar genes
    for sim in cnt.most_common(num_genes):
        all_sim_diseases = []
        for disease in sim_diseases[int(sim[0])]:
            try:
                all_sim_diseases.append(G.nodes[disease]["diseaseName"])
            except:
                all_sim_diseases.append("disease #"+str(disease))

        print("Gene #" +str(sim[0])+ " ("+ G.nodes[sim[0]]["geneSymbol"] +") has", str(sim[1]), "similar disease association/s.")
        print("Disease associations:", all_sim_diseases)
        print("-------------------------------------------")

def find_common_diseases(G):
    """
    get common diseases
    :param G:
    :return:
    """

    # enter nodes of interest
    while True:
        try:
            print()
            node1 = int(input("Enter the first gene's id: "))
            node2 = int(input("Enter the second gene's id: "))
            s1 = set(fetch_connected_nodes(G, node1, 0.5))
            s2 = set(fetch_connected_nodes(G, node2, 0.5))
            break
        except:
            print()
            print("Node/s entered was not part of graph")
            continue

    print()
    # check length
    if len(s1.intersection(s2)) > 0:
        d = s1.intersection(s2)
        return d
    else:
        return ("No common diseases")

def read_graph(f1, f2, f3):
    """
    read in all data and fill graph
    :param f1: file name 1
    :param f2: file name 2
    :param f3: file name 3
    :return: graph object
    """

    # make graph object
    D = nx.Graph()

    # make df of file1
    ddf = pd.read_csv(f1)

    # add all nodes
    for i in range(len(ddf)):
        disease = ddf.iloc[i]
        D.add_node(int(disease["diseaseId"][1:]),  diseaseName = disease["diseaseName"],
                   diseaseType = disease["diseaseType"], diseaseClass = disease["diseaseClass"],
                   diseaseSemanticType = disease["diseaseSemanticType"], NofGenes = disease["NofGenes"],
                   NofPmids = disease["NofPmids"], type = "disease")


    # make df of file3
    gdf = pd.read_csv(f3)

    # add all nodes
    for i in range(len(gdf)):
        gene = gdf.iloc[i]
        D.add_node(int(gene["geneId"]), geneSymbol=gene["geneSymbol"],DSI=gene["DSI"], DPI=gene["DPI"],
                   PLI=gene["PLI"], protein_class_name=gene["protein_class_name"],protein_class=gene["protein_class"],
                   NofDiseases = gene["NofDiseases"],NofPmids = gene["NofPmids"], type = "gene")

    #make df of file 2
    adf = pd.read_csv(f2)

    # add all edges
    for i in range(len(adf)):
        association = adf.iloc[i]
        D.add_edge(int(association["geneId"]), int(association["diseaseId"][1:]), weight= float(association["score"]) )
        D.nodes[int(association["geneId"])]['type'] = "gene"
        D.nodes[int(association["diseaseId"][1:])]['type'] = "disease"

    print()

    return D

def display_subgraph(G):
    """
    show subgraph of neighbors of node
    :param G: graph object
    :return:
    """

    # get node of interest and min weight for edges
    node = int(input("Enter node to create subgraph for: "))
    weight = float(input("Enter weight to find relationships for the node: "))

    # get neighbors of node
    lst = fetch_connected_nodes(G, node, weight)

    # show subplot
    H = nx.subgraph(G, lst)
    nx.draw_networkx(H, with_labels=True)
    plt.show()

def get_stats(G):
    """
    retrieve some general about network
    :param G: graph object
    :return:
    """

    # get genes with most edges
    cnt1 = Counter()
    for node in list(G.nodes):
        if G.nodes[node]["type"] == "gene":
            lst = fetch_connected_nodes(G, node, 0.6)
            cnt1[node] = len(lst)

    # present info abt genes with most edges
    print()
    print("Top 5 genes with most diseases associated:")
    print("----------------------------------------------------")
    for node_disease_tup in cnt1.most_common(5):
        print("Gene #"+ str(node_disease_tup[0])+ " ("+ G.nodes[node_disease_tup[0]]["geneSymbol"] +") has", node_disease_tup[1], "diseases associated.")

    # get diseases with the most edges
    cnt2 = Counter()
    for node in list(G.nodes):
        if G.nodes[node]["type"] == "disease":
            lst = fetch_connected_nodes(G, node, 0.6)
            cnt2[node] = len(lst)

    # present info about diseases with the most edges
    print()
    print("Top 5 diseases with most genes associated:")
    print("----------------------------------------------------")
    for disease_node_tup in cnt2.most_common(5):
        try:
            print("Disease #" + str(disease_node_tup[0]) + " (" + G.nodes[disease_node_tup[0]]["diseaseName"] + ") has",
                  disease_node_tup[1], "genes associated.")
        except:
            print("Disease #" + str(disease_node_tup[0]) + " has", disease_node_tup[1], "genes associated.")

    # request num of min edges for high association graph
    print()
    min_num_edges = input("Enter minimum number of edges for high association graph: ")
    print("(recommended is 15)")

    # visualize graph
    plt.figure(figsize=(10, 8))
    ax = plt.gca()
    ax.set_title(f'Genes/Diseases with over {min_num_edges} associations')
    lst = recursive_search(G, 6142, min_num_edges, seen=None)
    H = nx.subgraph(G, list(lst))
    nx.draw_networkx(H,with_labels=True, node_color='gray', ax=ax)

    # print all diseases/genes with high associations
    print()
    print(f"Below are the genes/diseases with over {min_num_edges} associations")
    print("--------------------------------------------------------------------")
    for node in lst:
        if G.nodes[node]["type"] == "disease":
            try:
                print("Disease #" + str(node) + " (" + G.nodes[node]["diseaseName"]+")")
            except:
                print("Disease #" + str(node))

        if G.nodes[node]["type"] == "gene":
            print("Gene #" + str(node) + " (" + G.nodes[node]["geneSymbol"]+")")

    plt.show()
    plt.close('all')

def main():

    print("Create Gene Disease Association Graph")
    G = read_graph("diseases.csv", "gad.csv", "genes.csv")
    q = False

    while q == False:
        print("Possible actions to enter: 'subgraph', 'common_diseases', 'similar_genes', 'network_stats', or 'quit'")
        action = input("Enter action: ").lower()

        if action == 'quit':
            break

        elif action == 'subgraph':
            print("Create a subgraph for a given node and weight")
            display_subgraph(G)
            print()

        elif action == 'common_diseases':
            print("Find if there are any common disease(s) between 2 genes")
            print(find_common_diseases(G))
            print()

        elif action == 'similar_genes':

            print("Find similar genes to the inputted gene")
            find_similar_genes(G)
            print()

        elif action == 'network_stats':
            print("Return statistics about gene-disease network.")
            get_stats(G)
            print()

if __name__ == "__main__":
    main()