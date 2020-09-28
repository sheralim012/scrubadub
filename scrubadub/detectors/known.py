import sys

from typing import Optional, List, Union, Dict, Generator

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

from .base import Detector
from ..filth.known import KnownFilth


class KnownFilthItem(TypedDict):
    start: str
    end: str
    limit: int
    match: str
    comparison_type: str


class KnownFilthDetector(Detector):
    """Use some predefined phrases to label the text.

    This is useful if you have found that some particular
    type of PII occurs regularly or you want to compare
    scrubadub with already selected PII.
    """

    filth_cls = KnownFilth
    name = 'known'

    def __init__(self, predefined_pii: Optional[List[KnownFilthItem]] = None, **kwargs):
        super().__init__(**kwargs)
        if predefined_pii is None:
            predefined_pii = []
        self._predefined_pii = predefined_pii

    def _find_all(
            self,
            text: str,
            substr: str,
            comparison_type: Optional[str] = None,
            document_name: Optional[str] = None
    ) -> Generator[KnownFilth, None, None]:
        """Yield filth for each match to substr in text."""
        substr_len = len(substr)
        start_location = text.find(substr)

        while start_location >= 0:
            yield KnownFilth(
                start_location,
                start_location + substr_len,
                text[start_location:start_location + substr_len],
                comparison_type=comparison_type,
                detector_name=self.name,
                document_name=document_name,
            )
            start_location = text.find(
                substr,
                start_location + substr_len
            )

    def _find_all_between(
            self,
            text: str,
            substr_start: str,
            substr_end: str,
            limit: int = 150,
            comparison_type: Optional[str] = None,
            document_name: Optional[str] = None
    ) -> Generator[KnownFilth, None, None]:
        """Yield filth for text between (and including)
        substr_start and substr_end, but only if the text
        between the two is less than limit characters.
        """
        substr_start_len = len(substr_start)
        substr_end_len = len(substr_end)
        start_location = text.find(substr_start)

        while start_location >= 0:
            end_location = text.find(
                substr_end,
                start_location + substr_start_len,
                start_location + substr_start_len + limit + substr_end_len
            )
            if end_location >= 0:
                yield KnownFilth(
                    start_location,
                    end_location + substr_end_len,
                    text[start_location:end_location + substr_end_len],
                    comparison_type=comparison_type,
                    detector_name=self.name,
                    document_name=document_name,
                )
                next_search_start = end_location + substr_end_len
            else:
                next_search_start = start_location + substr_start_len

            start_location = text.find(substr_start, next_search_start)

    def iter_filth(
            self,
            text: str,
            document_name: Optional[str] = None
    ) -> Generator[KnownFilth, None, None]:
        """Iterate over the predefined PII list and yield
        filth instances."""
        for pii_item in self._predefined_pii:
            # could also implement other types in here too
            if 'match' in pii_item:
                for found_item in self._find_all(
                        text,
                        pii_item['match'],
                        comparison_type=pii_item.get('comparison_type', None),
                        document_name=document_name,
                ):
                    yield found_item
            elif 'start' in pii_item and 'end' in pii_item:
                for found_item in self._find_all_between(
                    text,
                    pii_item['start'],
                    pii_item['end'],
                    limit=int(pii_item.get('limit', 150)),
                    comparison_type=pii_item.get('comparison_type', None),
                    document_name=document_name,
                ):
                    yield found_item
            else:
                raise ValueError(
                    "Unknown keys in predefined PII item: "
                    "{}".format(pii_item.keys())
                )
