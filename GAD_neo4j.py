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

    def get_relationships(self, node_idx):
        """
        Get all relationships for a given disease or gene
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
                
            for record in result:
                print(record)

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
    
    # def find_gene(self, gene):
    #     with self.driver.session() as session:
    #         result = session.run("MATCH (g:Gene {name: $gene}) RETURN g.name AS name", gene=gene)
    #         return [record["name"] for record in result]

    # def find_disease(self, disease):
    #     with self.driver.session() as session:
    #         result = session.run("MATCH (d:Disease {name: $disease}) RETURN d.name AS name", disease=disease)
    #         return [record["name"] for record in result]

    # def find_gene_disease(self, gene, disease):
    #     with self.driver.session() as session:
    #         result = session.run("MATCH (g:Gene {name: $gene})-[r:ASSOCIATION]->(d:Disease {name: $disease}) RETURN g.name AS gene, d.name AS disease, r.evidence AS evidence, r.score AS score", gene=gene, disease=disease)
    #         return [record["gene"] for record in result]

    # def find_gene_disease_all(self, gene, disease):
    #     with self.driver.session() as session:
    #         result = session.run("MATCH (g:Gene {name: $gene})-[r:ASSOCIATION]->(d:Disease {name: $disease}) RETURN g.name AS gene, d.name AS disease, r.evidence AS evidence, r.score AS score", gene=gene, disease=disease)
    #         return [record for record in result]

    # def find_gene_disease_all_evidence(self, gene, disease):
    #     with self.driver.session() as session:
    #         result = session.run("MATCH (g:Gene {name: $gene})-[r:ASSOCIATION]->(d:Disease {name: $disease}) RETURN g.name AS gene, d.name AS disease, r.evidence AS evidence, r.score AS score", gene=gene, disease=disease)
    #         return [record["evidence"] for record in result]


def main():
    # create GADGraph object
    gad = GADGraph("bolt://localhost:7687", "neo4j", "password")

    # # clear the database
    # gad.clear_database()

    # # insert nodes and relationships
    # gad.insert_nodes_and_relationships()

    # get relationships for a given node
    gad.get_relationships("19")

    # close the connection
    gad.close()


if __name__ == "__main__":
    main()