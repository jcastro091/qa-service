import re
from typing import List, Optional
from dateparser.search import search_dates

NAME_PATTERN = re.compile(r'(?P<name>[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', re.VERBOSE)

WHEN_WORDS = {"when", "date", "schedule", "trip", "travel", "going"}
COUNT_WORDS = {"how many", "count", "number"}
FAV_WORDS = {"favorite", "favourite", "favorites", "favourites"}

CARS_TOKENS = {"car", "cars", "vehicle", "vehicles"}
RESTAURANT_TOKENS = {"restaurant", "restaurants", "diner", "bistro"}

def extract_name(question: str) -> Optional[str]:
    candidates = [m.group("name") for m in NAME_PATTERN.finditer(question)]
    if not candidates:
        return None
    bad = {"What", "When", "How", "Who", "Where", "Which", "Why"}
    candidates = [c for c in candidates if c.split()[0] not in bad]
    if not candidates:
        return None
    return max(candidates, key=len)

def detect_intent(question: str) -> str:
    q = question.lower()
    if any(w in q for w in COUNT_WORDS):
        return "count"
    if any(w in q for w in FAV_WORDS):
        return "favorites"
    if any(w in q for w in WHEN_WORDS):
        return "when"
    if q.startswith("when"): return "when"
    if q.startswith("how many"): return "count"
    if q.startswith("what are"): return "favorites"
    return "unknown"

def extract_dates(text: str) -> List[str]:
    res = search_dates(text, settings={"PREFER_DATES_FROM":"future"})
    if not res:
        return []
    return [s for s, _dt in res]

def contains_any(text: str, vocab: set) -> bool:
    t = text.lower()
    return any(tok in t for tok in vocab)

def is_cars_context(text: str) -> bool:
    return contains_any(text, CARS_TOKENS)

def is_restaurant_context(text: str) -> bool:
    return contains_any(text, RESTAURANT_TOKENS)
