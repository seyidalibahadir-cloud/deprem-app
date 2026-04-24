import requests

def get_earthquakes():
    url = "https://deprem.afad.gov.tr/apiv2/event/filter"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        results = []

        for d in data:
            loc = d.get("location", "")

            if "Türkiye" in loc or "Turkey" in loc:
                results.append({
                    "mag": d.get("magnitude"),
                    "place": loc,
                    "time": d.get("date")
                })

        return results
    except:
        return []
