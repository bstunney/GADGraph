
import networkx as nx
import matplotlib.pyplot as plt

class GADVisualizeAnalyze():

    def __init__(self):

        # create a graph
        self.G = nx.Graph()

    def create_graph(self, edges_list):
        """
        Create a graph from a list of edges

        :param edges_list: list of edges
        :type edges_list: list
        :return: graph
        :rtype: networkx.classes.graph.Graph
        """

        # add edges
        self.G.add_edges_from(edges_list)

    def draw_graph(self):
        """
        Draw graph from instance variable G
        """

        # draw graph
        nx.draw_networkx(self.G, with_labels=True, font_weight='bold')

        # show graph
        plt.show()
