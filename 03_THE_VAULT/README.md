# [03] THE VAULT

## Challenge

> The vault trusts no one it hasn't met. But the app already made introductions. Something in the code proves who you are.
>
> hint: the token is hiding in plain sight

APK: `fam-ctf.apk`  
SHA256: `7534e6b0a665fb5c48b1a3b664274b423ca00601f77253b13220a7fe9ffb6e7c`

## Flag

```text
FAM{4pp_ch3ck_byp4ss_g00d_j0b}
```

## Short Summary

Challenge 3 reads `flags/flag3` from Firestore, but the direct Firestore request is blocked. The app installs a custom Firebase App Check provider and passes a native `getDebugToken()` value into `exchangeDebugToken`. Recovering that debug token from `libfam.so` and exchanging it for an App Check token unlocks the Firestore document.

## Steps

### 1. Decompile and extract the APK

```bash
jadx -d 03_THE_VAULT/decompiled_jadx 03_THE_VAULT/apk/fam-ctf.apk
apktool d -f 03_THE_VAULT/apk/fam-ctf.apk -o 03_THE_VAULT/apktool
```

### 2. Find the vault flow

```bash
rg -n 'initAppCheck|getDebugToken|verifyFlag3|collection\\("flags"\\)|document\\("flag3"\\)' 03_THE_VAULT/decompiled_jadx/sources/com/ctf/fam/MainActivity.java
```

Relevant code:

```java
FirebaseAppCheck.getInstance().installAppCheckProviderFactory(
    new DebugTokenAppCheckProviderFactory(
        "674578159678",
        "1:674578159678:android:775058d15777caf841996f",
        getDebugToken(),
        API_KEY
    )
);

FirebaseFirestore.getInstance()
    .collection("flags")
    .document("flag3")
    .get();
```

The same App Check setup can be checked in JADX GUI by opening `MainActivity` and searching for `initAppCheck`:

![JADX GUI App Check init](images/01_jadx_init_appcheck.png)

Searching for `getDebugToken` shows the native token source passed into App Check:

![JADX GUI getDebugToken](images/02_jadx_get_debug_token.png)

Searching for `collection("flags").document("flag3")` shows the Firestore document read:

![JADX GUI Firestore flag3](images/03_jadx_firestore_flag3.png)

### 3. Check the App Check exchange code

```bash
rg -n 'exchangeDebugToken|debug_token|X-Goog-Api-Key|json.getString\\("token"\\)' 03_THE_VAULT/decompiled_jadx/sources/com/ctf/fam/DebugTokenAppCheckProvider.java
```

The provider sends the native debug token to:

```text
https://firebaseappcheck.googleapis.com/v1/projects/{projectNumber}/apps/{appId}:exchangeDebugToken
```

### 4. Recover the debug token

`getDebugToken()` is native, so inspect `libfam.so`. The x86_64 library contains the same logic and is easier to disassemble locally:

```bash
readelf -Ws 03_THE_VAULT/apktool/lib/x86_64/libfam.so | rg 'getDebugToken'

objdump -d -M intel \
  --start-address=0x6c30 \
  --stop-address=0x6d90 \
  03_THE_VAULT/apktool/lib/x86_64/libfam.so
```

The function builds a 36-byte token by XORing two byte arrays from `.rodata`. Recreate it:

```bash
cat > /tmp/recover_debug_token.py <<'PY'
from pathlib import Path

lib = Path('03_THE_VAULT/apktool/lib/x86_64/libfam.so').read_bytes()
key = lib[0x34f0:0x34f0 + 19]
data = lib[0x3510:0x3510 + 36]
print(bytes(b ^ (key[i % 19] ^ 0xAA) for i, b in enumerate(data)).decode())
PY

python3 /tmp/recover_debug_token.py
```

Output:

```text
8F76557D-A35A-4B51-94D4-D0DF98D79B55
```

### 5. Confirm the vault blocks direct access

```bash
API_KEY='AIzaSyAes0IV3Hq3pN0oYmZJ1kfKl9vcvQEF2ww'

curl -sS "https://firestore.googleapis.com/v1/projects/fam-ctf/databases/(default)/documents/flags/flag3?key=${API_KEY}" | jq .
```

Output:

```json
{
  "error": {
    "code": 403,
    "message": "Missing or insufficient permissions.",
    "status": "PERMISSION_DENIED"
  }
}
```

### 6. Exchange the debug token and read Firestore

```bash
API_KEY='AIzaSyAes0IV3Hq3pN0oYmZJ1kfKl9vcvQEF2ww'
PROJECT_NUMBER='674578159678'
APP_ID='1:674578159678:android:775058d15777caf841996f'
DEBUG_TOKEN='8F76557D-A35A-4B51-94D4-D0DF98D79B55'

APP_CHECK_TOKEN=$(
  curl -sS -X POST "https://firebaseappcheck.googleapis.com/v1/projects/${PROJECT_NUMBER}/apps/${APP_ID}:exchangeDebugToken" \
    -H 'Content-Type: application/json' \
    -H "X-Goog-Api-Key: ${API_KEY}" \
    --data "{\"debug_token\":\"${DEBUG_TOKEN}\"}" \
  | jq -r '.token'
)

curl -sS "https://firestore.googleapis.com/v1/projects/fam-ctf/databases/(default)/documents/flags/flag3?key=${API_KEY}" \
  -H "X-Firebase-AppCheck: ${APP_CHECK_TOKEN}" \
  | jq -r '.fields.value.stringValue'
```

Output:

```text
FAM{4pp_ch3ck_byp4ss_g00d_j0b}
```

## Evidence Files

- `evidence/apk_sha256.txt`
- `evidence/mainactivity_vault_flow.txt`
- `evidence/appcheck_debug_exchange_code.txt`
- `evidence/recover_debug_token.py`
- `evidence/debug_token.txt`
- `evidence/appcheck_exchange_redacted.json`
- `evidence/firestore_without_appcheck.json`
- `evidence/firestore_flag3_response.json`
