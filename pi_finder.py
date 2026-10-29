from math import isqrt

import threading

import tkinter as tk
from tkinter import ttk

import sys
sys.set_int_max_str_digits(0)  # 0 = no limit

CONTEXT = 150  # digits shown on each side of a match
DIGITS = 1_000_000

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
    """First n digits of pi after the decimal point (Chudnovsky algorithm)."""
    guard = 10
    digits = n + guard
    terms = digits // 14 + 2  # each term adds about 14 digits

    def bs(a, b):
        """Binary splitting: combine terms a..b-1 into three big integers."""
        if b - a == 1:
            if a == 0:
                Pab = Qab = 1
            else:
                Pab = (6 * a - 5) * (2 * a - 1) * (6 * a - 1)
                Qab = a * a * a * 10939058860032000  # 640320**3 // 24
            Tab = Pab * (13591409 + 545140134 * a)
            if a % 2:
                Tab = -Tab
            return Pab, Qab, Tab
        m = (a + b) // 2
        Pam, Qam, Tam = bs(a, m)
        Pmb, Qmb, Tmb = bs(m, b)
        return Pam * Pmb, Qam * Qmb, Qmb * Tam + Pam * Tmb

    _, Q, T = bs(0, terms)
    one = 10 ** digits
    sqrt_c = isqrt(10005 * one * one)  # integer square root of 10005
    pi = (Q * 426880 * sqrt_c) // T
    s = str(pi // 10 ** guard)
    return s[1:n + 1]

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

PALETTE = ["#000000", "#8b4513", "#e63946", "#f77f00", "#fcbf49",
           "#2a9d8f", "#1d6fd8", "#7b2cbf", "#9aa0a6", "#ffffff"]

class PixelWindow(tk.Toplevel):
    def __init__(self, parent, digits):
        super().__init__(parent)
        self.title("Pi as pixels")
        self.digits = digits
        self.img = None  # keep a reference or tkinter will discard the image

        bar = ttk.Frame(self, padding=10)
        bar.pack(fill="x")
        ttk.Label(bar, text="Width (pixels):").pack(side="left")
        self.width_var = tk.IntVar(value=100)
        spin = ttk.Spinbox(bar, from_=10, to=316, textvariable=self.width_var,
                           width=6, command=self.draw)
        spin.pack(side="left", padx=6)
        spin.bind("<Return>", lambda e: self.draw())
        self.info = tk.StringVar()
        ttk.Label(bar, textvariable=self.info).pack(side="left", padx=12)

        self.label = ttk.Label(self)  # a label can display an image
        self.label.pack(padx=10, pady=10)
        self.draw()

    def draw(self):
        try:
            w = int(self.width_var.get())
        except (tk.TclError, ValueError):
            return
        w = max(10, min(316, w))
        rows = min(w * w, len(self.digits)) // w
        img = tk.PhotoImage(width=w, height=rows)
        for r in range(rows):
            row = self.digits[r * w:(r + 1) * w]
            img.put("{" + " ".join(PALETTE[int(d)] for d in row) + "}", to=(0, r))
        zoom = max(1, 600 // w)  # make small grids bigger so they stay visible
        self.img = img.zoom(zoom, zoom)
        self.label.config(image=self.img)
        self.info.set(f"{w} x {rows} pixels = first {w * rows:,} digits, zoom x{zoom}")

class PiFinderApp:
    def __init__(self, root):
        self.root = root
        self.digits = ""
        self.letters = ""
        self.letters_shift = ""
        self.shift = tk.BooleanVar(value=False)
        self.hits = []
        self.current = 0
        self.seq = ""
        root.title("Pi Pattern Finder")
        root.geometry("900x500")

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Mode:").pack(side="left")
        self.mode = ttk.Combobox(top, values=["Numbers", "Letters"], width=9, state="readonly")
        ttk.Checkbutton(top, text="Shift 1", variable=self.shift, command=self.on_mode_change).pack(side="left", padx=(0, 12))
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

        self.pixels_btn = ttk.Button(top, text="Pixels", command=self.open_pixels, state="disabled")
        self.pixels_btn.pack(side="left", padx=(12, 0))

        self.status = tk.StringVar(value="Computing pi digits...")
        ttk.Label(root, textvariable=self.status, padding=(10, 0)).pack(anchor="w")

        self.text = tk.Text(root, wrap="char", font=("Courier New", 14),
                            padx=10, pady=10, state="disabled")
        self.text.pack(fill="both", expand=True, padx=10, pady=10)
        self.text.tag_configure("hit", background="#f5c542", foreground="black")

        threading.Thread(target=self.load_digits, daemon=True).start()

    @property
    def stream(self):
        """The text we're searching: digits, letters, or shifted letters."""
        if self.mode.get() == "Letters":
            return self.letters_shift if self.shift.get() else self.letters
        return self.digits

    def open_pixels(self):
        PixelWindow(self.root, self.digits)

    def load_digits(self):
        digits = compute_pi_digits(DIGITS)
        self.root.after(0, self.digits_ready, digits)

    def digits_ready(self, digits):
        self.digits = digits
        self.letters = digits_to_letters(digits)
        self.letters_shift = digits_to_letters(digits[1:])
        self.search_btn.config(state="normal")
        self.pixels_btn.config(state="normal")
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
            off = 1 if self.shift.get() else 0
            first = 2 * pos + 1 + off
            last = 2 * (pos + len(self.seq)) + off
            where = f"letter {pos + 1:,} (digits {first:,}-{last:,})"
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