from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

# Database connection parameters
username = 'username'
password = 'password'
host = 'localhost'
port = '5432'
database = 'database name'

connection_string = ('postgresql+psycopg2://user:password@127.0.0.1:5432/database name')
engine = create_engine(connection_string)

#insert a namespace?

# Define the base class for declarative models
Base = declarative_base()

# Define the Substance class (mapping to the table)
class Substance(Base):
    __tablename__ = 'substance'
    __table_args__ = {'schema': 'public'}
    substance_id = Column(Integer, primary_key=True, nullable=False)
    substance_code = Column(String(40))
    substance_name = Column(String(80))
    substance_schedule = Column(Integer, default=0)
    other_names = Column(String(80))
    source_dataset = Column(Integer)
    year = Column(Integer)
    parent_category = Column(Integer)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Query the data
substances = session.query(Substance).all()

# Create a graph
g = Graph()

# Define a namespace for our substances
SUBSTANCE = Namespace("http://example.org/substance/")

# Bind the namespace to a prefix for easier reference
g.bind("substance", SUBSTANCE)

for substance in substances:
    # Create a URI for each substance
    substance_uri = URIRef(f"http://example.org/substance/{substance.substance_id}")

    # Add triples using store's add method.
    g.add((substance_uri, RDF.type, SUBSTANCE.Substance))
    g.add((substance_uri, SUBSTANCE.substance_code, Literal(substance.substance_code, datatype=XSD.string)))
    g.add((substance_uri, SUBSTANCE.substance_name, Literal(substance.substance_name, datatype=XSD.string)))
    g.add((substance_uri, SUBSTANCE.substance_schedule, Literal(substance.substance_schedule, datatype=XSD.integer)))
    g.add((substance_uri, SUBSTANCE.other_names, Literal(substance.other_names, datatype=XSD.string)))
    g.add((substance_uri, SUBSTANCE.source_dataset, Literal(substance.source_dataset, datatype=XSD.integer)))
    g.add((substance_uri, SUBSTANCE.year, Literal(substance.year, datatype=XSD.integer)))
    g.add((substance_uri, SUBSTANCE.parent_category, Literal(substance.parent_category, datatype=XSD.integer)))

# Close the session
session.close()

# Serialize the graph to a Turtle file
g.serialize(destination='substances.ttl', format='turtle')

print("Data exported to Turtle file successfully.")
