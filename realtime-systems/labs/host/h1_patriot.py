"""Lab H1c: why a clock that is "almost right" gets worse every hour (Patriot, 1991).

The Patriot's clock counted tenths of a second as an integer. To use it, the software multiplied
the count by 1/10 in a fixed-point register. 1/10 has no exact binary representation, and the
stored value was *chopped* (truncated), so every tick carries the same tiny error. The error in the
reported time is therefore  (number of ticks) x (error per tick)  -- linear in uptime.

GAO/IMTEC-92-26 gives the table (hours -> clock error): 1 h 0.0034 s, 8 h 0.0275 s, 20 h 0.0687 s,
48 h 0.1648 s, 72 h 0.2472 s, 100 h 0.3433 s.  This script reproduces it.

    python3 h1_patriot.py
"""
from fractions import Fraction

TENTH = Fraction(1, 10)


def chopped(frac_bits: int) -> Fraction:
    """1/10 chopped (not rounded) to `frac_bits` binary places after the point."""
    scale = 1 << frac_bits
    return Fraction(int(TENTH * scale), scale)


def drift_seconds(hours: float, frac_bits: int) -> float:
    ticks = int(hours * 3600 * 10)
    return float(ticks * (TENTH - chopped(frac_bits)))


if __name__ == "__main__":
    # GAO/IMTEC-92-26 table: hours -> (clock inaccuracy in seconds, approximate shift in the range gate in metres)
    gao = {1: (0.0034, 7), 8: (0.0275, 55), 20: (0.0687, 137), 48: (0.1648, 330), 72: (0.2472, 494), 100: (0.3433, 687)}
    for bits in (23, 24):
        err = float(TENTH - chopped(bits))
        print("1/10 chopped to %d binary places after the point: error per tick = %.3e s" % (bits, err))
    print()
    print("hours   our drift (23 places)   GAO clock error   GAO range-gate shift (m)   implied speed (m/s)")
    for h, (g, shift) in gao.items():
        d = drift_seconds(h, 23)
        print("%5d   %12.4f s        %9.4f s   %14d              %8.0f" % (h, d, g, shift, shift / g))
    print()
    print("The 23-place chop matches the GAO table to 4 decimals. The register is 24 bits wide, and because")
    print("0.1 < 0.5 its first fractional bit is zero, so the stored value effectively keeps 23 places.")
    print("(This explanation of the match is ours; GAO states only that the register is 24 bits.)")
    print("The range-gate shifts are GAO's numbers; they imply a closing speed of about 2,000 m/s.")
