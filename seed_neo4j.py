"""
Neo4j Seed Script — Molecular Intel Agent
Run this to populate the knowledge graph with oncology data.
Usage: python seed_neo4j.py
"""

import os
from neo4j import GraphDatabase

# ── Connection ──────────────────────────────────────────────────────────────
try:
    import streamlit as st
    URI      = st.secrets["NEO4J_URI"]
    USERNAME = st.secrets.get("NEO4J_USER") or st.secrets.get("NEO4J_USERNAME", "neo4j")
    PASSWORD = st.secrets["NEO4J_PASSWORD"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    URI      = os.getenv("NEO4J_URI")
    USERNAME = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME", "neo4j")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

# ── Seed Data ────────────────────────────────────────────────────────────────
# Format: (gene, mutation_name, drug, response_rate, outcome_description)
SEED_DATA = [
    # BRCA1
    ("BRCA1", "BRCA1_loss_of_function", "Olaparib",      0.72, "Positive — PARP inhibitor highly effective in BRCA1-mutated breast/ovarian cancer"),
    ("BRCA1", "BRCA1_loss_of_function", "Niraparib",     0.65, "Positive — PARP inhibitor with strong response in BRCA1 carriers"),
    ("BRCA1", "BRCA1_loss_of_function", "Talazoparib",   0.68, "Positive — PARP inhibitor approved for HER2-negative BRCA1 breast cancer"),

    # BRCA2
    ("BRCA2", "BRCA2_loss_of_function", "Olaparib",      0.70, "Positive — PARP inhibitor effective in BRCA2-mutated cancers"),
    ("BRCA2", "BRCA2_loss_of_function", "Rucaparib",     0.62, "Positive — PARP inhibitor for BRCA2-mutated ovarian/prostate cancer"),
    ("BRCA2", "BRCA2_loss_of_function", "Niraparib",     0.63, "Positive — effective maintenance therapy in BRCA2 carriers"),

    # TP53
    ("TP53",  "TP53_mutation",          "APR-246",        0.45, "Partial — restores TP53 function in mutant p53 tumors"),
    ("TP53",  "TP53_mutation",          "Carboplatin",    0.50, "Partial — platinum-based therapy used in TP53-mutated cancers"),
    ("TP53",  "TP53_mutation",          "Pembrolizumab",  0.40, "Partial — immunotherapy response in TP53-mutated tumors"),

    # ERBB2 (HER2)
    ("ERBB2", "ERBB2_amplification",   "Trastuzumab",   0.78, "Positive — HER2-targeted antibody highly effective in ERBB2+ cancers"),
    ("ERBB2", "ERBB2_amplification",   "Pertuzumab",    0.74, "Positive — dual HER2 blockade with trastuzumab improves outcomes"),
    ("ERBB2", "ERBB2_amplification",   "Lapatinib",     0.60, "Positive — dual EGFR/HER2 inhibitor for ERBB2-amplified breast cancer"),
    ("ERBB2", "ERBB2_amplification",   "T-DM1",         0.70, "Positive — antibody-drug conjugate for HER2+ breast cancer"),

    # MYC
    ("MYC",   "MYC_amplification",     "JQ1",            0.42, "Partial — BET bromodomain inhibitor suppresses MYC transcription"),
    ("MYC",   "MYC_amplification",     "Dinaciclib",     0.38, "Partial — CDK inhibitor targeting MYC-driven proliferation"),

    # PIK3CA
    ("PIK3CA","PIK3CA_mutation",        "Alpelisib",     0.64, "Positive — PI3K inhibitor approved for PIK3CA-mutated breast cancer"),
    ("PIK3CA","PIK3CA_mutation",        "Copanlisib",    0.55, "Positive — pan-PI3K inhibitor effective in PIK3CA-mutated tumors"),
    ("PIK3CA","PIK3CA_mutation",        "Everolimus",    0.48, "Partial — mTOR inhibitor used with exemestane in PIK3CA+ breast cancer"),

    # EGFR
    ("EGFR",  "EGFR_mutation",         "Erlotinib",     0.70, "Positive — first-gen EGFR TKI effective in EGFR-mutated NSCLC"),
    ("EGFR",  "EGFR_mutation",         "Osimertinib",   0.80, "Positive — third-gen EGFR TKI, superior in T790M and first-line"),
    ("EGFR",  "EGFR_mutation",         "Gefitinib",     0.68, "Positive — first-gen EGFR TKI for EGFR-mutated lung cancer"),
    ("EGFR",  "EGFR_mutation",         "Afatinib",      0.65, "Positive — second-gen EGFR/HER2 TKI for EGFR-mutated NSCLC"),

    # ALK
    ("ALK",   "ALK_fusion",            "Crizotinib",    0.72, "Positive — first-gen ALK inhibitor for ALK-rearranged NSCLC"),
    ("ALK",   "ALK_fusion",            "Alectinib",     0.82, "Positive — second-gen ALK inhibitor, superior CNS penetration"),
    ("ALK",   "ALK_fusion",            "Brigatinib",    0.75, "Positive — next-gen ALK inhibitor with activity against resistance mutations"),
    ("ALK",   "ALK_fusion",            "Lorlatinib",    0.76, "Positive — third-gen ALK inhibitor for resistant ALK+ NSCLC"),

    # KRAS
    ("KRAS",  "KRAS_G12C",             "Sotorasib",     0.57, "Positive — first approved KRAS G12C inhibitor for NSCLC"),
    ("KRAS",  "KRAS_G12C",             "Adagrasib",     0.55, "Positive — KRAS G12C inhibitor with CNS activity"),
    ("KRAS",  "KRAS_mutation",         "Cetuximab",     0.35, "Partial — anti-EGFR antibody, limited by KRAS mutation status in CRC"),

    # RET
    ("RET",   "RET_fusion",            "Selpercatinib", 0.79, "Positive — highly selective RET inhibitor for RET-mutated/fused cancers"),
    ("RET",   "RET_fusion",            "Pralsetinib",   0.74, "Positive — selective RET inhibitor approved for RET+ NSCLC and thyroid"),

    # APC
    ("APC",   "APC_mutation",          "Cetuximab",     0.42, "Partial — anti-EGFR therapy in APC-mutated colorectal cancer"),
    ("APC",   "APC_mutation",          "FOLFOX",        0.50, "Partial — standard chemotherapy regimen for APC-mutated CRC"),

    # BRAF
    ("BRAF",  "BRAF_mutation",         "Vemurafenib",   0.60, "Positive — BRAF inhibitor for BRAF-mutated melanoma"),
    ("BRAF",  "BRAF_mutation",         "Dabrafenib",    0.62, "Positive — BRAF inhibitor used with trametinib in BRAF+ tumors"),

    # BRAF_V600E
    ("BRAF",  "BRAF_V600E",            "Dabrafenib",    0.70, "Positive — highly effective in BRAF V600E mutated melanoma and NSCLC"),
    ("BRAF",  "BRAF_V600E",            "Vemurafenib",   0.68, "Positive — first approved BRAF V600E inhibitor"),
    ("BRAF",  "BRAF_V600E",            "Encorafenib",   0.72, "Positive — BRAF inhibitor with binimetinib for V600E melanoma"),
    ("BRAF",  "BRAF_V600E",            "Trametinib",    0.65, "Positive — MEK inhibitor combined with BRAF inhibitor for V600E"),

    # PTEN
    ("PTEN",  "PTEN_loss",             "Everolimus",    0.50, "Partial — mTOR inhibitor compensates for PTEN loss"),
    ("PTEN",  "PTEN_loss",             "Alpelisib",     0.52, "Partial — PI3K inhibitor effective in PTEN-deficient tumors"),

    # MLH1
    ("MLH1",  "MLH1_deficiency",       "Pembrolizumab", 0.74, "Positive — PD-1 inhibitor highly effective in MSI-H/dMMR tumors"),
    ("MLH1",  "MLH1_deficiency",       "Nivolumab",     0.68, "Positive — PD-1 inhibitor for MLH1-deficient MSI-H cancers"),
    ("MLH1",  "MLH1_deficiency",       "Ipilimumab",    0.55, "Positive — CTLA-4 inhibitor used in combination for dMMR tumors"),

    # NRAS
    ("NRAS",  "NRAS_mutation",         "Binimetinib",   0.45, "Partial — MEK inhibitor for NRAS-mutated melanoma"),
    ("NRAS",  "NRAS_mutation",         "Cobimetinib",   0.42, "Partial — MEK inhibitor in NRAS-mutated tumors"),

    # CDKN2A
    ("CDKN2A","CDKN2A_deletion",       "Palbociclib",   0.58, "Positive — CDK4/6 inhibitor effective when CDKN2A is lost"),
    ("CDKN2A","CDKN2A_deletion",       "Ribociclib",    0.55, "Positive — CDK4/6 inhibitor for CDKN2A-deleted tumors"),
    ("CDKN2A","CDKN2A_deletion",       "Abemaciclib",   0.57, "Positive — CDK4/6 inhibitor with activity in CDKN2A-loss cancers"),

    # FLT3
    ("FLT3",  "FLT3_ITD",              "Midostaurin",   0.65, "Positive — FLT3 inhibitor approved for FLT3-mutated AML"),
    ("FLT3",  "FLT3_ITD",              "Gilteritinib",  0.70, "Positive — second-gen FLT3 inhibitor for relapsed/refractory AML"),
    ("FLT3",  "FLT3_ITD",              "Quizartinib",   0.62, "Positive — selective FLT3 inhibitor for FLT3-ITD AML"),

    # BCR_ABL1
    ("BCR_ABL1","BCR_ABL1_fusion",     "Imatinib",      0.85, "Positive — first BCR-ABL TKI, transformed CML treatment"),
    ("BCR_ABL1","BCR_ABL1_fusion",     "Dasatinib",     0.82, "Positive — second-gen BCR-ABL TKI with broader kinase coverage"),
    ("BCR_ABL1","BCR_ABL1_fusion",     "Nilotinib",     0.80, "Positive — second-gen BCR-ABL TKI with improved selectivity"),
    ("BCR_ABL1","BCR_ABL1_fusion",     "Ponatinib",     0.72, "Positive — third-gen BCR-ABL TKI active against T315I resistance"),
]


def seed(driver):
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        print("🗑️  Cleared existing data")

        count = 0
        for gene, mutation, drug, response_rate, outcome_desc in SEED_DATA:
            session.run("""
                MERGE (g:Gene {name: $gene})
                MERGE (m:Mutation {name: $mutation})
                MERGE (d:Drug {name: $drug})
                MERGE (o:Outcome {
                    description: $outcome_desc,
                    response_rate: $response_rate
                })
                MERGE (g)-[:HAS_MUTATION]->(m)
                MERGE (m)-[:TARGETED_BY]->(d)
                MERGE (d)-[:HAS_OUTCOME]->(o)
            """, gene=gene, mutation=mutation, drug=drug,
                 response_rate=response_rate, outcome_desc=outcome_desc)
            count += 1
            print(f"  ✅ {gene} → {drug} ({int(response_rate*100)}% response)")

        print(f"\n🎉 Seeded {count} gene-drug relationships successfully!")

        # Verify
        result = session.run("""
            MATCH (g:Gene)-[:HAS_MUTATION]->(m:Mutation)-[:TARGETED_BY]->(d:Drug)-[:HAS_OUTCOME]->(o:Outcome)
            RETURN count(*) as total
        """)
        total = result.single()["total"]
        print(f"📊 Verification: {total} paths in graph")


if __name__ == "__main__":
    print(f"🔗 Connecting to {URI}...")
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    try:
        driver.verify_connectivity()
        print("✅ Connected to Neo4j Aura!")
        seed(driver)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        driver.close()
        print("🔒 Connection closed")
