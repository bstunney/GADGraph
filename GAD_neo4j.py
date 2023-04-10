"""
Query GAD database from Neo4j
"""

import neo4j

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


    def list_nodes(self):
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

    def count_relationships(self):
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

    def get_associations(self, node_idx):
        """
        Get all associations for a given disease or gene
        :param node_idx: index of gene or disease node
        :type node_idx: str
        """

        # query to check if node_idx matches a gene node's geneId
        gene_query = """
        MATCH (g:Gene {geneId: $node_idx})-[r:ASSOCIATION]-(d:Disease)
        RETURN g.geneSymbol as geneSymbol, r.score AS score, d.diseaseName AS diseaseName
        ORDER BY score DESC
        """

        # query to check if node_idx matches a disease node's diseaseId
        disease_query = """
        MATCH (d:Disease {diseaseId: $node_idx})-[r:ASSOCIATION]-(g:Gene)
        RETURN d.diseaseName as diseaseName, r.score AS score, g.geneSymbol AS geneSymbol
        ORDER BY score DESC
        """

        with self._driver.session() as session:
            result = session.run(gene_query, node_idx=str(node_idx))

            # check if results is empty
            if not result.peek():
                result = session.run(disease_query, node_idx=str(node_idx))

            # check if results is empty
            if not result.peek():
                print("No gene or disease node with index", str(node_idx), "found.")
                return
            else:
                for record in result:
                    print(record)
    
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
                
    def graph_projection(self):
        """
        Project graph onto genes and diseases.
        """

        query = """
        CALL gds.graph.create.cypher(
            'gad',
            'MATCH (g:Gene) RETURN id(g) AS id',
            'MATCH (g:Gene)-[r:ASSOCIATION]-(d:Disease) RETURN id(g) AS source, id(d) AS target'
        )
        """

        with self._driver.session() as session:
            result = session.run(query)
            for record in result:
                print(record)

    def drop_graph_projection(self):
        """
        Drop graph.
        """

        query = """
        CALL gds.graph.drop('gad')
        """

        with self._driver.session() as session:
            result = session.run(query)
            for record in result:
                print(record)
                
    def genes_degree_centraility(self):
        """
        Get degree centrality for all genes in the graph.
        """

        query = """
        CALL gds.degree.stream('gad')
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).geneSymbol as geneSymbol, score AS score
        ORDER BY score DESC, geneSymbol DESC
        """

        with self._driver.session() as session:
            result = session.run(query)

            gene_count = 0
            for record in result:

                # check if geneSymbol is not null
                if record['geneSymbol'] is not None:
                    print(record)

                    # count genes
                    gene_count += 1
                
                if gene_count == 10:
                    break

    def disease_degree_centraility(self):
        """
        Get degree centrality for all diseases in the graph.
        """

        query = """
        CALL gds.degree.stream('gad')
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).diseaseName as diseaseName, score AS score
        ORDER BY score DESC, diseaseName DESC
        """

        with self._driver.session() as session:
            result = session.run(query)

            disease_count = 0
            for record in result:

                # check if diseaseName is not null
                if record['diseaseName'] is not None:
                    print(record)

                    # count diseases
                    disease_count += 1

                if disease_count == 10:
                    break


                
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
    # gad.clear_database()

    # insert nodes and relationships
    # gad.insert_nodes_and_relationships()

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
    gad.disease_degree_centraility()

    # close the connection
    gad.close()


if __name__ == "__main__":
    main()