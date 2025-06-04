# Constants for opcodes
LOAD = 0x01
STORE = 0x02
ADD = 0x03
SUB = 0x04
HALT = 0xff

# Stretch goals
ADDI = 0x05
SUBI = 0x06
JUMP = 0x07
BEQZ = 0x08


registerMap = {
    "r1": 1,
    "r2": 2
}

def compute(memory):
    #print("SEE TTHIS", memory[8],memory)
  #  print("before", memory)
    """
    Given a 256 byte array of "memory", run the stored program
    to completion, modifying the data in place to reflect the result

    The memory format is:

    00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f ... ff
    **        **... __
    ^==DATA===============^ ^==INSTRUCTIONS==============^
    """
    registers = [8, 0, 0]  # PC, R1 and R2


    # start at 8
    # should follow fetch decode execute
    while True:  # keep looping, like a physical computer's clock
        pc = registers[0]
        registers[0] += 3

        opcode = memory[pc]
        if opcode == HALT:
            break

        arg1 =  memory[pc+1]
        if opcode == JUMP:
            registers[0] = arg1
            continue

        arg2 =  memory[pc+2]

        
        if opcode == ADD:
            res =  registers[arg1] + registers[arg2]
            registers[arg1] = res & 0xff
        elif opcode == LOAD:
            registers[arg1] = memory[arg2]
        elif opcode == SUB:
            res = registers[arg1]  - registers[arg2]
            registers[arg1] = res & 0xff
        elif opcode == STORE:
            memory[arg2] = registers[arg1]
            # Constants for opcodes
        elif opcode == ADDI:
            registers[arg1] = (arg2 + registers[arg1]) & 0xff
        elif opcode == SUBI:
            registers[arg1] = (registers[arg1] - arg2) & 0xff
        elif opcode == BEQZ:
            if registers[arg1] == 0:
                registers[0] += arg2
        else:
            raise ValueError(f"Illegal opcode detected: {opcode}")
       # break

    print("after", list(memory), registers)


if __name__ == "__main__":
    r1 = 1
    r2 = 2
    compute([0, 3, 45, 0, 0, 0, 0, 0, LOAD, r1, 0x01, BEQZ, r1, 0x02, ADD, r2, r1, SUBI, r1, 0x01, STORE, r2, 0x00, HALT])
#    compute([0, 3, 45, 0, 0, 0, 0, 0, LOAD, r1, 0x01, LOAD, r2, 0x02, ADDI, r1, 7, JUMP, 22 , SUBI, r1, 0x01, STORE, r1, 0x00, HALT])
    # compute([0, 78, 0, 0, 0, 0, 0, 0, LOAD, "r1", 0x1, HALT])
