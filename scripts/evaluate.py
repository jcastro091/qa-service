#!/usr/bin/env python3
import os, httpx, json, re, collections
from dateutil import parser

URL = os.getenv("MESSAGES_API_URL","https://november7-730026606190.europe-west1.run.app/messages")

def fetch():
    with httpx.Client(follow_redirects=True, timeout=30) as c:
        r = c.get(URL)
        r.raise_for_status()
        data = r.json()
        return data["items"] if isinstance(data, dict) and "items" in data else data

def norm(x):
    return {
        "id": str(x.get("id") or x.get("_id") or ""),
        "member": str(x.get("member_name") or x.get("user_name") or x.get("name") or ""),
        "text": str(x.get("message") or x.get("text") or ""),
        "timestamp": x.get("timestamp"),
    }

def main():
    raw = fetch()
    items = [norm(x) for x in raw]
    n = len(items)

    missing = {
        "id": sum(not i["id"] for i in items),
        "member": sum(not i["member"] for i in items),
        "text": sum(not i["text"] for i in items),
        "timestamp": sum(not i["timestamp"] for i in items),
    }

    bad_ts = 0
    for i in items:
        if i["timestamp"]:
            try:
                parser.isoparse(i["timestamp"])
            except Exception:
                bad_ts += 1

    members = collections.Counter(i["member"] for i in items if i["member"])
    top_members = members.most_common(5)

    has_london = [i for i in items if "london" in i["text"].lower()]
    cars_mentions = [i for i in items if re.search(r"\bcar(s)?\b", i["text"].lower())]
    favorite_mentions = [i for i in items if "favorite" in i["text"].lower() and "restaurant" in i["text"].lower()]

    print(json.dumps({
        "count": n,
        "missing_fields": missing,
        "bad_timestamps": bad_ts,
        "top_members": top_members,
        "examples": {
            "london": has_london[:2],
            "cars": cars_mentions[:2],
            "favorite_restaurants": favorite_mentions[:2]
        }
    }, indent=2))

if __name__ == "__main__":
    main()
