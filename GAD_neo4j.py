"""
Query GAD database from Neo4j
"""

import neo4j
from GAD_visualize_analyze import GADVisualizeAnalyze as GVA

class GADGraph():

    def __init__(self, uri, user, password):
        self._driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Close the driver connection.
        """

        self._driver.close()

    def clear_database(self):
        """
        Clear the database.
        """

        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared.")

    def insert_nodes_and_relationships(self):
        """
        Insert nodes and relationships from csv files into Neo4j database.
        GRAPH SCHEMA:
        Nodes are two types: Gene and Disease
        Relationships are given properties: score, evidence index, evidence level
        """

        # cypher query to insert nodes from genes.csv
        # gene has properties: geneId, geneSymbol, DSI, DPI, PLI, protein_class_name, NofDiseases
        gene_query = """
        LOAD CSV WITH HEADERS FROM "file:///Users/sree/Second2/DS4300/GADGraph/data/genes.csv" AS row
        CREATE (g:Gene {geneId: row.geneId, geneSymbol: row.geneSymbol, DSI: row.DSI, DPI: row.DPI, PLI: row.PLI, protein_class_name: row.protein_class_name, NofDiseases: row.NofDiseases})
        """

        # cypher query to insert nodes from diseases.csv
        # disease has properties: diseaseId, diseaseName, diseaseType, diseaseClass, diseaseSemanticType, NofGenes
        disease_query = """
        LOAD CSV WITH HEADERS FROM "file:///Users/sree/Second2/DS4300/GADGraph/data/diseases.csv" AS row
        CREATE (d:Disease {diseaseId: row.diseaseId, diseaseName: row.diseaseName, diseaseType: row.diseaseType, diseaseClass: row.diseaseClass, diseaseSemanticType: row.diseaseSemanticType, NofGenes: row.NofGenes})
        """

        # cypher query to insert relationships from gad.csv
        # edge has properties: score, evidence index, evidence level
        edges_query = """
        LOAD CSV WITH HEADERS FROM "file:///Users/sree/Second2/DS4300/GADGraph/data/gad.csv" AS row
        MATCH (g:Gene {geneId: row.geneId})
        MATCH (d:Disease {diseaseId: row.diseaseId})
        CREATE (g)-[r:ASSOCIATION {score: row.score, evidence_index: row.evidence_index, evidence_level: row.evidence_level}]->(d)
        RETURN COUNT(r)
        """

        with self._driver.session() as session:
            session.run(gene_query)
            print("Gene nodes inserted.")

            session.run(disease_query)
            print("Disease nodes inserted.")

            result = session.run(edges_query)
            for record in result:
                print("Relationships inserted:", record[0])

            print("Nodes and relationships inserted.")


    def _list_nodes(self):
        """
        List all nodes in the graph.
        """

        query = """
        MATCH (n)
        RETURN n
        """

        with self._driver.session() as session:
            result = session.run(query)
            for record in result:
                print(record)

    def _count_relationships(self):
        """
        Count number of relationships in the graph.
        """

        query = """
        MATCH ()-[r]->()
        RETURN COUNT(r)
        """

        with self._driver.session() as session:
            result = session.run(query)
            for record in result:
                print(record)

    def _parse_results(self, result):
        """
        Parse results from Neo4j query.

        :param result: result from Neo4j query
        :type result: neo4j.Result
        :return: list of edges
        :rtype: list
        """

        # empty list to store edges
        edges = []

        # iterate through result
        for record in result:
            edges.append((record[0], record[2]))

        # return edges
        return edges
    
    def _visualize(self, result):
        """
        _summary_

        :param result: _description_
        :type result: _type_
        """

        # parse results
        edges = self._parse_results(result)

        # visualize results
        gva = GVA()

        # add nodes
        gva.create_graph(edges)

        # visualize graph
        gva.draw_graph()

    def get_associations(self, node_idx, score_threshold=0.0):
        """
        Get all associations for a given disease or gene
        :param node_idx: index of gene or disease node
        :type node_idx: str
        :param score_threshold: score threshold for association, defaults to 0.0
        :type score_threshold: float, optional
        """

        # query to check if node_idx matches a gene node's geneId
        gene_query = """
        MATCH (g:Gene {geneId: $node_idx})-[r:ASSOCIATION]-(d:Disease)
        WHERE toFloat(r.score) >= $score
        RETURN g.geneSymbol as geneSymbol, r.score AS score, d.diseaseName AS diseaseName
        ORDER BY score DESC
        """

        # query to check if node_idx matches a disease node's diseaseId
        disease_query = """
        MATCH (d:Disease {diseaseId: $node_idx})-[r:ASSOCIATION]-(g:Gene)
        WHERE toFloat(r.score) >= $score
        RETURN d.diseaseName as diseaseName, r.score AS score, g.geneSymbol AS geneSymbol
        ORDER BY score DESC
        """

        with self._driver.session() as session:
            result = session.run(gene_query, node_idx=str(node_idx), score=score_threshold)

            # check if results is empty
            if not result.peek():
                result = session.run(disease_query, node_idx=str(node_idx), score=score_threshold)

            # check if results is empty
            if not result.peek():
                print("No gene or disease node with index", str(node_idx), "found.")
                return
            else:

                # visualize the results
                self._visualize(result)
                
    
    def get_gene_details(self, gene):
        """
        Get details of a gene from its geneId or geneSymbol

        :param gene: geneId or geneSymbol
        :type gene: str
        :return: geneSymbol or geneId
        :rtype: str
        """

        # get details of a gene from its geneId
        geneId_query = """
        MATCH (g:Gene {geneId: $gene})
        RETURN g.geneSymbol as geneSymbol, g.DSI AS DSI, g.DPI AS DPI, g.PLI AS PLI, g.protein_class_name AS protein_class_name, g.NofDiseases AS NofDiseases
        """

        # get details of a gene from its geneSymbol
        geneSymbol_query = """
        MATCH (g:Gene {geneSymbol: $gene})
        RETURN g.geneId as geneId, g.DSI AS DSI, g.DPI AS DPI, g.PLI AS PLI, g.protein_class_name AS protein_class_name, g.NofDiseases AS NofDiseases
        """

        with self._driver.session() as session:
            result = session.run(geneId_query, gene=str(gene))
            
            # check if results is empty
            if not result.peek():
                result = session.run(geneSymbol_query, gene=str(gene))
            else:
                for record in result:
                    print(record)

                    # return geneSymbol
                    return record['geneSymbol']

            # check if results is empty
            if not result.peek():
                print("No gene with index or symbol", str(gene), "found.")
                return
            else:
                for record in result:
                    print(record)

                    # return geneId
                    return record['geneId']

    def get_disease_details(self, disease):
        """
        Get details of a disease from its diseaseId or diseaseName

        :param disease: diseaseId or diseaseName
        :type disease: str
        :return: diseaseName or diseaseId
        :rtype: str
        """

        # get details of a disease from its diseaseId
        diseaseId_query = """
        MATCH (d:Disease {diseaseId: $disease})
        RETURN d.diseaseName as diseaseName, d.diseaseSemanticType as diseaseSemanticType, d.NofGenes AS NofGenes
        """

        # get details of a disease from its diseaseName
        diseaseName_query = """
        MATCH (d:Disease {diseaseName: $disease})
        RETURN d.diseaseId as diseaseId, d.diseaseSemanticType as diseaseSemanticType, d.NofGenes AS NofGenes
        """

        with self._driver.session() as session:
            result = session.run(diseaseId_query, disease=str(disease))
            
            # check if results is empty
            if not result.peek():
                result = session.run(diseaseName_query, disease=str(disease))
            else:
                for record in result:
                    print(record)

                    # return diseaseName
                    return record['diseaseName']

            # check if results is empty
            if not result.peek():
                print("No disease with index or name", str(disease), "found.")
                return
            else:
                for record in result:
                    print(record)

                    # return diseaseId
                    return record['diseaseId']
                
    def _reverse_graph_projection(self, node_type):
        """
        Project reverse graph onto genes or diseases.

        :param node_type: node type to project onto
        :type node_type: str
        """

        # project reverse graph onto genes or diseases
        query = """
        CALL gds.graph.project.cypher(
            'reverse_gad',
            $node_type,
            {
                ASSOCIATION: {
                    orientation: 'REVERSE',
                    properties: 'score'
                }
            }
        )
        """

        with self._driver.session() as session:
            session.run(query, node_type=str(node_type))
            # for record in result:
            #     print(record)

    def _drop_graph_projection(self, graph_name):
        """
        Drop graph if it exists.

        :param graph_name: name of graph to drop
        :type graph_name: str
        """

        # check if graph exists
        exists_query = """
        CALL gds.graph.exists($graph_name)
            YIELD exists
        RETURN exists
        """

        # drop graph if it exists
        query = """
        CALL gds.graph.drop($graph_name)
        """

        with self._driver.session() as session:

            # check if graph exists
            result = session.run(exists_query, graph_name=str(graph_name))
            for record in result:
                if record['exists']:
                    print("Graph", graph_name, "exists. Dropping graph projection.")
                    result = session.run(query, graph_name=str(graph_name))
                    for record in result:
                        print(record)
                else:
                    print("Graph", graph_name, "does not exist.")
                
    def genes_degree_centraility(self):
        """
        Get degree centrality for all genes in the graph.
        """

        # drop graph if it exists
        self._drop_graph_projection('reverse_gad')

        # project reverse graph onto genes
        self._reverse_graph_projection('Gene')

        query = """
        CALL gds.degree.stream('reverse_gad')
        YIELD nodeId, score
        WHERE gds.util.asNode(nodeId).geneSymbol IS NOT NULL
        RETURN gds.util.asNode(nodeId).geneSymbol as geneSymbol, score AS score
        ORDER BY score DESC, geneSymbol DESC
        LIMIT 10
        """

        with self._driver.session() as session:
            result = session.run(query)

            for record in result:
                print(record)

    def disease_degree_centraility(self):
        """
        Get degree centrality for all diseases in the graph.
        """

        # drop graph if it exists
        self._drop_graph_projection('reverse_gad')

        # project reverse graph onto diseases
        self._reverse_graph_projection('Disease')

        query = """
        CALL gds.degree.stream('gad')
        YIELD nodeId, score
        WHERE gds.util.asNode(nodeId).diseaseName IS NOT NULL
        RETURN gds.util.asNode(nodeId).diseaseName as diseaseName, score AS score
        ORDER BY score DESC, diseaseName DESC
        LIMIT 10
        """

        with self._driver.session() as session:
            result = session.run(query)

            for record in result:
                print(record)

    def find_common_dieases(self, gene1, gene2, score1=0.0, score2=0.0):
        """
        Find common diseases between two genes.

        :param gene1: geneId of gene 1
        :type gene1: str
        :param gene2: geneId of gene 2
        :type gene2: str
        :param score1: score threshold for gene 1
        :type score1: float
        :param score2: score threshold for gene 2
        :type score2: float
        :return: common diseases between gene 1 and gene 2
        :rtype: `Result`
        """

        query = """
        MATCH (g1:Gene {geneId: $gene1})
        MATCH (g2:Gene {geneId: $gene2})
        MATCH (g1)-[r1:ASSOCIATION]->(d:Disease)
        MATCH (g2)-[r2:ASSOCIATION]->(d)
        WHERE toFloat(r1.score) >= $score1 AND toFloat(r2.score) >= $score2
        RETURN d.diseaseName as diseaseName, r1.score as score1, r2.score as score2
        """

        with self._driver.session() as session:
            result = session.run(query, gene1=str(gene1), gene2=str(gene2), score1=float(score1), score2=float(score2))

            for record in result:
                print(record)

            return result
        
    def find_common_genes(self, disease1, disease2, score1=0.0, score2=0.0):
        """
        Find common genes between two diseases.

        :param disease1: diseaseId of disease 1
        :type disease1: str
        :param disease2: diseaseId of disease 2
        :type disease2: str
        :param score1: score threshold for disease 1
        :type score1: float
        :param score2: score threshold for disease 2
        :type score2: float
        :return: common genes between disease 1 and disease 2
        :rtype: `Result`
        """

        query = """
        MATCH (d1:Disease {diseaseId: $disease1})
        MATCH (d2:Disease {diseaseId: $disease2})
        MATCH (d1)-[r1:ASSOCIATION]->(g:Gene)
        MATCH (d2)-[r2:ASSOCIATION]->(g)
        WHERE toFloat(r1.score) >= $score1 AND toFloat(r2.score) >= $score2
        RETURN g.geneSymbol as geneSymbol, r1.score as score1, r2.score as score2
        """

        with self._driver.session() as session:
            result = session.run(query, disease1=str(disease1), disease2=str(disease2), score1=float(score1), score2=float(score2))

            for record in result:
                print(record)

            return result
        
    def most_connected_genes(self, score=0.0, limit=5):
        """
        Find most connected genes in the graph.

        :param score: score threshold
        :type score: float
        :param limit: number of results to return
        :type limit: int
        :return: most connected genes in the graph
        :rtype: `Result`
        """

        query = """
        MATCH (g:Gene)-[r:ASSOCIATION]->(d:Disease)
        WHERE toFloat(r.score) >= $score
        RETURN g.geneSymbol as geneSymbol, count(d) as count
        ORDER BY count DESC, geneSymbol DESC
        LIMIT $limit
        """

        with self._driver.session() as session:
            result = session.run(query, score=float(score), limit=int(limit))

            for record in result:
                print(record)

            return result
    
    def most_connected_diseases(self, score=0.0, limit=5):
        """
        Find most connected diseases in the graph.

        :param score: score threshold
        :type score: float
        :param limit: number of results to return
        :type limit: int
        :return: most connected diseases in the graph
        :rtype: `Result`
        """

        query = """
        MATCH (d:Disease)-[r:ASSOCIATION]->(g:Gene)
        WHERE toFloat(r.score) >= $score
        RETURN d.diseaseName as diseaseName, count(g) as count
        ORDER BY count DESC, diseaseName DESC
        LIMIT $limit
        """

        with self._driver.session() as session:
            result = session.run(query, score=float(score), limit=int(limit))

            for record in result:
                print(record)

            return result
      
    def show_graph(self):
        """
        Show the graph in Neo4j database.
        """

        # display all nodes and relationships in the graph
        query = """
        MATCH (n)
        MATCH (n)-[r]-()
        RETURN n, r
        """

        with self._driver.session() as session:
            result = session.run(query)
            for record in result:
                print(record)

def main():

    # create GADGraph object
    gad = GADGraph("bolt://localhost:7687", "neo4j", "password")

    # clear the database
    gad.clear_database()

    # insert nodes and relationships
    gad.insert_nodes_and_relationships()

    # user input
    q = False

    while q == False:
        print("Possible actions to enter: 'gene details', 'disease details', 'subgraph', 'common_diseases', 'common genes', 'similar genes', 'network stats', or 'quit'")

        # enter an action
        action = input("Enter an action: ").lower()

        # quit the program
        if action == 'quit':
            q = True

        # gene details
        elif action == 'gene details':
            print("\nFind details about a gene")
            gene = str(input("Enter gene id or gene symbol to get full details for: "))

            # get gene details
            gad.get_gene_details(gene)

        # disease details
        elif action == 'disease details':
            print("\nFind details about a disease")
            disease = str(input("Enter disease id or disease name to get full details for: "))

            # get disease details
            gad.get_disease_details(disease)

        # subgraph
        elif action == 'subgraph':
            print("\nCreate a subgraph for a given node and threshold for score of association")
            node_idx = str(input("Enter node index to create subgraph for: "))
            score = float(input("Enter score to find relationships for the node: "))

            # create subgraph
            gad.get_associations(node_idx, score)            

        # common diseases
        elif action == 'common diseases':
            print("\nFind if there are any common disease(s) between 2 genes (with optional score thresholds)")
            node1 = int(input("Enter the first gene's id: "))
            node2 = int(input("Enter the second gene's id: "))

            # default score thresholds
            score1 = 0.0
            score2 = 0.0

            # ask user if they want to enter score thresholds
            ans1 = input("Do you want to enter a score threshold for the first gene? (y/n)")

            # if yes, get score threshold
            if ans1 == 'y':
                score1 = float(input("Enter score threshold for the first gene: "))

            ans2 = input("Do you want to enter a score threshold for the second gene? (y/n)")

            if ans2 == 'y':
                score2 = float(input("Enter score threshold for the second gene: "))

            # find common diseases
            gad.find_common_dieases(node1, node2, score1, score2)

        # common genes
        elif action == 'common genes':
            print("\nFind if there are any common gene(s) between 2 diseases (with optional score thresholds)")
            node1 = int(input("Enter the first disease's id: "))
            node2 = int(input("Enter the second disease's id: "))

            # default score thresholds
            score1 = 0.0
            score2 = 0.0

            # ask user if they want to enter score thresholds
            ans1 = input("Do you want to enter a score threshold for the first disease? (y/n)")

            # if yes, get score threshold
            if ans1 == 'y':
                score1 = float(input("Enter score threshold for the first disease: "))

            ans2 = input("Do you want to enter a score threshold for the second disease? (y/n)")

            if ans2 == 'y':
                score2 = float(input("Enter score threshold for the second disease: "))

            # find common diseases
            gad.find_common_genes(node1, node2, score1, score2)

        # elif action == 'similar genes':

        #     print("\nFind similar genes to the inputted gene")
        #     find_similar_genes(G)
        #     print()
        
        # network stats
        elif action == 'network stats':
            print("\nReturn statistics about gene-disease network.")

            # ask what statistics to return
            # print("Enter 'degree centrality' to return degree centrality for genes and diseases.")
            print("Enter 'most connected genes' to return the most connected genes in the graph.")
            print("Enter 'most connected diseases' to return the most connected diseases in the graph.")

            # get user input
            ans = input("Enter an action: ")

            # degree centrality
            # if ans == 'degree centrality':
            #     print("\nDegree centrality for genes and diseases:")
            #     gad.genes_degree_centraility()
            #     gad.disease_degree_centraility()

            # most connected genes
            if ans == 'most connected genes':
                print("\nMost connected genes in the graph.")
                gad.most_connected_genes()

            # most connected diseases
            elif ans == 'most connected diseases':
                print("\nMost connected diseases in the graph.")
                gad.most_connected_diseases()

    # get gene details
    # geneID = gad.get_gene_details("ABCA1")

    # get disease details
    # diseaseID = gad.get_disease_details("Tangier Disease")

    # get associations for a given node
    # gad.get_associations(geneID)

    # get associations for a given node
    # gad.get_associations(diseaseID)

    # genes degree centrality
    # gad.genes_degree_centraility()

    # diseases degree centrality
    # gad.disease_degree_centraility()

    # find common diseases between two genes
    # gad.find_common_dieases('24', '1406', 0.0, 0.0)

    # close the connection
    gad.close()


if __name__ == "__main__":
    main()