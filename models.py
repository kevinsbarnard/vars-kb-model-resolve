from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class ConceptSpec:
    concept: str
    include_descendants: bool
    part: str = "self"


@dataclass_json
@dataclass
class ClassSpec:
    label: str
    includes: List[ConceptSpec]
    excludes: List[ConceptSpec]


@dataclass_json
@dataclass
class ModelSpec:
    name: str
    classes: List[ClassSpec]


@dataclass_json
@dataclass
class Concept:
    concept: str
    part: str

    def __hash__(self) -> int:
        return hash((self.concept, self.part))


@dataclass_json
@dataclass
class Class:
    label: str
    concepts: List[Concept]


@dataclass_json
@dataclass
class Model:
    name: str
    classes: List[Class]
