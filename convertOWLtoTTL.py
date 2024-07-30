from rdflib import Graph

# Load the .owl (RDF/XML) file
g = Graph()
g.parse("substances_ontology.owl", format="xml")

# Serialize the graph into Turtle format and save it to a file
g.serialize(destination="substancesOntology.ttl", format="turtle")
print(f"TTL created and saved")
