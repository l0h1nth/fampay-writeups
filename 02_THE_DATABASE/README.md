# [02] THE DATABASE

## Challenge

> The door is open to anyone. You don't need a name to enter, but the room still has a lock.
>
> hint: identity is optional here

APK: `fam-ctf.apk`  
SHA256: `7534e6b0a665fb5c48b1a3b664274b423ca00601f77253b13220a7fe9ffb6e7c`

## Flag

```text
FAM{4n0n_4uth_1s_n0t_s3cur3_en0ugh}
```

## Short Summary

The app reads challenge 2 from Firebase Realtime Database. A direct request to `/flag.json` is denied, but the code signs in with Firebase anonymous authentication before reading the `flag` reference. Recreating that anonymous sign-in with the Firebase Auth REST API gives an ID token that unlocks the database path.

## Steps

### 1. Decompile and extract the APK

```bash
jadx -d 02_THE_DATABASE/decompiled_jadx 02_THE_DATABASE/apk/fam-ctf.apk
apktool d -f 02_THE_DATABASE/apk/fam-ctf.apk -o 02_THE_DATABASE/apktool
```

### 2. Find the database flow

Search for the challenge 2 code:

```bash
rg -n 'signInAnonymously|verifyFlag2|FirebaseDatabase|getReference\\("flag"\\)' 02_THE_DATABASE/decompiled_jadx/sources/com/ctf/fam/MainActivity.java
```

Relevant code:

```java
firebaseAuth.signInAnonymously();

FirebaseDatabase
    .getInstance("https://fam-ctf-default-rtdb.asia-southeast1.firebasedatabase.app")
    .getReference("flag")
    .addListenerForSingleValueEvent(...);
```

The Firebase config is also present in `res/values/strings.xml`:

```xml
<string name="firebase_database_url">https://fam-ctf-default-rtdb.asia-southeast1.firebasedatabase.app</string>
<string name="google_api_key">AIzaSyAes0IV3Hq3pN0oYmZJ1kfKl9vcvQEF2ww</string>
<string name="project_id">fam-ctf</string>
```

The same database flow can be checked in JADX GUI by opening `MainActivity` and searching for `verifyFlag2`:

![JADX GUI database flow](images/01_jadx_database_flow.png)

### 3. Confirm the lock

```bash
curl -sS 'https://fam-ctf-default-rtdb.asia-southeast1.firebasedatabase.app/flag.json'
```

Output:

```json
{
  "error" : "Permission denied"
}
```

### 4. Use anonymous Firebase auth

```bash
API_KEY='AIzaSyAes0IV3Hq3pN0oYmZJ1kfKl9vcvQEF2ww'
DB_URL='https://fam-ctf-default-rtdb.asia-southeast1.firebasedatabase.app'

TOKEN=$(
  curl -sS -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=${API_KEY}" \
    -H 'Content-Type: application/json' \
    --data '{"returnSecureToken":true}' \
  | jq -r '.idToken'
)

curl -sS "${DB_URL}/flag.json?auth=${TOKEN}"
```

Output:

```text
"FAM{4n0n_4uth_1s_n0t_s3cur3_en0ugh}"
```

## Evidence Files

- `evidence/apk_sha256.txt`
- `evidence/firebase_config_strings.txt`
- `evidence/mainactivity_database_flow.txt`
- `evidence/rtdb_unauth_denied.txt`
- `evidence/rtdb_flag_response.txt`
