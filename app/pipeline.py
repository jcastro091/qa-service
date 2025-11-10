from typing import List, Optional
import re
from rapidfuzz import fuzz, process

try:
    from rapidfuzz import fuzz
    HAVE_FUZZ = True
except Exception:
    HAVE_FUZZ = False

from .retriever import fetch_messages
from .rules import extract_name, detect_intent, extract_dates, is_cars_context, is_restaurant_context
from .models import AskResponse, Evidence, Message



PREF_TOKENS = ("prefer", "preference", "i prefer")
SEAT_TOKENS = ("aisle", "window", "middle")

def _match_member(target: Optional[str], name: str) -> bool:
    if not target:
        return True
    if name.lower() == target.lower():
        return True
    if HAVE_FUZZ and fuzz.partial_ratio(name.lower(), target.lower()) >= 85:
        return True
    return False

def _rank_messages(question: str, msgs: List[Message]) -> List[Message]:
    q_tokens = set(re.findall(r"\w+", question.lower()))
    def score(m: Message) -> int:
        t = set(re.findall(r"\w+", m.text.lower()))
        return len(q_tokens & t)
    return sorted(msgs, key=score, reverse=True)

async def answer_question(question: str) -> AskResponse:
    target_name = extract_name(question)
    intent = detect_intent(question)

    msgs = await fetch_messages()
    filtered = [m for m in msgs if _match_member(target_name, m.member_name or "")]
    ranked = _rank_messages(question, filtered)[:25]

    if intent == "when":
        # date anywhere in ranked messages
        for m in ranked:
            ds = extract_dates(m.text)
            if ds:
                return AskResponse(answer=ds[0], confidence=0.8,
                                   evidence=[Evidence(message_id=m.id, snippet=m.text[:200])])

        # name+trip/travel/flight + city + date anywhere among member's messages
        TRAVEL_TOKENS = ("trip", "travel", "flight", "flights", "book", "going to")
        for m in filtered:
            t = m.text.lower()
            if any(x in t for x in TRAVEL_TOKENS) and any(c in t for c in CITY_KEYWORDS):
                ds = extract_dates(m.text)
                if ds:
                    return AskResponse(answer=ds[0], confidence=0.75,
                                       evidence=[Evidence(message_id=m.id, snippet=m.text[:200])])

    q_lower = question.lower()

    if intent == "count" and any(w in q_lower for w in ["car","cars","vehicle","vehicles"]):
        for m in ranked + filtered:
            m_lower = (m.text or "").lower()
            if not m_lower:
                continue
            match = re.search(r"(?:has|own|owns|with|:)?\s*(\d{1,3})\s+(?:car|cars|vehicle|vehicles)\b", m_lower)
            if match:
                return AskResponse(
                    answer=match.group(1),
                    confidence=0.85,
                    evidence=[Evidence(message_id=m.id, snippet=m.text[:200])],
                )
        # If we saw a number but not tied to 'cars', fall back softly
        for m in ranked:
            if not m.text:
                continue
            match = re.search(r"\b(\d{1,3})\b", m.text)
            if match:
                return AskResponse(
                    answer=match.group(1),
                    confidence=0.5,
                    evidence=[Evidence(message_id=m.id, snippet=m.text[:200])],
                )


                        
        for m in ranked:
            match = re.search(r"\b(\d{1,3})\b", m.text)
            if match:
                return AskResponse(
                    answer=match.group(1),
                    confidence=0.5,
                    evidence=[Evidence(message_id=m.id, snippet=m.text[:200])],
                )

    if intent == "favorites" or "favorite" in question.lower():
        for m in ranked:
            if is_restaurant_context(m.text) or "favorite" in m.text.lower():
                parts = re.split(r"[:\-]\s*| are | is | include | includes ", m.text, maxsplit=1)
                if len(parts) > 1:
                    candidates = re.split(r",|;|\band\b", parts[1])
                    cleaned = [c.strip().strip(". ") for c in candidates if len(c.strip()) > 1]
                    if cleaned:
                        cleaned = [c for c in cleaned if not re.match(r"^(favorite|restaurants?)$", c, flags=re.I)]
                        if cleaned:
                            top = list(dict.fromkeys(cleaned))[:3]
                            return AskResponse(
                                answer=", ".join(top),
                                confidence=0.7,
                                evidence=[Evidence(message_id=m.id, snippet=m.text[:200])],
                            )
                            
                            
    q = question.lower()
    if any(t in q for t in ("seat", "seats", "preference", "prefer")):
        for m in ranked + filtered:
            t = m.text.lower()
            if any(pt in t for pt in PREF_TOKENS) and any(st in t for st in SEAT_TOKENS):
                import re
                m2 = re.search(r"(?:prefer|preference is)\s+(?P<seat>aisle|window|middle)\s+seats?", t)
                if m2:
                    seat = m2.group("seat").title()
                    return AskResponse(answer=f"{seat} seats", confidence=0.9,
                        evidence=[Evidence(message_id=m.id, snippet=m.text[:200])])  

    # --- Restaurant / reservation extraction ---
    # Triggers on questions mentioning restaurant/reservation/dinner/table/booking
    if any(k in q_lower for k in ["restaurant", "reservation", "dinner", "table", "booking", "book a table", "booked at"]):
        # Regex: capture a Proper Noun phrase after "reservation|booking|table at/for ..."
        RE_RESTAURANT = re.compile(
            r"(?:reservation|book(?:ing)?|table)\s+(?:at|for)\s+"
            r"([A-Z][\w'&.-]*(?:\s+[A-Z][\w'&.-]*){0,6})"
        )
        # Search the most relevant first, then any from the same member
        for m in ranked + filtered:
            text = (m.text or "")
            tl = text.lower()
            if "reservation" in tl or "restaurant" in tl or "dinner" in tl or "table" in tl or "booking" in tl:
                hit = RE_RESTAURANT.search(text)
                if hit:
                    restaurant = hit.group(1).strip().rstrip(" .,!?:;")
                    return AskResponse(
                        answer=restaurant,
                        confidence=0.85,
                        evidence=[Evidence(message_id=m.id, snippet=text[:200])],
                    )
                        

    return AskResponse(
        answer="I couldn't find that in the member messages.",
        confidence=0.0,
        evidence=[],
    )
