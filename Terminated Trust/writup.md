Challenge Writeup:Terminated Trust

Flag: Securinets{l3g4cy_tl5_Pr0bl3m5}
Vulnerability: Bleichenbacher's Attack  via Timing Oracle

Challenge Overview

The challenge presented a custom netcat server acting as a "legacy TLS terminator." By interacting with the server, we could retrieve an RSA public key ($n, e$) and a target encrypted ciphertext.

The server also provided a probing endpoint (Option 3) that returned the execution time (time_ns) of the decryption process. This created a classic padding oracle.

The Vulnerability: Timing-Based PKCS#1 v1.5 Oracle

The RSA encryption used standard PKCS#1 v1.5 padding, which formats the plaintext as:
00 02 [Non-Zero Padding String] 00 [Message]

When probing the server with a crafted ciphertext, the decryption routine exhibited a measurable timing difference depending on whether the resulting plaintext was properly PKCS#1 v1.5 formatted or not. By setting a strict latency threshold (time_ns > 190962), we could reliably determine if a given ciphertext decrypted to a valid padded structure.

Exploitation (Bleichenbacher's Attack)

With a working padding oracle, the challenge was solvable using Daniel Bleichenbacher's 1998 adaptive chosen-ciphertext attack.

Crafting Ciphertexts: We multiplied the target ciphertext $c$ by $s^e \pmod n$ for incrementally increasing values of $s$.

Querying the Oracle: We sent $c' = c \cdot s^e \pmod n$ to the server. If the server's timing indicated valid padding, we knew that $m \cdot s \pmod n$ fell into a specific mathematical boundary ($[2B, 3B-1]$).

Narrowing the Intervals: Using the valid $s$ values, we iteratively narrowed down the possible range for the original plaintext $m$.

Convergence: After about 220 iterations, the upper and lower bounds merged, revealing the fully padded original message $m$.

Extracting the Flag

Once the integer $m$ was recovered, it was converted back to bytes:
00 02 f1 ea 42 ff a0 7d 6f 46 f0 68 f2 7b 5e ca 38 77 c0 71 00 52 61 6b 20 4d 33 61 6c 6c 65 6d

To extract the target passphrase, we stripped the leading padding (00 02 [PS]) by searching for the 00 separator byte. The remaining bytes translated to:
Passphrase: Rak M3allem
Hex: 52616b204d33616c6c656d

Submitting this unpadded hex payload to Option 4 of the server successfully unlocked the flag: Securinets{l3g4cy_tl5_Pr0bl3m5}.
