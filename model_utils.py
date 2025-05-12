# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import typing
from collections.abc import Iterable
from typing import Optional

from aqt import mw

AnkiCardSide = typing.Literal["qfmt", "afmt"]


class AnkiCardTemplateDict(typing.TypedDict):
    qfmt: str
    afmt: str
    name: str  # card template name, e.g. "recognition", "production".


class AnkiNoteTypeFieldDict(typing.TypedDict):
    name: str
    ord: int
    # omitted other keys


class AnkiNoteTypeDict(typing.TypedDict):
    tmpls: list[AnkiCardTemplateDict]
    css: str
    name: str  # model name
    flds: list[AnkiNoteTypeFieldDict]


def get_model_field_names(model_dict: typing.Optional[AnkiNoteTypeDict]) -> Iterable[str]:
    """
    Returns all field names found in the note type.
    """
    if model_dict is None:
        raise ValueError("note type is None.")
    return (field["name"] for field in model_dict["flds"])


def relevant_field_names(note_type_name_fuzzy: Optional[str] = None) -> Iterable[str]:
    """
    Return an iterable of field names present in note types whose names contain the first parameter.
    """
    for model in mw.col.models.all_names_and_ids():
        if not note_type_name_fuzzy or note_type_name_fuzzy.lower() in model.name.lower():
            yield from get_model_field_names(mw.col.models.get(model.id))


def gather_all_field_names() -> Iterable[str]:
    """
    Returns all field names found in all note types found in the collection.
    """
    return relevant_field_names()
