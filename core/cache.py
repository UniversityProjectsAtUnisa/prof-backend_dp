from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class Cache:
    def __init__(self):
        def nested_dict(): return defaultdict(nested_dict)
        self._cache = nested_dict()

    def retrieve(self, q: str, long: bool, lang: str, maxage: int, provider: Optional[str] = None) -> Dict[str, Any]:
        # {q:provider:long:lang:{data:"", created_at:"", original_language:"", current_language="", provider=""}}
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
        maxdate = datetime.now() - timedelta(seconds=seconds)
        for q in self._cache.values():
            for provider in q.values():
                for long in provider.values():
                    for lang in long.values():
                        if lang["created_at"] < maxdate:
                            del long[lang]

    def add(self, q: str, provider: str, long: bool, lang: str, data: Dict[str, Any]):
        old_data = self._cache[q][provider][long][lang]
        self._cache[q][provider][long][lang] = data
        return old_data

cache = Cache()