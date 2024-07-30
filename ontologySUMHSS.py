import fitz  # PyMuPDF
from owlready2 import *

def extract_outline(pdf_path):
    """
    Extract the table of contents from the PDF.
    """
    doc = fitz.open(pdf_path)
    outline = doc.get_toc()  # Returns a list of lists
    
    parsed_outline = []
    for item in outline:
        level = item[0]
        title = item[1]
        page_num = item[2]
        parsed_outline.append((title, page_num, level))
    
    return parsed_outline

def parse_outline(outline):
    """
    Parse the extracted outline into a hierarchical structure.
    """
    ontology_structure = {}
    current_parents = {0: ontology_structure}  # Dictionary to keep track of the current parent at each level

    for title, page, level in outline:
        # Clean the title to create a valid class name
        cleaned_title = title.replace(' ', '').replace('-', '').replace(',', '').replace('(', '').replace(')', '')
        
        # Ensure uniqueness if there are duplicate titles
        if cleaned_title in current_parents[level - 1]:
            cleaned_title = f"{cleaned_title}_page{page}"  
        
        # Nest the current title under its parent in the hierarchy
        current_parents[level - 1][cleaned_title] = {}
        current_parents[level] = current_parents[level - 1][cleaned_title]

    return ontology_structure

def create_ontology(structure, onto_name="http://example.org/ontology"):
    """
    Create an ontology from the hierarchical structure.
    """
    onto = get_ontology(onto_name)

    def add_classes(parent, structure, level=0):
        """
        Recursively add classes to the ontology based on the hierarchical structure.
        """
        for class_name, subclasses in structure.items():
            safe_class_name = f"Level{level}_{class_name}"
            try:
                new_class = types.new_class(safe_class_name, (parent,))
                print(f"Created class: {new_class}")
            except TypeError as e:
                print(f"Error creating class '{safe_class_name}': {e}")
                continue
            if subclasses:
                add_classes(new_class, subclasses, level + 1)
    
    with onto:
        # Start with a root class
        class Root(Thing): pass
        add_classes(Root, structure)

    return onto

# Main execution block
if __name__ == "__main__":
    # Define the path to your PDF file
    pdf_path = ' '  # Replace with the actual path to your PDF

    # Step 1: Extract the PDF outline
    pdf_outline = extract_outline(pdf_path)
    print("Extracted PDF Outline:")
    for title, page, level in pdf_outline:
        print(f"{'  ' * (level - 1)}{title} (Page {page})")

    # Step 2: Parse the outline into a hierarchical structure
    ontology_structure = parse_outline(pdf_outline)
    print("\nParsed Ontology Structure:")
    print(ontology_structure)

    # Step 3: Create the ontology and save it as an OWL file
    ontology = create_ontology(ontology_structure)
    ontology.save(file="ontologyNSUMHSS.owl", format="rdfxml")
    print("\nOntology created and saved as ontologyNSUMHSS.owl")
