from collections import namedtuple
import unittest
import os

from src.vm import compute
from src.opcodes import LOAD, STORE, ADD, SUB, MUL, DIV, REM , HALT, ADDI, SUBI , JUMP, BEQZ, BEQ

VMCase = namedtuple('VMCase', ['x', 'y', 'out'])
VMTest = namedtuple('VMTest', ['name', 'asm', 'cases'])

main_tests = [
    VMTest('Halt', 'halt', [VMCase(0, 0, 0)]),
    VMTest('LoadStore', """
load r1 1
store r1 0
halt""", [VMCase(1, 0, 1), VMCase(255, 0, 255)]),
    VMTest('Add', """
load r1 1
load r2 2
add r1 r2
store r1 0
halt""", [
    VMCase(1, 2, 3),     # 1 + 2 = 3
    VMCase(254, 1, 255), # support max int
    VMCase(255, 1, 0),   # correctly overflow
    ]),
VMTest('Subtract', """
load r1 1
load r2 2
sub r1 r2
store r1 0
halt""", [
    VMCase(5, 3, 2),
    VMCase(0, 1, 255),  # correctly overflow backwards
    ]),
VMTest('MULTIPLE', """
load r1 1
load r2 2
mul  r1 r2
store r1 0
halt
""", [
    VMCase(5, 5, 25),
    VMCase(52, 5, 4)
    ]),

VMTest('DIV', """
load r1 1
load r2 2
div r1 r2
store r1 0
halt
""", [
    VMCase(5, 5, 1),
    #VMCase(300, 1, 1),
    ]),

VMTest('REM', """
load r1 1
load r2 2
rem r1 r2
store r1 0
halt
""", [
    VMCase(10, 3, 1),
    VMCase(20, 3, 2),
    #VMCase(300, 1, 1),
    ]),
]

stretch_goal_tests = [
    VMTest('Jump', """
load r1 1
jump 16
store r1 0
halt""", [VMCase(42, 0, 0)]),
    VMTest('Beqz', """
load r1 1
load r2 2
beqz r2 3
store r1 0
halt""", [
    VMCase(42, 0, 0),   # r2 is zero, so should branch over the store
    VMCase(42, 1, 42),  # r2 is nonzero, so should store back 42
    ]),
VMTest('Addi', """
load r1 1
addi r1 3
addi r1 5
store r1 0
halt""", [
    VMCase(0, 0, 8),    # 0 + 3 + 5 = 8
    VMCase(20, 0, 28),  # 20 + 3 + 5 = 28
    ]),
VMTest('Sum to n', """
load r1 1
beqz r1 8
add r2 r1
subi r1 1
jump 11
store r2 0
halt""", [
    VMCase(0, 0, 0),
    VMCase(1, 0, 1),
    VMCase(5, 0, 15),
    VMCase(10, 0, 55),
    ]),
VMTest('Sum to n BEQ', """
load r1 1
beq r1 0 8
add r2 r1
subi r1 1
jump 11
store r2 0
halt""", [
    VMCase(0, 0, 0),
    VMCase(1, 0, 1),
    VMCase(5, 0, 15),
    VMCase(10, 0, 55),
    ]),
]

class TestVM(unittest.TestCase):
    def test_compute(self):
        for test in main_tests:
            with self.subTest(name=test.name):
                self.run_vm_test(test)

        if os.getenv('STRETCH') == 'true':
            for test in stretch_goal_tests:
                with self.subTest(name=test.name):
                    self.run_vm_test(test)
        else:
            print('Skipping stretch goal tests. Run `STRETCH=true python -m unittest test_vm.py` to include them.')

    def run_vm_test(self, test):
        # Assemble code and load into memory
        memory = bytearray(256)
        code = assemble(test.asm)
        memory[8:8+len(code)] = code

        # For each case, set inputs and run vm
        for case in test.cases:
            memory[1] = case.x
            memory[2] = case.y

            compute(memory)

            actual = memory[0]
            self.assertEqual(actual, case.out, f'Expected f({case.x}, {case.y}) to be {case.out}, not {actual}')

            memory[1] = 0
            memory[2] = 0

def reg(s):
    return {'r1': 0x01, 'r2': 0x02}[s]

def mem(s):
    return int(s) & 0xFF

def imm(s):
    # for now, immediate values and memory addresses are both just ints
    return mem(s)

def assemble(asm):
    mc = bytearray()
    asm = asm.strip()
    for line in asm.split('\n'):
        parts = line.strip().split()
        if not parts:
            continue
        op = parts[0]
        if op == 'load':
            mc.extend([LOAD, reg(parts[1]), mem(parts[2])])
        elif op == 'store':
            mc.extend([STORE, reg(parts[1]), mem(parts[2])])
        elif op == 'add':
            mc.extend([ADD, reg(parts[1]), reg(parts[2])])
        elif op == 'sub':
            mc.extend([SUB, reg(parts[1]), reg(parts[2])])
        elif op == 'mul':
            mc.extend([MUL, reg(parts[1]), reg(parts[2])])
        elif op == 'div':
            mc.extend([DIV, reg(parts[1]), reg(parts[2])])
        elif op == 'rem':
            mc.extend([REM, reg(parts[1]), reg(parts[2])])
        elif op == 'addi':
            mc.extend([ADDI, reg(parts[1]), imm(parts[2])])
        elif op == 'subi':
            mc.extend([SUBI, reg(parts[1]), imm(parts[2])])
        elif op == 'jump':
            mc.extend([JUMP, imm(parts[1])])
        elif op == 'beqz':
            mc.extend([BEQZ, reg(parts[1]), imm(parts[2])])
        elif op == 'halt':
            mc.append(HALT)
        elif op == 'beq':
            mc.extend([BEQ,  reg(parts[1]), imm(parts[2]),  imm(parts[3])])
        else:
            raise ValueError(f'Invalid operation: {op}')
    return mc


if __name__ == '__main__':
    unittest.main()

