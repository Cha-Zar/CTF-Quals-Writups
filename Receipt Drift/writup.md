Challenge Overview

The challenge presents a "lottery" service where numbers are generated using a Linear Congruential Generator (LCG). However, the service does not leak the raw states of the generator directly. Instead, it provides "receipts" which are the sums of two consecutive states ($y_n = x_n + x_{n+1}$).

The goal is to recover the internal parameters of the LCG and predict the next six hidden states ($x_1$ through $x_6$).

Technical Details

The Generator

An LCG follows the recurrence relation:


$$x_{n+1} = (a \cdot x_n + b) \pmod{p}$$

The "receipts" provided by the server are calculated as:


$$y_n = x_n + x_{n+1}$$

Substituting the LCG relation into the receipt equation:


$$y_n = x_n + (a \cdot x_n + b) = (a + 1)x_n + b \pmod{p}$$

Mathematical Vulnerability

By analyzing the relationship between consecutive receipts, we can recover the multiplier ($a$) and the increment ($b$).

Finding $a$:
Since $y_n$ is a linear transformation of $x_n$, the receipts themselves follow a shifted LCG pattern:


$$y_{n+1} - y_n = a(y_n - y_{n-1}) \pmod{p}$$


Therefore:


$$a = (y_2 - y_1) \cdot (y_1 - y_0)^{-1} \pmod{p}$$

Finding $b$:
Once $a$ is known, we can find the "effective increment" of the $y$ sequence and derive $b$:


$$b = (y_1 - a \cdot y_0) \cdot 2^{-1} \pmod{p}$$

Recovering the initial state $x_0$:
With $a$ and $b$ recovered, we use the first receipt $y_0$:


$$y_0 = (a + 1)x_0 + b \pmod{p}$$

$$x_0 = (y_0 - b) \cdot (a + 1)^{-1} \pmod{p}$$

Solution Script Logic

The solver performs the following steps:

Connection: Connects to the server via TCP socket and parses JSONL responses.

Data Collection: Requests the modulus $p$ using the info action and the receipts $y$ using the receipts action.

Parameter Recovery: Implements the modular inverse and arithmetic logic described above to find $a$, $b$, and $x_0$.

State Generation: Iterates the LCG to generate the sequence $x_0, x_1, \dots, x_6$.

Submission: Sends the predicted values $x_1$ to $x_6$ back to the server.

Flag

Upon successful prediction, the server returns the flag:
Securicon{L0tt3ry_15_r15ky}
