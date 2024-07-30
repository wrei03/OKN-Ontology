import rdflib
from rdflib import Graph, Literal, RDF, RDFS, OWL, URIRef, Namespace
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Define the database connection parameters
username = 'username'
password = 'password'
database = 'database name'
host = 'localhost'
port = '5432'

# Connect to the database
engine = create_engine(f'postgresql+psycopg2://username:password@127.0.0.1:5432/database name')
Session = sessionmaker(bind=engine)
session = Session()

# Define namespaces
EX = Namespace("http://example.org/substance#")
SCHEMA = Namespace("http://schema.org/")
OWL_NAMESPACE = Namespace("http://www.w3.org/2002/07/owl#")

# Create an RDF graph and bind namespaces
g = Graph()
g.bind("ex", EX)
g.bind("schema", SCHEMA)
g.bind("owl", OWL_NAMESPACE)

# Define the OWL class for Substance
g.add((EX.Substance, RDF.type, OWL.Class))

# Define the OWL object properties
g.add((EX.isInCategory, RDF.type, OWL.ObjectProperty))

# Define the OWL datatype properties
g.add((EX.hasCode, RDF.type, OWL.DatatypeProperty))
g.add((EX.hasSchedule, RDF.type, OWL.DatatypeProperty))
g.add((EX.hasOtherNames, RDF.type, OWL.DatatypeProperty))
g.add((EX.sourceDataset, RDF.type, OWL.DatatypeProperty))
g.add((EX.year, RDF.type, OWL.DatatypeProperty))

# Query to retrieve all substances
query = text("SELECT * FROM public.substance")
result = session.execute(query)

# Iterate over the database results and add them to the RDF graph
for row in result.mappings():  # Convert to dictionary-like rows for easier access
    substance_uri = EX[f"Substance_{row['substance_id']}"]
    g.add((substance_uri, RDF.type, EX.Substance))
    g.add((substance_uri, SCHEMA.identifier, Literal(row['substance_id'])))
    g.add((substance_uri, RDFS.label, Literal(row['substance_name'])))
    g.add((substance_uri, EX.hasCode, Literal(row['substance_code'])))
    g.add((substance_uri, EX.hasSchedule, Literal(row['substance_schedule'])))
    g.add((substance_uri, EX.hasOtherNames, Literal(row['other_names'])))
    g.add((substance_uri, EX.sourceDataset, Literal(row['source_dataset'])))
    g.add((substance_uri, EX.year, Literal(row['year'])))
    
    # Handle parent category relationship if applicable
    if row['parent_category'] is not None and row['parent_category'] != -1:
        parent_uri = EX[f"Substance_{row['parent_category']}"]
        g.add((substance_uri, EX.isInCategory, parent_uri))

# Define additional OWL ontology metadata (optional)
ontology_uri = EX["SubstanceOntology"]
g.add((ontology_uri, RDF.type, OWL.Ontology))
g.add((ontology_uri, RDFS.comment, Literal("Ontology describing various substances as found in the NSDUH.")))
g.add((ontology_uri, RDFS.label, Literal("Substance Ontology")))

# Save the RDF graph to a file (OWL format)
g.serialize(destination="substances_ontology.owl", format='xml')

print("Ontology file 'substances_ontology.owl' created successfully.")

# Close the database session
session.close()
