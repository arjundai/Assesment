# EncryptDecrypt_Assessment.py

def encrypt_character(ch, shift1, shift2):
    # Lowercase rules
    if 'a' <= ch <= 'z':
        if ch <= 'm':  # a-m: forward by shift1 * shift2
            shift = (shift1 * shift2) % 26
            return chr(((ord(ch) - ord('a') + shift) % 26) + ord('a'))
        else:          # n-z: backward by shift1 + shift2
            shift = (shift1 + shift2) % 26
            return chr(((ord(ch) - ord('a') - shift) % 26) + ord('a'))

    # Uppercase rules
    if 'A' <= ch <= 'Z':
        if ch <= 'M':  # A-M: backward by shift1
            shift = shift1 % 26
            return chr(((ord(ch) - ord('A') - shift) % 26) + ord('A'))
        else:          # N-Z: forward by (shift2)^2
            shift = (shift2 * shift2) % 26
            return chr(((ord(ch) - ord('A') + shift) % 26) + ord('A'))

    # Other chars unchanged
    return ch


def decrypt_character(ch, shift1, shift2):
    """
    Because the mapping is not injective (collisions exist), we cannot
    always know the *exact* original. The robust approach is:
      - Try every possible original letter (within the same case).
      - Choose the one that re-encrypts to the current cipher character.
    This guarantees encrypt(decrypt(c)) == c (round-trip correctness).
    """
    if 'a' <= ch <= 'z':
        for i in range(26):
            cand = chr(ord('a') + i)
            if encrypt_character(cand, shift1, shift2) == ch:
                return cand
        return ch  # shouldn't happen

    if 'A' <= ch <= 'Z':
        for i in range(26):
            cand = chr(ord('A') + i)
            if encrypt_character(cand, shift1, shift2) == ch:
                return cand
        return ch  # shouldn't happen

    return ch  # non-letters unchanged


def encrypt_file(input_file, output_file, shift1, shift2):
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
    encrypted = "".join(encrypt_character(ch, shift1, shift2) for ch in text)
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        f.write(encrypted)
    return encrypted


def decrypt_file(input_file, output_file, shift1, shift2):
    with open(input_file, "r", encoding="utf-8") as f:
        cipher = f.read()
    decrypted = "".join(decrypt_character(ch, shift1, shift2) for ch in cipher)
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        f.write(decrypted)
    return decrypted


def verify_roundtrip(encrypted_file, shift1, shift2):
    """Checks encrypt(decrypt(cipher)) == cipher (always achievable)."""
    with open(encrypted_file, "r", encoding="utf-8") as f:
        cipher = f.read()
    reenc = "".join(encrypt_character(ch, shift1, shift2) for ch in
                    "".join(decrypt_character(ch, shift1, shift2) for ch in cipher))
    return reenc == cipher


def verify_strict(original_file, decrypted_file, report_mismatches=5):
    """Strict check: original == decrypted. Returns (ok, mismatches_list)."""
    with open(original_file, "r", encoding="utf-8") as f1, open(decrypted_file, "r", encoding="utf-8") as f2:
        original = f1.read()
        decrypted = f2.read()

    if original == decrypted:
        return True, []

    # collect first few mismatches (index, original_char, decrypted_char)
    mismatches = []
    n = min(len(original), len(decrypted))
    for i in range(n):
        if original[i] != decrypted[i]:
            mismatches.append((i, original[i], decrypted[i]))
            if len(mismatches) >= report_mismatches:
                break
    # if lengths differ, add a length mismatch hint
    if len(mismatches) < report_mismatches and len(original) != len(decrypted):
        mismatches.append(("length", len(original), len(decrypted)))
    return False, mismatches


# ----------------- MAIN PROGRAM -----------------
if __name__ == "__main__":
    shift1 = int(input("Enter shift1: "))
    shift2 = int(input("Enter shift2: "))

    # Step 1: Encrypt raw -> encrypted
    encrypt_file("raw_text.txt", "encrypted_text.txt", shift1, shift2)
    print("Encryption complete. Check 'encrypted_text.txt'.")

    # Step 2: Decrypt encrypted -> decrypted
    decrypt_file("encrypted_text.txt", "decrypted_text.txt", shift1, shift2)
    print("Decryption complete. Check 'decrypted_text.txt'.")

    # Step 3A: Round-trip verification (always achievable)
    if verify_roundtrip("encrypted_text.txt", shift1, shift2):
        print("Round-trip verification passed: encrypt(decrypt) == encrypted.")
    else:
        print("Round-trip verification failed (unexpected).")

    # Step 3B: Strict verification (may fail due to inherent collisions)
    ok, mismatches = verify_strict("raw_text.txt", "decrypted_text.txt")
    if ok:
        print("Strict verification passed: Original and Decrypted texts match exactly.")
    else:
        print("Strict verification: mismatch detected (expected with these rules).")
        # Show a few examples to illustrate why
        for m in mismatches:
            print("   Mismatch:", m)
        print("   Note: Collisions occur (e.g., 'T' and 'E' can both encrypt to 'C' when shift1=2, shift2=3).")

