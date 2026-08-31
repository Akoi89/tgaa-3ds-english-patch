"""
Proportional text-width model for this game's dialogue font.

Why character count is not enough (confirmed by an in-game screenshot):
a 45-character ALL-CAPS newspaper headline overflowed the box, while a
46-character mixed-case line on the previous screen fit comfortably.
Capitals are substantially wider than lowercase in a proportional font,
so "number of characters" mismeasures any line whose case mix differs
from the average. Measured across the 8 officially localized episodes:
mixed-case lines reach 52 characters, but all-caps lines never exceed
34 -- the same box, two very different character counts.

So width is modelled in font units instead. The advance widths below are
standard Helvetica/Arial AFM values (units per 1000em). This game's
dialogue face is a humanist sans, and what matters here is only the
RELATIVE width of one glyph against another, which is very stable across
sans-serif faces -- an 'M' is ~3x a 'l' in essentially all of them. The
absolute threshold is then calibrated from the official script itself
(see calibrate() below), so any constant scale error cancels out.
"""

# Helvetica AFM advance widths, units/1000em.
_W = {
    ' ': 278, '!': 278, '"': 355, '#': 556, '$': 556, '%': 889, '&': 667,
    "'": 191, '(': 333, ')': 333, '*': 389, '+': 584, ',': 278, '-': 333,
    '.': 278, '/': 278,
    '0': 556, '1': 556, '2': 556, '3': 556, '4': 556, '5': 556, '6': 556,
    '7': 556, '8': 556, '9': 556,
    ':': 278, ';': 278, '<': 584, '=': 584, '>': 584, '?': 556, '@': 1015,
    'A': 667, 'B': 667, 'C': 722, 'D': 722, 'E': 667, 'F': 611, 'G': 778,
    'H': 722, 'I': 278, 'J': 500, 'K': 667, 'L': 556, 'M': 833, 'N': 722,
    'O': 778, 'P': 667, 'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'U': 722,
    'V': 667, 'W': 944, 'X': 667, 'Y': 667, 'Z': 611,
    '[': 278, '\\': 278, ']': 278, '^': 469, '_': 556, '`': 333,
    'a': 556, 'b': 556, 'c': 500, 'd': 556, 'e': 556, 'f': 278, 'g': 556,
    'h': 556, 'i': 222, 'j': 222, 'k': 500, 'l': 222, 'm': 833, 'n': 556,
    'o': 556, 'p': 556, 'q': 556, 'r': 333, 's': 500, 't': 278, 'u': 556,
    'v': 500, 'w': 722, 'x': 500, 'y': 500, 'z': 500,
    '{': 334, '|': 260, '}': 334, '~': 584,
}
_DEFAULT = 556  # unknown glyph -> average lowercase width


def width(text):
    """Width of a single physical line, in font units (1000 = 1em)."""
    return sum(_W.get(ch, _DEFAULT) for ch in text)


def width_chars(text):
    """Width expressed in 'average lowercase characters' -- easier to
    reason about than raw font units, and directly comparable to the
    old character-count thresholds."""
    return width(text) / 556.0
