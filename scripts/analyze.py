import asyncio
from collections import defaultdict
from app.retriever import fetch_messages

async def main():
    msgs = await fetch_messages()
    print(f"Total messages: {len(msgs)}")
    by_member = defaultdict(list)
    for m in msgs:
        by_member[m.member_name].append(m)

    empties = [k for k in by_member.keys() if not k or k.strip() == ""]
    if empties:
        print("\n[Anomaly] Messages with missing member_name:", len(empties))

    large_numbers = 0
    for m in msgs:
        for tok in m.text.split():
            if tok.isdigit() and int(tok) > 10:
                large_numbers += 1
                break
    print(f"\nPotential outlier numeric mentions (>10): {large_numbers}")

    import re
    date_like = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b", re.I)
    conflicts = []
    for name, arr in by_member.items():
        dset = set()
        for m in arr:
            for mt in date_like.findall(m.text):
                dset.add(mt)
        if len(dset) >= 3:
            conflicts.append((name, len(dset)))
    if conflicts:
        print("\n[Potential conflicts] Members with many distinct date tokens:")
        for name, n in conflicts[:10]:
            print(" -", name, "dates:", n)

if __name__ == "__main__":
    asyncio.run(main())
