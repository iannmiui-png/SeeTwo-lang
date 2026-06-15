#!/usr/bin/env python3
# See Two? reference interpreter (compact)
# Author: assistant
# Usage: python seetwo.py program.st2
# Or run as a module to execute built-in examples and tests.

from typing import List, Tuple, Dict, Optional
import sys
import unittest

# --- Configuration / mappings ------------------------------------------------

# Palochka character used as stick (U+04C0)
PALOCHKA = '\u04C0'  # Ӏ

# Loader: map simple pcx symlink names to primitive opcode sequences (pgm)
PCX_TO_PGM: Dict[str, str] = {
    # Example mappings; extend as needed
    "zCeq.pcx": "=",   # equals primitive
    "zCdo.pcx": "D",   # dodecahedron primitive
    "zCha.pcx": "▩",   # square primitive
    "zCit.pcx": "V",   # V primitive
}

# Map high-level primitives to concrete opcode sequences
PRIMITIVE_TO_OPS: Dict[str, str] = {
    "=": "c",   # map '=' to increment axis 0
    "V": "D",   # map 'V' to toggle axis 2 (program begin)
    "▩": "e",   # map square to exponent (rotate palochka)
    # Dodecahedron literal handled separately
}

# --- Runtime state ----------------------------------------------------------

class Runtime:
    def __init__(self, code: List[str]):
        self.code = code
        self.ip = 0
        # group bits b0,b1,b2 stored as integer 0..7
        self.group = 0
        # dodecahedron 4 palochka bits stored as integer 0..15
        self.dodec = 0
        # accumulators: primary uses group by default
        self.acc_primary_mode = 'group'  # 'group' or 'dodec'
        self.acc_secondary_mode = 'dodec'
        self.call_stack: List[int] = []
        self.running = True
        self.output = []  # collect output for testing

    # Helpers to read/write accumulators
    def get_acc(self, which='primary') -> int:
        mode = self.acc_primary_mode if which == 'primary' else self.acc_secondary_mode
        return self.group if mode == 'group' else self.dodec

    def set_acc(self, value: int, which='primary'):
        value &= 0xF
        if which == 'primary':
            if self.acc_primary_mode == 'group':
                self.group = value & 0x7
            else:
                self.dodec = value & 0xF
        else:
            if self.acc_secondary_mode == 'group':
                self.group = value & 0x7
            else:
                self.dodec = value & 0xF

    def toggle_group_axis(self, axis: int):
        mask = 1 << axis
        self.group ^= mask
        self.group &= 0x7

    def rotate_dodec_left(self, steps=1):
        steps %= 4
        self.dodec = ((self.dodec << steps) | (self.dodec >> (4 - steps))) & 0xF

    # Execution of a single opcode
    def step(self):
        if self.ip < 0 or self.ip >= len(self.code):
            self.running = False
            return
        op = self.code[self.ip]
        self.ip += 1

        # Concrete opcode semantics
        if op == 'c':
            # toggle axis 0
            self.toggle_group_axis(0)
        elif op == 'd':
            # toggle axis 1
            self.toggle_group_axis(1)
        elif op == 'D':
            # toggle axis 2 and mark program start (same as toggle)
            self.toggle_group_axis(2)
        elif op == 'e':
            # exponent: rotate palochka bits left by 1
            self.rotate_dodec_left(1)
        elif op == 'a':
            # alternate accumulator: swap primary/secondary modes
            self.acc_primary_mode, self.acc_secondary_mode = self.acc_secondary_mode, self.acc_primary_mode
        elif op == 'o':
            # output ASCII of primary accumulator
            val = self.get_acc('primary')
            try:
                ch = chr(val)
            except Exception:
                ch = '?'
            self.output.append(ch)
            print(ch, end='', flush=True)
        elif op == 'n':
            # output numeric value of primary accumulator
            val = self.get_acc('primary')
            s = str(val)
            self.output.append(s)
            print(s, end='', flush=True)
        elif op == 'h':
            self.running = False
        elif op == 'r':
            # return: pop IP or jump to secondary accumulator value
            if self.call_stack:
                self.ip = self.call_stack.pop()
            else:
                # jump to address in secondary accumulator (bounded)
                addr = self.get_acc('secondary')
                self.ip = max(0, min(addr, len(self.code)))
        elif op == PALOCHKA * 1 or op.startswith(PALOCHKA):
            # Dodecahedron literal token: set dodec bits from count of palochkas
            count = len(op)
            self.dodec = count & 0xF
        elif op == '#':
            # comment/no-op
            pass
        else:
            # Unknown token: ignore or treat as no-op
            pass

    def run(self, max_steps: Optional[int] = 100000):
        steps = 0
        while self.running and steps < max_steps:
            self.step()
            steps += 1
        return ''.join(self.output)

