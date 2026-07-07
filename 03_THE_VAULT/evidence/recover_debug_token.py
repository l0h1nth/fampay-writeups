from pathlib import Path

lib = Path('apktool/lib/x86_64/libfam.so').read_bytes()
key = lib[0x34f0:0x34f0 + 19]
data = lib[0x3510:0x3510 + 36]
print(bytes(b ^ (key[i % 19] ^ 0xAA) for i, b in enumerate(data)).decode())
