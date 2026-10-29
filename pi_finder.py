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

def digits_to_letters(digits):
    """Turn each pair of digits (00-99) into a letter A-Z."""
    letters = []
    for i in range(0, len(digits) - 1, 2):
        letters.append(chr(ord("A") + int(digits[i:i + 2]) % 26))
    return "".join(letters)

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
        self.letters = ""
        self.hits = []
        self.current = 0
        self.seq = ""
        root.title("Pi Pattern Finder")
        root.geometry("900x500")

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Mode:").pack(side="left")
        self.mode = ttk.Combobox(top, values=["Numbers", "Letters"], width=9, state="readonly")
        self.mode.set("Numbers")
        self.mode.pack(side="left", padx=(4, 12))
        self.mode.bind("<<ComboboxSelected>>", self.on_mode_change)

        ttk.Label(top, text="Search:").pack(side="left")
        self.entry = ttk.Entry(top, width=20)
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

    @property
    def stream(self):
        """The text we're searching: digits or letters, depending on the mode."""
        return self.letters if self.mode.get() == "Letters" else self.digits

    def load_digits(self):
        digits = compute_pi_digits(100_000)
        self.root.after(0, self.digits_ready, digits)

    def digits_ready(self, digits):
        self.digits = digits
        self.letters = digits_to_letters(digits)
        self.search_btn.config(state="normal")
        self.status.set(f"Loaded {len(digits):,} digits of pi.")
        self.show_window(0, 0)

    def on_mode_change(self, event=None):
        self.hits = []
        self.prev_btn.config(state="disabled")
        self.next_btn.config(state="disabled")
        self.status.set(f"{self.mode.get()} mode. Type something and press Search.")
        self.show_window(0, 0)

    def search(self):
        if not self.digits:
            return
        raw = self.entry.get().strip()
        if self.mode.get() == "Letters":
            seq = raw.upper()
            if not (seq.isalpha() and seq.isascii()):
                self.status.set("Enter letters only (A-Z).")
                return
        else:
            seq = raw
            if not seq.isdigit():
                self.status.set("Enter digits only (0-9).")
                return
        self.seq = seq
        self.hits = find_all(self.stream, seq)
        self.current = 0
        if not self.hits:
            self.status.set(f"'{seq}' not found in this stream.")
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            return
        self.prev_btn.config(state="normal")
        self.next_btn.config(state="normal")
        self.show_current()

    def step(self, delta):
        if self.hits:
            self.current = (self.current + delta) % len(self.hits)
            self.show_current()

    def show_current(self):
        pos = self.hits[self.current]
        if self.mode.get() == "Letters":
            # letter i was made from digits 2i+1 and 2i+2 (counting from 1)
            where = f"letter {pos + 1:,} (digits {2 * pos + 1:,}-{2 * (pos + len(self.seq)):,})"
        else:
            where = f"digit {pos + 1:,}"
        self.status.set(f"Match {self.current + 1} of {len(self.hits):,} - starts at {where}")
        self.show_window(pos, len(self.seq))

    def show_window(self, pos, length):
        s = self.stream
        start = max(0, pos - CONTEXT)
        end = min(len(s), pos + length + CONTEXT)
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", s[start:pos])
        self.text.insert("end", s[pos:pos + length], "hit")
        self.text.insert("end", s[pos + length:end])
        self.text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    PiFinderApp(root)
    root.mainloop()