# vars-kb-model-resolve
Specify custom model classes and resolve them to collections of taxa names.

Author: Kevin Barnard, [kbarnard@mbari.org](mailto:kbarnard@mbari.org)

## :pencil: Model specification

Define a model specification JSON as follows:

```json
{
    "name": "my_model",
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
                    "concept": "my_concept_c",
                    "include_descendants": true,
                    "part": "self"
                },
                {
                    "concept": "my_concept_d",
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

## :hammer: Setup

```bash
pip install -r requirements.txt
```

## :rocket: Usage

### Resolve 

Resolve a model specification to a set of taxa names:

```bash
python resolve.py <taxa provider> <model spec JSON>
```

> [!NOTE]
> The taxa provider can currently be either `kb` or `fathomnet`.

### Check

Check info of model:

```bash
python check.py <resolved model JSON>
```

If the check reports duplicates, that means your model is including the same concept in several classes.

### Print

Print model in human-readable format:

```bash
python print.py <resolved model JSON>
```
