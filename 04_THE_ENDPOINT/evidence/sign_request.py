from pathlib import Path
import sys

MASK = (1 << 64) - 1


def fmix64(x):
    x &= MASK
    x ^= x >> 33
    x = (x * 0xff51afd7ed558ccd) & MASK
    x ^= x >> 33
    x = (x * 0xc4ceb9fe1a85ec53) & MASK
    x ^= x >> 33
    return x & MASK


def sign(method, path, body, lib_path='apktool/lib/x86_64/libfam.so', app_sabotage=False):
    lib = Path(lib_path).read_bytes()
    key = lib[0x34f0:0x34f0 + 19]
    state = [int.from_bytes(lib[0x3570 + i * 8:0x3578 + i * 8], 'little') for i in range(4)]
    fnv = 0xcbf29ce484222325
    msg = f'{method}|{path}|{body}'.encode()

    for i, b in enumerate(msg):
        masked = b ^ (key[i % 19] ^ 0xAA)
        state[i & 3] = (state[i & 3] ^ masked) & MASK
        state[(i + 1) & 3] = (state[i & 3] + state[(i + 1) & 3]) & MASK
        state[(i + 2) & 3] = fmix64(state[(i + 2) & 3])
        state[(i + 3) & 3] = ((0x517cc1b727220a95 * state[(i + 1) & 3]) ^ state[(i + 3) & 3]) & MASK
        fnv = ((fnv ^ b) * 0x100000001B3) & MASK

    for _ in range(4):
        for j in range(4):
            state[j] = fmix64(state[j] ^ state[(j + 1) & 3])

    if app_sabotage and fnv == 0xdcc67eca15a7c732:
        state[2] ^= 0xdeadbeefcafebabe

    return ''.join(f'{x:016x}' for x in state)


if __name__ == '__main__':
    method = sys.argv[1]
    path = sys.argv[2]
    body = sys.argv[3]
    print(sign(method, path, body))
