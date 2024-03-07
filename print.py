"""
Print a model in a human-readable format.
"""

import argparse
from pathlib import Path

from models import Model


def print_model(model: Model):
    """
    Print model in human-readable format.
    """
    for model_class in model.classes:
        print(f"{model_class.label}:")
        for concept in sorted(
            model_class.concepts, key=(lambda concept: (concept.concept, concept.part))
        ):
            print(
                f"- {concept.concept}"
                + (f" ({concept.part})" if concept.part != "self" else "")
            )
        print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path, help="Model file to print.")

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
    print_model(model)


if __name__ == "__main__":
    main()
