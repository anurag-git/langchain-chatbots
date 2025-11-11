import certifi
import requests

print(certifi.where())
try:
    requests.get("https://www.google.com")
    print("✓ Certificates working!")
except Exception as e:
    print(f"✗ Certificate issue: {e}")
