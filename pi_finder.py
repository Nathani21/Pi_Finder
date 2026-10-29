import threading

import tkinter as tk
from tkinter import ttk

import sys
sys.set_int_max_str_digits(0)  # 0 = no limit

CONTEXT = 150  # digits shown on each side of a match

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
        self.hits = []
        self.current = 0
        self.seq = ""
        root.title("Pi Pattern Finder")
        root.geometry("760x500")

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Number sequence:").pack(side="left")
        self.entry = ttk.Entry(top, width=24)
        self.entry.pack(side="left", padx=6)
        self.entry.bind("<Return>", lambda e: self.search())
        self.search_btn = ttk.Button(top, text="Search", command=self.search, state="disabled")
        self.search_btn.pack(side="left")
        self.prev_btn = ttk.Button(top, text="< Prev", command=lambda: self.step(-1), state="disabled")
        self.prev_btn.pack(side="left", padx=(12, 2))
        self.next_btn = ttk.Button(top, text="Next >", command=lambda: self.step(1), state="disabled")
        self.next_btn.pack(side="left")

        self.status = tk.StringVar(value="Computing pi digits...")
        ttk.Label(root, textvariable=self.status, padding=(10, 0)).pack(anchor="w")

        self.text = tk.Text(root, wrap="char", font=("Courier New", 14),
                            padx=10, pady=10, state="disabled")
        self.text.pack(fill="both", expand=True, padx=10, pady=10)
        self.text.tag_configure("hit", background="#f5c542", foreground="black")

        threading.Thread(target=self.load_digits, daemon=True).start()

    def load_digits(self):
        digits = compute_pi_digits(100_000)
        self.root.after(0, self.digits_ready, digits)

    def digits_ready(self, digits):
        self.digits = digits
        self.search_btn.config(state="normal")
        self.status.set(f"Loaded {len(digits):,} digits of pi.")
        self.show_window(0, 0)

    def search(self):
        if not self.digits:
            return
        seq = self.entry.get().strip()
        if not seq.isdigit():
            self.status.set("Enter digits only (0-9).")
            return
        self.seq = seq
        self.hits = find_all(self.digits, seq)
        self.current = 0
        if not self.hits:
            self.status.set(f"'{seq}' not found in the first {len(self.digits):,} digits.")
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            return
        self.prev_btn.config(state="normal")
        self.next_btn.config(state="normal")
        self.show_current()

    def step(self, delta):
        if self.hits:
            self.current = (self.current + delta) % len(self.hits)  # wraps around
            self.show_current()

    def show_current(self):
        pos = self.hits[self.current]
        self.status.set(
            f"Match {self.current + 1} of {len(self.hits):,} "
            f"- starts at digit {pos + 1:,}"
        )
        self.show_window(pos, len(self.seq))

    def show_window(self, pos, length):
        start = max(0, pos - CONTEXT)
        end = min(len(self.digits), pos + length + CONTEXT)
        self.text.config(state="normal")   # unlock to edit
        self.text.delete("1.0", "end")
        self.text.insert("end", self.digits[start:pos])
        self.text.insert("end", self.digits[pos:pos + length], "hit")  # highlighted part
        self.text.insert("end", self.digits[pos + length:end])
        self.text.config(state="disabled")  # lock so it can't be typed in

if __name__ == "__main__":
    root = tk.Tk()
    PiFinderApp(root)
    root.mainloop()