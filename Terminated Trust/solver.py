from pwn import *
import math

context.log_level = 'info'

HOST = '20.250.145.165'
PORT = 5010
r = remote(HOST, PORT)

def get_params():
    r.sendlineafter(b'choice> ', b'1')
    n = int(r.recvline().split(b'=')[1])
    e = int(r.recvline().split(b'=')[1])
    k = int(r.recvline().split(b'=')[1])
    
    r.sendlineafter(b'choice> ', b'2')
    c_hex = r.recvline().split(b'=')[1].strip().decode()
    c = int(c_hex, 16)
    return n, e, k, c

n, e, k, target_c = get_params()
B = 2**(8*(k-2))
THRESHOLD = 190962 

def is_pkcs1_valid(c_prime):
    c_hex = f"{c_prime:0{k*2}x}"
    r.sendlineafter(b'choice> ', b'3')
    r.sendlineafter(b'> ', c_hex.encode())
    res = r.recvline().decode()
    try:
        time_ns = int(res.split('"time_ns": ')[1].strip('}\n'))
        return time_ns > THRESHOLD
    except:
        return False

M = [(2*B, 3*B - 1)]
s = (n + 3*B - 1) // (3*B)
i = 1

print("** Starting")

while True:
    if i == 1:
        while not is_pkcs1_valid((target_c * pow(s, e, n)) % n):
            s += 1
    elif len(M) > 1:
        s += 1
        while not is_pkcs1_valid((target_c * pow(s, e, n)) % n):
            s += 1
    else:
        a, b = M[0]
        r_val = (2 * (b * s - 2 * B) + n - 1) // n
        found = False
        while not found:
            lower_s = (2 * B + r_val * n + b - 1) // b
            upper_s = (3 * B + r_val * n + a - 1) // a
            for s_test in range(lower_s, upper_s + 1):
                if is_pkcs1_valid((target_c * pow(s_test, e, n)) % n):
                    s = s_test
                    found = True
                    break
            r_val += 1

    new_M = []
    for a, b in M:
        r_min = (a * s - 3 * B + 1 + n - 1) // n
        r_max = (b * s - 2 * B) // n
        for r_val in range(r_min, r_max + 1):
            start = max(a, (2 * B + r_val * n + s - 1) // s)
            end = min(b, (3 * B - 1 + r_val * n) // s)
            if start <= end:
                new_M.append((start, end))
    M = list(set(new_M))

    if len(M) == 1 and M[0][0] == M[0][1]:
        recovered_m = M[0][0]
        break
    
    i += 1
    if i % 10 == 0:
        print(f"** Iteration {i}, Range size: {M[0][1]-M[0][0]}")

m_bytes = recovered_m.to_bytes(k, 'big')
separator_index = m_bytes.find(b'\x00', 2)
actual_data = m_bytes[separator_index + 1:]

passphrase_ascii = actual_data.decode(errors='ignore').strip()
plaintext_hex = actual_data.hex()

print(f"\n** RECOVERED PASSPHRASE: {passphrase_ascii}")
print(f"** SUBMITTING HEX: {plaintext_hex}")

r.sendlineafter(b'choice> ', b'4')
r.sendlineafter(b'plaintext hex> ', plaintext_hex.encode())

print(f"\n[!] SERVER RESPONSE: {r.recvall().decode()}")
