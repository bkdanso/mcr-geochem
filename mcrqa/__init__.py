"""mcrqa: open QA checker for whole-rock and mineral geochemistry tables.

Flags below-detection values (and uninformative detection limits), above-limit values,
semi-quantitative and partial-digestion methods, unit errors, oxide-total problems,
likely altered samples (LOI, CIA, Ishikawa AI, source descriptions), coordinate problems,
and probable cross-source duplicates. Built for MCR-GeoChem; works on any table in its schema
or on a wide spreadsheet.
"""
__version__ = "1.0.0"

from .checker import FLAG_DOC, flag_analyses, flag_samples, load_rules  # noqa: F401
from .wide import wide_to_long  # noqa: F401
