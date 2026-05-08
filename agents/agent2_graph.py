from neo4j import GraphDatabase
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError, Exception):
        return os.getenv(key)

def run(state):
    print("Agent 2 running — querying knowledge graph...")

    uri = get_secret("NEO4J_URI")
    username = get_secret("NEO4J_USER") or get_secret("NEO4J_USERNAME")
    password = get_secret("NEO4J_PASSWORD")
    print(f"URI: {uri}, USER: {username}, PASS set: {password is not None}")
    if not uri:
        raise ValueError("NEO4J_URI is not set.")

    driver = GraphDatabase.driver(uri, auth=(username, password))

    mutations = state['mutations']
    cnvs = state['cnvs']
    all_genes = mutations + cnvs

    if not all_genes:
        print("No mutations found to query")
        state['graph_results'] = []
        return state

    with driver.session() as session:
        result = session.run("""
            MATCH (g:Gene)-[:HAS_MUTATION]->(m:Mutation)
            WHERE g.name IN $genes
            MATCH (m)-[:TARGETED_BY]->(d:Drug)
            MATCH (d)-[:HAS_OUTCOME]->(o:Outcome)
            RETURN g.name AS gene,
                   m.name AS mutation,
                   d.name AS drug,
                   o.response_rate AS response_rate
            ORDER BY o.response_rate DESC
        """, genes=all_genes)
        graph_results = [record.data() for record in result]
        state['graph_results'] = graph_results

    driver.close()
    print(f"Graph results found: {len(graph_results)} matches")
    return state
