"""
Resolve model specifications.
"""

import argparse
from pathlib import Path
from typing import List

from requests import HTTPError

from kb import VARSKBClient
from models import Class, ClassSpec, Concept, ConceptSpec, Model, ModelSpec

DEFAULT_KB_URL = 'http://dsg.mbari.org/kb/v1'


class ConceptNotFoundException(Exception):
    def __init__(self, concept: str):
        self.concept = concept
    
    @property
    def message(self):
        return f'Concept "{self.concept}" not found.'


def get_concepts(kb_client: VARSKBClient, concept_spec: ConceptSpec) -> List[Concept]:
    """
    Get a list of concepts for a given concept specification. 
    Raise an error if the concept specification is invalid.
    """
    # Look up the taxa for the specified concept
    try:
        taxa = kb_client.get_taxa(concept_spec.concept)
    except HTTPError as e:
        if e.response.status_code == 404:
            raise ConceptNotFoundException(concept_spec.concept)
        else:
            raise e
    
    # Collect a list of concepts from the response
    concepts = []
    for taxon in taxa:
        concepts.append(Concept(taxon['name'], concept_spec.part))
        if not concept_spec.include_descendants:  # The first taxon is the concept itself
            break
    
    return concepts


def resolve_class(kb_client: VARSKBClient, class_spec: ClassSpec) -> Class:
    """
    Resolve a class specification to a class.
    """
    concepts = set()
    
    # Union with the concepts for each include
    for concept_spec in class_spec.includes:
        try:
            include_concepts = get_concepts(kb_client, concept_spec)
        except ConceptNotFoundException as e:
            print(e.message)
        else:
            concepts.update(include_concepts)
    
    # Subtract the concepts for each exclude
    for concept_spec in class_spec.excludes:
        try:
            exclude_concepts = get_concepts(kb_client, concept_spec)
        except ConceptNotFoundException as e:
            print(e.message)
        else:
            concepts.difference_update(exclude_concepts)
    
    return Class(class_spec.label, list(concepts))


def resolve_model(kb_client: VARSKBClient, model_spec: ModelSpec) -> Model:
    """
    Resolve a model specification to a model.
    """
    classes = []
    
    # Resolve each class
    for class_spec in model_spec.classes:
        classes.append(resolve_class(kb_client, class_spec))
    
    return Model(model_spec.name, classes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', help='Model specification file.')
    parser.add_argument('-o', '--output', default='model.json', help='Output file.')
    parser.add_argument('--kb', default=DEFAULT_KB_URL, help='Knowledge base URL. Default: %(default)s')
    args = parser.parse_args()
    
    # Load the model specification
    model_spec_file = Path(args.model)
    if not model_spec_file.is_file():
        parser.error(f'Model specification file "{model_spec_file}" not found.')
    with open(args.model) as f:
        model_spec = ModelSpec.from_json(f.read())
    
    # Connect to the KB
    kb_client = VARSKBClient(args.kb)
    
    # Resolve the model
    model = resolve_model(kb_client, model_spec)
    
    # Write the model to a file
    model_file = Path(args.output)
    model_file.parent.mkdir(parents=True, exist_ok=True)  # Create the output directory if it doesn't exist
    model_file.write_text(model.to_json(indent=2))
    print(f'Wrote model to {model_file}')


if __name__ == '__main__':
    main()