"""
Resolve model specifications.
"""

import argparse
from abc import ABC
from pathlib import Path
from typing import List, Optional

from fathomnet.api import worms
from requests import HTTPError

from kb import VARSKBClient
from models import Class, ClassSpec, Concept, ConceptSpec, Model, ModelSpec

DEFAULT_KB_URL = "http://dsg.mbari.org/kb/v1"


class ConceptNotFoundException(Exception):
    def __init__(self, concept: str):
        self.concept = concept

    @property
    def message(self):
        return f'Concept "{self.concept}" not found.'


class TaxaProvider(ABC):
    """
    Taxa provider interface.
    """

    def get_descendants_names(self, name: str) -> List[str]:
        """
        Get the list of names of descendants of a given taxon name, including the given name.

        Args:
            name: The name of the taxon.

        Returns:
            The list of names of descendants of the taxon.

        Raises:
            ConceptNotFoundException: If the taxon is invalid.
        """
        raise NotImplementedError


class VARSKBTaxaProvider(TaxaProvider):
    """
    VARS Knowledge Base (KB) taxa provider.
    """

    def __init__(self, kb_client: VARSKBClient):
        self._kb_client = kb_client

    def get_descendants_names(self, name: str) -> Optional[List[str]]:
        try:
            taxa = self._kb_client.get_taxa(name)
        except HTTPError as e:
            if e.response.status_code == 404:
                raise ConceptNotFoundException(name)
            else:
                raise e
        else:
            return [taxon["name"] for taxon in taxa]


class FathomNetWoRMSTaxaProvider(TaxaProvider):
    """
    FathomNet-WoRMS taxa provider.
    """

    def get_descendants_names(self, name: str) -> List[str]:
        return worms.get_descendants_names(name)


def get_concepts(
    taxa_provider: TaxaProvider, concept_spec: ConceptSpec
) -> List[Concept]:
    """
    Get a list of concepts for a given concept specification.

    Args:
        taxa_provider: The taxa provider to use for resolving taxa names.
        concept_spec: The concept specification.

    Returns:
        The list of concepts.

    Raises:
        ConceptNotFoundException: If the concept is not found.
    """
    # Look up the taxa for the specified concept
    taxa_names = taxa_provider.get_descendants_names(concept_spec.concept)

    # Collect a list of concepts from the response
    concepts = []
    for taxon_name in taxa_names:
        concepts.append(Concept(taxon_name, concept_spec.part))
        if (
            not concept_spec.include_descendants
        ):  # The first taxon is the concept itself
            break

    return concepts


def resolve_class(taxa_provider: TaxaProvider, class_spec: ClassSpec) -> Class:
    """
    Resolve a class specification to a class.

    Args:
        taxa_provider: The taxa provider to use for resolving taxa names.
        class_spec: The class specification to resolve.

    Returns:
        The resolved class.
    """
    concepts = set()

    # Union with the concepts for each include
    for concept_spec in class_spec.includes:
        try:
            include_concepts = get_concepts(taxa_provider, concept_spec)
        except ConceptNotFoundException as e:
            print(e.message)
        else:
            concepts.update(include_concepts)

    # Subtract the concepts for each exclude
    for concept_spec in class_spec.excludes:
        try:
            exclude_concepts = get_concepts(taxa_provider, concept_spec)
        except ConceptNotFoundException as e:
            print(e.message)
        else:
            concepts.difference_update(exclude_concepts)

    return Class(class_spec.label, list(concepts))


def resolve_model(taxa_provider: TaxaProvider, model_spec: ModelSpec) -> Model:
    """
    Resolve a model specification to a model.

    Args:
        taxa_provider: The taxa provider to use for resolving taxa names.
        model_spec: The model specification to resolve.
    """
    classes = []

    # Resolve each class
    for class_spec in model_spec.classes:
        classes.append(resolve_class(taxa_provider, class_spec))

    return Model(model_spec.name, classes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(
        title="Provider",
        dest="provider",
        required=True,
        help="The taxa provider to use.",
    )
    kb_subparser = subparsers.add_parser(
        "kb", help="Resolve a model using the VARS knowledge base API."
    )
    kb_subparser.add_argument(
        "--url",
        dest="kb_url",
        default=DEFAULT_KB_URL,
        help="Knowledge base URL. Default: %(default)s",
    )

    fathomnet_subparser = subparsers.add_parser(
        "fathomnet", help="Resolve a model using the FathomNet-WoRMS API."
    )

    parser.add_argument("model", help="Model specification file.")
    parser.add_argument("-o", "--output", default="model.json", help="Output file.")

    args = parser.parse_args()

    taxa_provider_name: str = args.provider

    # Load the model specification
    model_spec_file = Path(args.model)
    if not model_spec_file.is_file():
        parser.error(f'Model specification file "{model_spec_file}" not found.')
    with open(args.model) as f:
        model_spec = ModelSpec.from_json(f.read())

    if taxa_provider_name == "kb":
        # Connect to the KB
        kb_client = VARSKBClient(args.kb_url)
        taxa_provider = VARSKBTaxaProvider(kb_client)
    elif taxa_provider_name == "fathomnet":
        taxa_provider = FathomNetWoRMSTaxaProvider()
    else:
        parser.error(f"Invalid taxa provider: {taxa_provider_name}")

    # Resolve the model
    model = resolve_model(taxa_provider, model_spec)

    # Write the model to a file
    model_file = Path(args.output)
    model_file.parent.mkdir(
        parents=True, exist_ok=True
    )  # Create the output directory if it doesn't exist
    model_file.write_text(model.to_json(indent=2))
    print(f"Wrote model to {model_file}")


if __name__ == "__main__":
    main()
