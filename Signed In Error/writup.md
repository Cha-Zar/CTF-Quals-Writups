Challenge Overview

We were given a public modulus $n$, exponent $e$, a valid signature (sig_good), and a faulty signature (sig_fault) for the same message. An encrypted ciphertext containing the flag was also provided.

Vulnerability Analysis

The vulnerability is known as the Bellcore Attack. It targets RSA implementations using the Chinese Remainder Theorem (CRT). If a computation error (fault) occurs during the signing process for one of the primes (e.g., $q$), the faulty signature $s'$ will be correct modulo $p$ but incorrect modulo $q$.

Because $s \equiv s' \pmod{p}$, the difference $s - s'$ is a multiple of $p$. We can factor $n$ by calculating:

$$\gcd(|sig_{good} - sig_{fault}|, n) = p$$

Solution

Factorization: Calculated $p = \gcd(|sig\_good - sig\_fault|, n)$.

Private Key Recovery: Derived $q = n // p$, then calculated $d = e^{-1} \pmod{\phi(n)}$.

Decryption: Decrypted the ciphertext using the recovered private key.

Results:

p: 106604878787300545228308569665690395211132416432065297017069043337630105817391

q: 62582197564766780397735003967279299802711218864639282107372353782924674763119

Flag: Securinets{0n3_b4d_s1gn4tur3_0n3_l05t_pr1m3}
