# FamPay CTF Writeups

Writeups for the FamPay security CTF at [ctf.fampay.co](https://ctf.fampay.co).

## Why This CTF

Fam described this challenge as more than a leaderboard exercise: the bugs here mirror issues that matter when real financial data and real users are involved.

That is what made it worth playing. The set covered the kind of security work I enjoy most: broken access control, misplaced trust, weak auth boundaries, JWT mistakes, mobile reverse engineering, and cloud metadata abuse.

## Challenges

| # | Challenge | Main Idea | Writeup |
|---|-----------|-----------|---------|
| 01 | THE LIBRARY | Secret left inside native app code | [01_THE_LIBRARY](01_THE_LIBRARY/) |
| 02 | THE DATABASE | Firebase anonymous auth and exposed database path | [02_THE_DATABASE](02_THE_DATABASE/) |
| 03 | THE VAULT | App Check debug token and trusted app identity | [03_THE_VAULT](03_THE_VAULT/) |
| 04 | THE ENDPOINT | Native request signing and admin-only clearance | [04_THE_ENDPOINT](04_THE_ENDPOINT/) |
| 05 | THE VAULT DOOR | JWT role bypass using `alg: none` | [05_THE_VAULT_DOOR](05_THE_VAULT_DOOR/) |
| 06 | THE CLOUD | Debug webhook SSRF to IMDSv2 and S3 | [06_THE_CLOUD](06_THE_CLOUD/) |

## Flags

```text
[01] FAM{str1ngs_d0nt_l13_1n_n4t1v3_l4nd}
[02] FAM{4n0n_4uth_1s_n0t_s3cur3_en0ugh}
[03] FAM{4pp_ch3ck_byp4ss_g00d_j0b}
[04] FAM{x_s1gn4tur3_r3v3rs3d_n1c3ly}
[05] FAM{jwt_4lg_n0n3_byp4ss_gr4nt3d}
[06] FAM{cl0ud_ssrf_imds_1894d750213a}
```

## Repository Layout

Each challenge folder contains:

- `README.md` with the solve path
- `evidence/` with commands, outputs, scripts, or extracted artifacts
- `images/` with screenshots used in the writeup
- `apk/` where the challenge APK was needed

Temporary cloud credentials and presigned URLs were redacted before publishing.
