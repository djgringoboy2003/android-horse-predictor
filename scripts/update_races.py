import csv
import json
import requests
from collections import defaultdict

URL = "https://www.sportinglife.com/racing/abc-guide/today/download.csv"


def fractional_to_decimal(frac):
    try:
        num, den = frac.split('/')
        return (float(num) / float(den)) + 1
    except:
        return None


def main():
    r = requests.get(URL)
    text = r.text

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    races = defaultdict(list)

    for i in range(1, len(lines)):
        parts = lines[i].split('\t')
        if len(parts) < 4:
            parts = lines[i].split(',')
        if len(parts) < 4:
            continue

        horse = parts[0].strip()
        race = parts[1].strip()
        day = parts[2].strip()
        odds = parts[3].strip()

        try:
            time, course = race.split(' ', 1)
        except:
            continue

        dec = fractional_to_decimal(odds)
        if not dec:
            continue

        prob = 1 / dec

        key = f"{day}_{time}_{course}"

        races[key].append({
            "horse": horse,
            "odds": odds,
            "decimal_odds": dec,
            "implied_prob": prob
        })

    output = []

    for key, runners in races.items():
        day, time, course = key.split('_', 2)
        total_prob = sum(r['implied_prob'] for r in runners)
        for r in runners:
            r['implied_prob'] = r['implied_prob'] / total_prob

        output.append({
            "day": day,
            "time": time,
            "course": course,
            "runners": runners
        })

    with open('data/upcoming_races.json', 'w') as f:
        json.dump(output, f, indent=2)


if __name__ == '__main__':
    main()
