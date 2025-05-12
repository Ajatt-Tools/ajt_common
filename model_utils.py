# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import typing
from collections.abc import Iterable

from aqt import mw


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


def gather_all_field_names() -> Iterable[str]:
    """
    Returns all field names found in all note types found in the collection.
    """
    for model in mw.col.models.all_names_and_ids():
        yield from get_model_field_names(mw.col.models.get(model.id))
