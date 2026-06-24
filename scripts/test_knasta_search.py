"""Test Knasta real-time search endpoint."""
import sys, os, requests, json, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

BASE_URL = "https://knasta.cl"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/120.0",
    "Accept": "text/html",
}

# Test 1: Search for a specific product
query = "Memoria RAM DDR5"
url = f"{BASE_URL}/results?q={requests.utils.quote(query)}&page=1&page_size=10"
print(f"=== Test 1: Search query '{query}' ===")
print(f"URL: {url}")
try:
    r = requests.get(url, headers=headers, timeout=15)
    print(f"Status: {r.status_code}")
    
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', r.text, re.DOTALL)
    if m:
        data = json.loads(m.group(1))
        init = data.get("props", {}).get("pageProps", {}).get("initialData", {})
        products = init.get("products", [])
        count = init.get("count", 0)
        print(f"Productos encontrados: {count}")
        for p in products[:5]:
            print(f"  - {p.get('title', '?')[:80]} | ${p.get('current_price', '?')}")
    else:
        print("NO __NEXT_DATA__ found")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Search by category + query
print(f"\n=== Test 2: Category + Search ===")
path = "hardware/componentes/memorias-ram"
url2 = f"{BASE_URL}/results/{path}?q=kingston&page=1&page_size=10"
print(f"URL: {url2}")
try:
    r = requests.get(url2, headers=headers, timeout=15)
    print(f"Status: {r.status_code}")
    
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', r.text, re.DOTALL)
    if m:
        data = json.loads(m.group(1))
        init = data.get("props", {}).get("pageProps", {}).get("initialData", {})
        products = init.get("products", [])
        count = init.get("count", 0)
        print(f"Productos encontrados: {count}")
        for p in products[:5]:
            print(f"  - {p.get('title', '?')[:80]} | ${p.get('current_price', '?')}")
    else:
        print("NO __NEXT_DATA__ found")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try the API endpoint directly
print(f"\n=== Test 3: Try API endpoint ===")
url3 = f"https://api.knasta.cl/api/v1/products/search?q={requests.utils.quote(query)}"
print(f"URL: {url3}")
try:
    r = requests.get(url3, headers={**headers, "Accept": "application/json"}, timeout=15)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Response: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")
    print("API endpoint may not exist - trying alternative...")
