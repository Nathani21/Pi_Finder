import threading

import tkinter as tk
from tkinter import ttk

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

class PiFinderApp:
    def __init__(self, root):
        self.root = root
        self.digits = ""
        root.title("Pi Pattern Finder")
        root.geometry("700x300")

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Number sequence:").pack(side="left")
        self.entry = ttk.Entry(top, width=24)
        self.entry.pack(side="left", padx=6)
        self.entry.bind("<Return>", lambda e: self.search())
        self.search_btn = ttk.Button(top, text="Search", command=self.search, state="disabled")
        self.search_btn.pack(side="left")

        self.status = tk.StringVar(value="Computing pi digits...")
        ttk.Label(root, textvariable=self.status, padding=10).pack(anchor="w")

        threading.Thread(target=self.load_digits, daemon=True).start()

    def load_digits(self):
        digits = compute_pi_digits(100_000)
        self.root.after(0, self.digits_ready, digits)  # hand the result back to the GUI thread

    def digits_ready(self, digits):
        self.digits = digits
        self.search_btn.config(state="normal")
        self.status.set(f"Loaded {len(digits):,} digits of pi.")

    def search(self):
        if not self.digits:  # Enter key works even while the button is disabled
            return
        seq = self.entry.get().strip()
        if not seq.isdigit():
            self.status.set("Enter digits only (0-9).")
            return
        hits = find_all(self.digits, seq)
        if not hits:
            self.status.set(f"'{seq}' not found in the first {len(self.digits):,} digits.")
        else:
            self.status.set(f"Found {len(hits):,} time(s). First at digit {hits[0] + 1:,}.")

if __name__ == "__main__":
    root = tk.Tk()
    PiFinderApp(root)
    root.mainloop()