Writeup: Noise

Challenge Overview
Target: Base64 encoded blob
We were provided with a large Base64-encoded string. Upon decoding, we obtained 2,055 bytes of seemingly random binary data. The lack of file headers or printable strings suggested a stream cipher or a simple XOR operation.

1. Initial Reconnaissance

Base64 Decoding

First, we converted the challenge data into its raw binary form:

import base64

with open("chall.txt", "r") as f:
    encoded_data = f.read()

decoded = base64.b64decode(encoded_data)
print(f"Data Length: {len(decoded)} bytes")


Failed Attempts

Standard automated XOR solvers failed to yield results. We tried:

Brute-forcing Single-byte XOR: Tested all 256 possible keys.

Known Plaintext Attack: Searching for the XOR-transformed bytes of Securinets{.

2. The Breakthrough: Key Stability Analysis

Since standard tools failed, we suspected the flag might be buried at a specific offset within the blob, potentially using a different key or a slightly modified plaintext. We implemented a sliding window script to derive a potential XOR key at every position, assuming the flag started there.

The Anomaly at Offset 1000

When we analyzed the key derived from the expected prefix Securinets{ at position 1000, we noticed a fascinating pattern:

Index

Expected Char

Raw Byte

Derived Key (Byte ^ Char)

0

S

0x96

0xd5

1

e

0xb4

0xd5

2

c

0xb6

0xd5

3

u

0xa0

0xd5

4

r

0xa7

0xd5

5

i

0xbc

0xd5

6

n

0xbb

0xd5

7

e

0xa1

0xc4 (Mismatch!)

8

t

0xb0

0xc4 (Mismatch!)

9

s

0xa6

0xd5

10

{

0xac

0xd5

The Hypothesis

The derived key was a stable 0xd5 for almost every character, except at indices 7 and 8. In XOR crypto, an inconsistent key usually means the known plaintext is wrong.

Looking at the swaps:

Expected e (index 7) and t (index 8) yielded 0xc4.

If we swap the characters to t and e (spelling Securintes instead of Securinets):

0xa1 ^ 't' (0x74) = 0xd5

0xb0 ^ 'e' (0x65) = 0xd5

The flag header was misspelled as Securintes{.

3. Decryption & Flag Extraction

With the corrected key (0xd5) and the knowledge of the misspelling, we decrypted the block starting at offset 1000.

Final Solver

def get_flag():
    decoded = base64.b64decode(encoded)
    
    # We know from analysis the data starts at offset 1000
    position = 1000
    target_start = b"Securintes{"
    
    # Derive the 1-byte XOR key using the known plaintext
    xor_key = decoded[position] ^ target_start[0]
    print(f"** Derived XOR key: {hex(xor_key)}")
    
    # Decrypt a chunk of data starting from the position
    chunk_size = 100
    decrypted = bytes([decoded[position + i] ^ xor_key for i in range(chunk_size)])
    text = decrypted.decode('latin-1')
    
    # Extract the string up to the closing brace
    match = re.search(r'Securintes\{.*?\}', text)
    if match:
        flag = match.group(0)
        print(f"** FLAG FOUND: {flag}")
       


if __name__ == "__main__":
    get_flag()


Flag Analysis

The full decrypted string was:
Securintes{allo_allo_yiiiiiiiiiiiiiiiiiiiiiiiiii_rawa7}

The challenge included several "distractors":

Misspelling: Securintes instead of Securinets.
