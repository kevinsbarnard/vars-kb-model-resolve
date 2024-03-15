"""
Check out a model.
"""

import argparse
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

from models import Concept, Model


def get_all_concepts(model: Model) -> Set[Concept]:
    """
    Get a set of all concepts in the model.
    """
    return {
        concept for model_class in model.classes for concept in model_class.concepts
    }


def get_overlapping_concepts(model: Model) -> Set[Concept]:
    """
    Get a set of concepts that are present in multiple classes.
    """
    all_concepts = set()
    overlapping_concepts = set()
    for model_class in model.classes:
        overlapping_concepts.update(all_concepts & set(model_class.concepts))
        all_concepts.update(model_class.concepts)
    return overlapping_concepts


def get_concept_map(model: Model) -> Iterable[Tuple[Concept, List[str]]]:
    """
    Generate concept -> list of class labels that have the concept.
    """
    for concept in get_overlapping_concepts(model):
        yield concept, [
            model_class.label
            for model_class in model.classes
            if concept in model_class.concepts
        ]


def get_duplicate_concepts(model: Model) -> Dict[Concept, List[str]]:
    """
    Get a dictionary of duplicated (present in multiple classes) concept -> list of class labels.
    """
    return filter(lambda pair: len(pair[1]) > 1, get_concept_map(model))


def check_model(model: Model):
    """
    Print summary info for a model.
    """
    print(f"Name: {model.name}")
    print(f"Classes: {len(model.classes)}")
    print(f"Concepts: {len(get_all_concepts(model))}")
    print("Duplicates:")
    for concept, class_labels in get_duplicate_concepts(model):
        print(
            f"  {concept.concept} ({concept.part}) is present in {len(class_labels)} classes:"
        )
        for label in class_labels:
            print(f"    {label}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=str, help="Model file to check.")

    args = parser.parse_args()

    # Check model file existence
    model_file = Path(args.model)
    if not model_file.is_file():
        parser.error(f'Model file "{model_file}" does not exist.')

    # Read model
    try:
        model = Model.from_json(model_file.read_text())
    except Exception as e:
        parser.error(f'Error reading model file "{model_file}": {e}')

    # Run check
    check_model(model)


if __name__ == "__main__":
    main()
