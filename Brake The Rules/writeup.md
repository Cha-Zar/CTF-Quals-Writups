# Writeup: Brake The Rules

## Challenge Overview

The challenge provided a single modulus n and two different public exponents, e1​ and e2​, each with its corresponding ciphertext, c1​ and c2​. This setup is a classic indicator of a Common Modulus Attack.

## Vulnerability Analysis

When the same message m is encrypted twice using the same modulus n but different exponents e1​ and e2​, the message can be recovered if gcd(e1​,e2​)=1.

Using the Extended Euclidean Algorithm, we can find integers a and b such that:

```
ae1​+be2​=gcd(e1​,e2​)=1
```

By raising the ciphertexts to these powers, we can retrieve the original message:

```
(c1a​⋅c2b​)(modn)≡(me1​a⋅me2​b)(modn)≡mae1​+be2​(modn)≡m1(modn)
```

## Solution

To solve this efficiently, I used BitRSA, a specialized RSA CTF toolkit.

**Parameters Provided:**

```
n: 6016679753890303163142663245369767132888716702370395030807984388293531323087058493587913953264916322884638040426939660761879851940463636593392309666401889

e1: 7, e2: 11

c1: 3557675364189901347764643828793604180502918099353703973011364339563551107677056257500384809831638247352678007964873251772458547394121998900307874415958479

c2: 107264968886674099013558662764497088756114173794723900727253285828032857196526359305366881107052798457940254866734322603727735816717628320665756540450647
```

- **Tool Execution:** I loaded these parameters into `BitRSA.py` and selected Option 6: Common Modulus Attack.
- **Result:** The tool calculated the modular inverse and performed the exponentiation to recover the plaintext.

## Flag

`Securinets{c0mm0n_m0dulu5}`