# --- Tokenizer / Loader -----------------------------------------------------

def normalize_source(src: str) -> str:
    # Normalize line endings and strip BOMs if present
    return src.replace('\r\n', '\n').replace('\r', '\n')

def expand_pcx_tokens(src: str) -> str:
    # Replace occurrences of pcx filenames with their pgm primitives
    for pcx, pgm in PCX_TO_PGM.items():
        src = src.replace(pcx, pgm)
    return src

def tokenize(src: str) -> List[str]:
    src = normalize_source(src)
    src = expand_pcx_tokens(src)
    tokens: List[str] = []
    i = 0
    while i < len(src):
        ch = src[i]
        # collapse runs of palochka into a single token
        if ch == PALOCHKA:
            j = i
            while j < len(src) and src[j] == PALOCHKA:
                j += 1
            tokens.append(src[i:j])  # e.g., 'Ӏ', 'ӀӀ', up to 4
            i = j
            continue
        # skip whitespace and newlines
        if ch.isspace():
            i += 1
            continue
        # single-char tokens
        tokens.append(ch)
        i += 1
    # Expand high-level primitives into concrete ops
    expanded: List[str] = []
    for t in tokens:
        if t in PRIMITIVE_TO_OPS:
            expanded.extend(list(PRIMITIVE_TO_OPS[t]))
        else:
            expanded.append(t)
    return expanded

# --- Example programs -------------------------------------------------------

EXAMPLES: Dict[str, str] = {
    "count0to7": "n c n c n c n c n c n c n c n n h",
    # Explanation: print numeric primary (initial 0), toggle axis0 (c) repeatedly to show 0..7
    "dodec_demo": f"{PALOCHKA*1} e {PALOCHKA*2} e o h",
    # Set dodec=1, rotate, set dodec=2, rotate, output ASCII of primary (group) then halt
}

# --- CLI / runner -----------------------------------------------------------

def run_source(src: str):
    tokens = tokenize(src)
    rt = Runtime(tokens)
    return rt.run()

def run_file(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    return run_source(src)

# --- Unit tests -------------------------------------------------------------

class TestSeeTwo(unittest.TestCase):
    def test_toggle_axes(self):
        src = "c d D h"
        rt = Runtime(tokenize(src))
        rt.run()
        # c toggles axis0 -> 1, d toggles axis1 -> 3, D toggles axis2 -> 7
        self.assertEqual(rt.group, 0b111)

    def test_dodec_rotate(self):
        src = f"{PALOCHKA*1} e h"
        rt = Runtime(tokenize(src))
        rt.run()
        # start with dodec=1, rotate left -> 2
        self.assertEqual(rt.dodec, 0b0010)

    def test_output_numeric(self):
        src = "n c n h"
        rt = Runtime(tokenize(src))
        out = rt.run()
        # prints "0" then toggles axis0 -> 1 then prints "1"
        self.assertIn("0", out)
        self.assertIn("1", out)

    def test_pcx_expansion(self):
        src = "zCeq.pcx zCdo.pcx h"
        tokens = tokenize(src)
        # zCeq.pcx -> '=', which maps to 'c'; zCdo.pcx -> 'D'
        self.assertIn('c', tokens)
        self.assertIn('D', tokens)

# --- Self-test runner -------------------------------------------------------

def run_examples():
    print("=== Examples ===")
    for name, src in EXAMPLES.items():
        print(f"\n-- {name} --")
        print("source:", src)
        print("output:", run_source(src))

def run_tests():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSeeTwo)
    runner = unittest.TextTestRunner()
    runner.run(suite)

# --- Main -------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("See Two? interpreter demo")
        run_examples()
        print("\nRunning unit tests...")
        run_tests()
    else:
        # run file passed as argument
        path = sys.argv[1]
        run_file(path)
