#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import hmac
import json
from pathlib import Path
from urllib.parse import quote


def sign(key, msg):
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()


def signing_key(secret, date_stamp, region, service):
    k_date = sign(("AWS4" + secret).encode(), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    return sign(k_service, "aws4_request")


def canonical_query(params):
    pairs = []
    for key, value in params:
        pairs.append((quote(key, safe="-_.~"), quote(value, safe="-_.~")))
    return "&".join(f"{key}={value}" for key, value in sorted(pairs))


def presign(creds, bucket, region, key=None, prefix=None, expires=900):
    now = dt.datetime.now(dt.UTC)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")
    service = "s3"
    host = f"{bucket}.s3.{region}.amazonaws.com"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"

    if key:
        path = "/" + quote(key, safe="/-_.~")
        params = []
    else:
        path = "/"
        params = [("list-type", "2"), ("prefix", prefix or "")]

    params.extend(
        [
            ("X-Amz-Algorithm", "AWS4-HMAC-SHA256"),
            ("X-Amz-Credential", f"{creds['AccessKeyId']}/{credential_scope}"),
            ("X-Amz-Date", amz_date),
            ("X-Amz-Expires", str(expires)),
            ("X-Amz-Security-Token", creds["Token"]),
            ("X-Amz-SignedHeaders", "host"),
        ]
    )

    canonical_request = "\n".join(
        [
            "GET",
            path,
            canonical_query(params),
            f"host:{host}\n",
            "host",
            "UNSIGNED-PAYLOAD",
        ]
    )
    string_to_sign = "\n".join(
        [
            "AWS4-HMAC-SHA256",
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode()).hexdigest(),
        ]
    )
    signature = hmac.new(
        signing_key(creds["SecretAccessKey"], date_stamp, region, service),
        string_to_sign.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"https://{host}{path}?{canonical_query(params + [('X-Amz-Signature', signature)])}"


def load_creds(path):
    raw = Path(path).read_text()
    start = raw.find('{"body"')
    outer = json.loads(raw[start:])
    return json.loads(outer["body"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--creds-file", default="evidence/webhook_imdsv2_credentials.txt")
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--prefix")
    parser.add_argument("--key")
    args = parser.parse_args()

    creds = load_creds(args.creds_file)
    print(presign(creds, args.bucket, args.region, key=args.key, prefix=args.prefix))


if __name__ == "__main__":
    main()
