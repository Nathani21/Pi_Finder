import sys
sys.set_int_max_str_digits(0)  # 0 = no limit

def find_all(digits, sequence):
    """Return every start index of sequence in digits (overlaps allowed)."""
    hits = []
    start = digits.find(sequence)
    while start != -1:
        hits.append(start)
        start = digits.find(sequence, start + 1)
    return hits

def compute_pi_digits(n):
    """Return the first n digits of pi after the decimal point, as a string."""
    guard = 10  # extra digits so rounding errors don't hit the ones we keep
    scale = 10 ** (n + guard)

    def arctan_inv(x):
        # arctan(1/x) = 1/x - 1/(3x^3) + 1/(5x^5) - ...
        total = term = scale // x
        x2 = x * x
        k = 1
        sign = -1
        while term:
            term //= x2
            k += 2
            total += sign * (term // k)
            sign = -sign
        return total

    # Machin's formula: pi = 16*arctan(1/5) - 4*arctan(1/239)
    pi = 16 * arctan_inv(5) - 4 * arctan_inv(239)
    s = str(pi // 10 ** guard)  # "3" followed by n decimals
    return s[1:n + 1]


if __name__ == "__main__":
    digits = compute_pi_digits(100_000)
    print(len(digits))

    hits = find_all(digits, "999999")
    print(hits)
    print("first hit is digit", hits[0] + 1)