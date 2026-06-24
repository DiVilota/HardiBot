"""Debug Knasta scraper to find the error."""
import sys, os, requests, json, re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

BASE_URL = "https://knasta.cl"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/120.0",
    "Accept": "text/html",
}

path = "hardware/componentes/procesadores"
url = f"{BASE_URL}/results/{path}?page=1&page_size=32&order=price_asc"
print(f"Fetching: {url}")

try:
    r = requests.get(url, headers=headers, timeout=15)
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.text)}")

    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
        r.text,
        re.DOTALL,
    )

    if m:
        data = json.loads(m.group(1))
        print(f"Top-level keys: {list(data.keys())}")

        if "props" in data and "pageProps" in data["props"]:
            pp = data["props"]["pageProps"]
            print(f"pageProps keys: {list(pp.keys())}")

            if "initialData" in pp:
                init = pp["initialData"]
                print(f"initialData keys: {list(init.keys())}")
                print(f"count: {init.get('count', 0)}")
                products = init.get("products", [])
                print(f"products count: {len(products)}")
                if products:
                    print(f"First product keys: {list(products[0].keys())}")
                    print(f"First product sample: {json.dumps(products[0], indent=2)[:500]}")
            else:
                print("NO initialData. Raw pageProps:")
                print(json.dumps(pp, indent=2)[:1000])
        else:
            print("NO pageProps in props")
            print(json.dumps(data, indent=2)[:1000])
    else:
        print("__NEXT_DATA__ script NOT FOUND!")
        debug_path = os.path.join("logs", "knasta_debug.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(r.text)
        print(f"Saved HTML to {debug_path}")

        # Try to find any JSON data in script tags
        scripts = re.findall(r'<script[^>]*>([^<]+)</script>', r.text)
        print(f"Found {len(scripts)} script tags")
        for i, s in enumerate(scripts[:5]):
            print(f"  Script {i}: {s[:100]}...")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
