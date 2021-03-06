# vars-kb-model-resolve
Specify custom model classes and resolve them to collections of VARS knowledge base concepts.

Author: Kevin Barnard, [kbarnard@mbari.org](mailto:kbarnard@mbari.org)

## Model specification

Define a model specification JSON as follows:

```json
{
    "model_name": "my_model",
    "classes": [
        {
            "label": "my_class",
            "includes": [
                {
                    "concept": "my_concept_a",
                    "include_descendants": true,
                    "part": "self"
                },
                {
                    "concept": "my_concept_b",
                    "include_descendants": true,
                    "part": "some_part"
                }
            ],
            "excludes": [
                {
                    "name": "my_concept_c",
                    "include_descendants": true,
                    "part": "self"
                },
                {
                    "name": "my_concept_d",
                    "include_descendants": false,
                    "part": "some_part"
                }
            ]
        }
    ]
}
```

This model specifies a model named `my_model` with a single class: `my_class`.

This class specifies:
- `my_concept_a` + descendant concepts and 
- `my_concept_b` parts + descendant concept parts named `some_part`

excluding:
- `my_concept_c` + descendant concepts and
- `my_concept_d` parts named `my_part`.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Resolve a model specification to a set of VARS knowledge base concepts:

```bash
python resolve.py <model spec JSON>
```

Check info of model:

```bash
python check.py <resolved model JSON>
```

If the check reports duplicates, that means your model is including the same concept in several classes.

Print model in human-readable format:

```bash
python print.py <resolved model JSON>
```
