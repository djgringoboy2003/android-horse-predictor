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

DAY_NAMES = {
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
}


def fractional_to_decimal(frac):
    try:
        num, den = frac.split("/")
        return (float(num) / float(den)) + 1.0
    except Exception:
        return None


def clean_text(line):
    line = re.sub(r"\[[^\]]+\]", "", line)
    line = re.sub(r"<[^>]+>", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def parse_entries_from_text(html):
    raw_lines = html.splitlines()
    lines = [clean_text(line) for line in raw_lines]
    lines = [line for line in lines if line]

    entries = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if line in {"Horse Race Day Odds", "ABC Guide", "Today", "Tomorrow", "5 Days", "My Stable"}:
            i += 1
            continue

        horse = line

        if i + 2 >= len(lines):
            i += 1
            continue

        if lines[i + 1] == "My Stable":
            race_day_odds = lines[i + 2]

            match = re.match(
                r"^(\d{1,2}:\d{2})\s+(.+?)\s+"
                r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+"
                r"(\d+/\d+)$",
                race_day_odds
            )

            if match:
                time_part = match.group(1).strip()
                course = match.group(2).strip()
                day = match.group(3).strip()
                odds = match.group(4).strip()

                entries.append({
                    "horse": horse,
                    "race": f"{time_part} {course}",
                    "day": day,
                    "odds": odds
                })

                i += 3
                continue

        i += 1

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
            entries = parse_entries_from_text(response.text)
            print(f"{url} -> {len(entries)} entries")
            all_entries.extend(entries)
        except Exception as exc:
            print(f"Failed to fetch {url}: {exc}")

    races = build_races(all_entries)

    with open("data/upcoming_races.json", "w", encoding="utf-8") as f:
        json.dump(races, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(races)} races")


if __name__ == "__main__":
    main()
