import json
import re
import requests

URL = "https://www.sportinglife.com/racing/racecards"
HEADERS = {"User-Agent": "Mozilla/5.0"}

MEETINGS = [
    "Doncaster", "Kempton", "Stratford", "Uttoxeter", "Southwell",
    "Curragh", "Meydan", "Gulfstream", "Auteuil", "Laval", "Nancy",
    "Aqueduct", "Charles Town", "Laurel Park", "Oaklawn Park",
    "Sam Houston Race Park", "Santa Anita", "Tampa Bay Downs",
    "Turfway Park", "Will Rogers Downs"
]

def clean(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def parse_main_racecards(text):
    lines = [clean(x) for x in text.splitlines()]
    lines = [x for x in lines if x]

    meetings = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if line in MEETINGS:
            meeting = {
                "meeting": line,
                "going": "",
                "surface": "",
                "races": []
            }

            j = i + 1

            while j < len(lines):
                current = lines[j]

                if j > i + 1 and current in MEETINGS:
                    break

                if current.startswith("Going:"):
                    meeting["going"] = current.replace("Going:", "").strip()

                elif current.startswith("Surface:"):
                    meeting["surface"] = current.replace("Surface:", "").strip()

                elif re.match(r"^\d{1,2}:\d{2}$", current):
                    if j + 1 < len(lines):
                        title = lines[j + 1]
                        meta = lines[j + 2] if j + 2 < len(lines) else ""

                        age_band = ""
                        runner_count = None
                        race_class = ""
                        distance = ""

                        parts = [p.strip() for p in meta.split("|")]

                        for part in parts:
                            if "Runners" in part:
                                m = re.search(r"(\d+)\s+Runners", part)
                                if m:
                                    runner_count = int(m.group(1))
                            elif "Class" in part:
                                race_class = part
                            elif re.search(r"\d+[fm]", part):
                                distance = part
                            elif "YO" in part or "plus" in part:
                                age_band = part

                        meeting["races"].append({
                            "time": current,
                            "title": title,
                            "age_band": age_band,
                            "runner_count": runner_count,
                            "class": race_class,
                            "distance": distance
                        })

                j += 1

            meetings.append(meeting)
            i = j
            continue

        i += 1

    return meetings

def main():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    meetings = parse_main_racecards(response.text)

    with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
        json.dump(meetings, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(meetings)} meetings")

if __name__ == "__main__":
    main()
