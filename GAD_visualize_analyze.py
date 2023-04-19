
import networkx as nx
import matplotlib.pyplot as plt

class GADVisualizeAnalyze():

    def __init__(self):
        """
        Initialize GADVisualizeAnalyze class
        """

        # create a graph
        self.G = nx.Graph()

    def set_graph(self, graph):
        """
        Set graph to instance variable G

        :param graph: graph
        :type graph: networkx.classes.graph.Graph
        """

        # set graph
        self.G = graph

    def create_graph(self, edges_list, genes = None, diseases = None):
        """
        Create a graph from a list of edges

        :param edges_list: list of edges
        :type edges_list: list
        :param genes: list of genes
        :type genes: list
        :param diseases: list of diseases
        :type diseases: list
        :return: graph
        :rtype: networkx.classes.graph.Graph
        """

        # add nodes with attributes
        if (genes is not None) and (diseases is not None):
            self.G.add_nodes_from(genes, type='gene')
            self.G.add_nodes_from(diseases, type='disease')

        # add edges
        self.G.add_edges_from(edges_list)

    def draw_graph(self, title = None):
        """
        Draw graph from instance variable G
        """

        # create figure
        plt.figure(figsize=(10, 8))
        ax = plt.gca()

        # set title
        if title is not None:
            ax.set_title(title)

        # draw graph
        nx.draw_networkx(self.G, with_labels=True, font_weight='bold', ax=ax)

        # show graph
        plt.show()
        plt.close('all')

    def recursive_search(self, node, min_num, seen = None):
        """
        Recursively search for nodes with min_num or greater edges
        
        :param node: geneSymbol or diseaseName
        :type node: str
        :param min_num: int minimum number of edges from node
        :type min_num: int
        :param seen: nodes added to subgraph
        :type seen: set
        :return: nodes in subgraph
        :rtype: set
        """

        # seen is new set of nodes if not recurred yet
        if seen is None:
            seen = set([node])

        # add all nodes that have min_num or greater edges
        for neighbor in self.G.neighbors(node):
            if neighbor not in seen:
                if len(list(self.G.neighbors(neighbor))) > int(min_num):

                    # recurse if node has min_num or greater edges
                    seen.add(neighbor)
                    self.recursive_search(neighbor, min_num, seen)

        # return subgraph nodes
        return seen
    
    def create_subgraph(self, nodes):
        """
        Create subgraph from node with min_num or greater edges
        
        :param nodes: list of nodes
        :type nodes: list
        :return: subgraph
        :rtype: networkx.classes.graph.Graph
        """

        # create subgraph
        subgraph = nx.subgraph(self.G, list(nodes))

        # return subgraph
        return subgraph
    
    def get_graph(self):
        """
        Return graph

        :return: graph
        :rtype: networkx.classes.graph.Graph
        """

        # return graph
        return self.G
