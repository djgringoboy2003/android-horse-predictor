import json
import re
import requests
from collections import defaultdict

URLS = [
    "https://www.sportinglife.com/racing/abc-guide/today",
    "https://www.sportinglife.com/racing/abc-guide/tomorrow",
    "https://www.sportinglife.com/racing/abc-guide/5-days",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fractional_to_decimal(frac):
    try:
        num, den = frac.split("/")
        return (float(num) / float(den)) + 1.0
    except Exception:
        return None


def parse_html_entries(html):
    entries = []

    blocks = re.findall(
        r'([A-Za-z0-9\'’&().,\- ]+?)\s+(\d{1,2}:\d{2}\s+[A-Za-z\'’&().,\- ]+)\s+'
        r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d+/\d+)',
        html,
        flags=re.IGNORECASE
    )

    for horse, race, day, odds in blocks:
        horse = re.sub(r"\s+", " ", horse).strip()
        race = re.sub(r"\s+", " ", race).strip()
        day = day.strip()
        odds = odds.strip()

        bad_values = {
            "My Stable",
            "ABC Guide",
            "Today",
            "Tomorrow",
            "5 Days",
            "Today's entries",
            "Todays entries",
            "Horse",
            "Race",
            "Day",
            "Odds",
        }

        if horse in bad_values:
            continue

        entries.append({
            "horse": horse,
            "race": race,
            "day": day,
            "odds": odds
        })

    return entries


def build_races(entries):
    races = defaultdict(list)

    for item in entries:
        try:
            time_part, course = item["race"].split(" ", 1)
        except ValueError:
            continue

        dec = fractional_to_decimal(item["odds"])
        if not dec:
            continue

        prob = 1 / dec
        key = f'{item["day"]}_{time_part}_{course}'

        races[key].append({
            "horse": item["horse"],
            "odds": item["odds"],
            "decimal_odds": dec,
            "implied_prob": prob
        })

    output = []

    for key, runners in races.items():
        day, time_part, course = key.split("_", 2)
        total_prob = sum(r["implied_prob"] for r in runners)

        if total_prob > 0:
            for runner in runners:
                runner["implied_prob"] = runner["implied_prob"] / total_prob

        runners.sort(key=lambda x: x["implied_prob"], reverse=True)

        output.append({
            "day": day,
            "time": time_part,
            "course": course,
            "runners": runners
        })

    output.sort(key=lambda x: (x["day"], x["time"], x["course"]))
    return output


def main():
    all_entries = []

    for url in URLS:
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            entries = parse_html_entries(response.text)
            if entries:
                all_entries.extend(entries)
        except Exception as exc:
            print(f"Failed to fetch {url}: {exc}")

    races = build_races(all_entries)

    with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
        json.dump(races, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(races)} races")


if __name__ == "__main__":
    main()
