from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class Cache:
    """Cache used to store results along with their languages"""
    def __init__(self):
        def nested_dict(): return defaultdict(nested_dict)
        self._cache = nested_dict()

    def retrieve(self, q: str, long: bool, lang: str, maxage: int, provider: Optional[str] = None) -> Dict[str, Any]:
        """Function used to retrieve a value from cache with certain arguments shown below.

        Args:
            q (str): The text to search
            long (bool): If the search is long or short
            lang (str): The requested language
            maxage (int): The maximum age for the cache to be acceptable
            provider (str, optional): The specific provider of the informations. Defaults to None.

        Returns:
            Dict[str, Any]: The cached result according the input arguments
        """
        mindate = datetime.now() - timedelta(seconds=maxage)
        if q not in self._cache:
            return None
        values = []
        if not provider:
            for v in self._cache[q].values():
                if long in v:
                    values.append(v[long])
            if len(values) == 0:
                return None
        else:
            if provider not in self._cache[q] or long not in self._cache[q][provider]:
                return None
            values = [self._cache[q][provider][long]]

        for v in values:
            if lang not in v:
                continue
            if mindate is not None and v[lang]["created_at"] >= mindate:
                return v[lang]

        for v in values:
            for lang, res in v.items():
                if mindate is not None and res["original_language"] == res["current_language"] and res["created_at"] >= mindate:
                    return res

        return None

    def clear(self, seconds: int):
        """Function used to clear the cache

        Args:
            seconds (int): the minimum age of the result after which the cache has to be cleared
        """
        maxdate = datetime.now() - timedelta(seconds=seconds)
        for q in self._cache.values():
            for provider in q.values():
                for long in provider.values():
                    for lang in long.values():
                        if lang["created_at"] < maxdate:
                            del long[lang]

    def add(self, q: str, provider: str, long: bool, lang: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Function used to add a result to the cache

        Args:
            q (str): The text to search
            provider (str): The specific provider of the informations.
            long (bool): If the search is long or short
            lang (str): The request language
            data (Dict[str, Any]): The data to be added in the cache

        Returns:
            Dict[str, Any]: The old data that was stored in place of the data currently inserted
        """
        old_data = self._cache[q][provider][long][lang]
        self._cache[q][provider][long][lang] = data
        return old_data

cache = Cache()