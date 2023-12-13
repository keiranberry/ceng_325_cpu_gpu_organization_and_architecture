import byte

def convertToSigned(value):
    if value[0] == "1":
        inverted_str = ''.join('1' if bit == '0' else '0' for bit in value)

        carry = 1
        result_list = []
        for bit in reversed(inverted_str):
            new_bit = (int(bit) + carry) % 2
            carry = (int(bit) + carry) // 2
            result_list.insert(0, str(new_bit))

        result_str = ''.join(result_list)
        return "-0b" + result_str
    return value


def convertToUnsigned(value):
    if(value < 0):
        value = abs(value)
        value = bin(value)[2:]
        inverted_str = ''.join('1' if bit == '0' else '0' for bit in value)
        carry = 1
        result_list = []
        for bit in reversed(inverted_str):
            new_bit = (int(bit) + carry) % 2
            carry = (int(bit) + carry) // 2
            result_list.insert(0, str(new_bit))

        result_str = ''.join(result_list)
        while len(result_str < 32):
            result_str = "1" + result_str
        return int(result_str, 2)
    return value

# i format instructions
def executeIInstruction(memory, registers, rd, rs1, imm, inst):
    instruction = inst.lower()

    if instruction == "lb":
        lb(memory, registers, rd, rs1, imm)
    elif instruction == "addi":
        addi(registers, rd, rs1, imm)
    elif instruction == "jalr":
        jalr(registers, rd, rs1, imm)
    elif instruction == "lh":
        lh(memory, registers, rd, rs1, imm)
    elif instruction == "slli":
        slli(registers, rd, rs1, imm)
    elif instruction == "lw":
        lw(memory, registers, rd, rs1, imm)
    elif instruction == "slti":
        slti(registers, rd, rs1, imm)
    elif instruction == "sltiu":
        sltiu(registers, rd, rs1, imm)
    elif instruction == "lbu":
        lbu(memory, registers, rd, rs1, imm)
    elif instruction == "xori":
        xori(registers, rd, rs1, imm)
    elif instruction == "lhu":
        lhu(memory, registers, rd, rs1, imm)
    elif instruction == "srli":
        srli(registers, rd, rs1, imm)
    elif instruction == "srai":
        srai(registers, rd, rs1, imm)
    elif instruction == "ori":
        ori(registers, rd, rs1, imm)
    else:
        andi(registers, rd, rs1, imm)

def lb(memory, registers, rd, rs1, imm):
    imm = convertToSigned(imm)
    address = registers[int(rs1, 2) + 1] + int(imm, 2)
    value = memory[address].hexValue
    value = bin(value)[2:].zfill(8)
    sign = value[0]
    value = (sign * 24) + value
    registers[int(rd, 2) + 1] = int(value, 2)



def addi(registers, rd, rs1, imm):
    imm = convertToSigned(imm)
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] + int(imm, 2)


def jalr(registers, rd, rs1, imm):
    imm = convertToSigned(imm)
    registers[int(rd, 2) + 1] = registers[0] + 4
    registers[0] = registers[int(rs1, 2) + 1] + int(imm, 2)


def lh(memory, registers, rd, rs1, imm):
    imm = convertToSigned(imm)
    imm = int(imm, 2)
    address = registers[int(rs1, 2) + 1] + imm
    value = int(memory[address + 1].hexString + memory[address].hexString, 16)
    value = bin(value)[2:].zfill(16)
    sign = value[0]
    sign = sign * 16
    value = sign + value
    registers[int(rd, 2) + 1] = int(value, 2)


def slli(registers, rd, rs1, imm):
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] << int(imm, 2)


def lw(memory, registers, rd, rs1, imm):
    imm = convertToSigned(imm)
    imm = int(imm, 2)
    address = registers[int(rs1, 2) + 1] + imm
    registers[int(rd, 2) + 1] = int(memory[address + 3].hexString + memory[address + 2].hexString + memory[address + 1].hexString + memory[address].hexString, 16)


def slti(registers, rd, rs1, imm):
    imm = convertToSigned(imm)
    if (registers[int(rs1, 2) + 1] < int(imm, 2)):
        registers[int(rd, 2)] = 1
    else:
        registers[int(rd, 2)] = 0


def sltiu(registers, rd, rs1, imm):
    valueOne = convertToUnsigned(registers[int(rs1, 2) + 1])
    if (valueOne < int(imm, 2)):
        registers[int(rd, 2)] = 1
    else:
        registers[int(rd, 2)] = 0


def lbu(memory, registers, rd, rs1, imm):
    val = convertToUnsigned(registers[int(rs1, 2) + 1])
    address = val + int(imm, 2)
    value = memory[address].hexValue
    value = ("0" * 24) + bin(memory[address].hexValue)[2:]
    registers[int(rd, 2) + 1] = int(value, 2)


def xori(registers, rd, rs1, imm):
    imm = convertToSigned(imm)
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] ^ int(imm, 2)


def lhu(memory, registers, rd, rs1, imm):
    val = convertToUnsigned(registers[int(rs1, 2) + 1])
    address = val + int(imm, 2)
    value = int(memory[address + 1].hexString + memory[address].hexString, 16)
    value = bin(value)[2:]
    value = ("0" * 16) + value
    registers[int(rd, 2) + 1] = int(value, 2)


def srli(registers, rd, rs1, imm):
    imm = convertToSigned(imm)
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] >> int(imm, 2)


def srai(registers, rd, rs1, imm):
    length = len(bin(registers[int(rs1, 2) + 1])) - 2
    sign = bin(registers[int(rs1, 2) + 1])[2]
    finalInt = registers[int(rs1, 2) + 1] >> int(convertToSigned(imm), 2)
    if sign == "1":
        finalBin = bin(finalInt)[2:]
        while(len(finalBin) < length):
            finalBin = sign + finalBin
        finalInt = int(finalBin, 2)
    registers[int(rd, 2) + 1] = finalInt


def ori(registers, rd, rs1, imm):
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] | int(convertToSigned(imm), 2)


def andi(registers, rd, rs1, imm):
    imm = convertToSigned(imm)
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] & int(imm, 2)


# s format instructions
def executeSInstruction(memory, registers, rs1, rs2, imm, inst):
    instruction = inst.lower()
    
    if instruction == "sb":
        sb(memory, registers, rs1, rs2, imm)
    elif instruction == "sh":
        sh(memory, registers, rs1, rs2, imm)
    else:
        sw(memory, registers, rs1, rs2, imm)


def sb(memory, registers, rs1, rs2, imm):
    imm = convertToSigned(imm)
    imm = int(imm, 2)
    address = registers[int(rs1, 2) + 1] + imm
    value = registers[int(rs2, 2) + 1]
    value = hex(value)
    value = value[2:]
    memory[address] = byte.byte(value[-2:])


def sh(memory, registers, rs1, rs2, imm):
    imm = convertToSigned(imm)
    imm = int(imm, 2)
    address = registers[int(rs1, 2) + 1] + imm
    value = registers[int(rs2, 2) + 1]
    value = hex(value)
    value = value[2:]
    first = value[-4:-2]
    second = value[-2:]
    memory[address] = byte.byte(second)
    memory[address + 1] = byte.byte(first)


def sw(memory, registers, rs1, rs2, imm):
    imm = convertToSigned(imm)
    imm = int(imm, 2)
    address = registers[int(rs1, 2) + 1] + imm
    value = registers[int(rs2, 2) + 1]
    value = hex(value)
    value = value[2:]
    first = value[-8:-6].zfill(2)
    second = value[-6:-4].zfill(2)
    third = value[-4:-2].zfill(2)
    fourth = value[-2:].zfill(2)
    memory[address] = byte.byte(fourth)
    memory[address + 1] = byte.byte(third)
    memory[address + 2] = byte.byte(second)
    memory[address + 3] = byte.byte(first)


# b format instructions
def executeBInstruction(registers, rs1, rs2, imm, inst):
    instruction = inst.lower()

    if instruction == "beq":
        beq(registers, rs1, rs2, imm)
    elif instruction == "bne":
        bne(registers, rs1, rs2, imm)
    elif instruction == "blt":
        blt(registers, rs1, rs2, imm)
    elif instruction == "bge":
        bge(registers, rs1, rs2, imm)
    elif instruction == "bltu":
        bltu(registers, rs1, rs2, imm)
    else:
        bgeu(registers, rs1, rs2, imm)



def beq(registers, rs1, rs2, imm):
    imm = convertToSigned(imm)
    imm = imm[:-1] + '0'
    if registers[int(rs1, 2) + 1] == registers[int(rs2, 2) + 1]:
        registers[0] = registers[0] + int(imm, 2)


def bne(registers, rs1, rs2, imm):
    imm = convertToSigned(imm)
    imm = imm[:-1] + '0'
    if registers[int(rs1, 2) + 1] != registers[int(rs2, 2) + 1]:
        registers[0] = registers[0] + int(imm, 2)


def blt(registers, rs1, rs2, imm):
    imm = convertToSigned(imm)
    imm = imm[:-1] + '0'
    if registers[int(rs1, 2) + 1] < registers[int(rs2, 2) + 1]:
        registers[0] = registers[0] + int(imm, 2)


def bge(registers, rs1, rs2, imm):
    imm = convertToSigned(imm)
    imm = imm[:-1] + '0'
    if registers[int(rs1, 2) + 1] >= registers[int(rs2, 2) + 1]:
        registers[0] = registers[0] + int(imm, 2)


def bltu(registers, rs1, rs2, imm):
    valOne = convertToUnsigned(registers[int(rs1, 2) + 1])
    valTwo = convertToUnsigned(registers[int(rs2, 2) + 1])
    imm = imm[:-1] + '0'
    if valOne < valTwo:
        registers[0] = registers[0] + int(imm, 2)


def bgeu(registers, rs1, rs2, imm):
    valOne = convertToUnsigned(registers[int(rs1, 2) + 1])
    valTwo = convertToUnsigned(registers[int(rs2, 2) + 1])
    imm = imm[:-1] + '0'
    if valOne >= valTwo:
        registers[0] = registers[0] + int(imm, 2)


# r format instructions
def executeRInstruction(registers, rd, rs1, rs2, inst):
    instruction = inst.lower()

    if instruction == "add":
        add(registers, rd, rs1, rs2)
    elif instruction == "sub":
        sub(registers, rd, rs1, rs2)
    elif instruction == "sll":
        sll(registers, rd, rs1, rs2)
    elif instruction == "slt":
        slt(registers, rd, rs1, rs2)
    elif instruction == "sltu":
        sltu(registers, rd, rs1, rs2)
    elif instruction == "xor":
        xor(registers, rd, rs1, rs2)
    elif instruction == "srl":
        srl(registers, rd, rs1, rs2)
    elif instruction == "sra":
        sra(registers, rd, rs1, rs2)
    elif instruction == "or":
        OR(registers, rd, rs1, rs2)
    elif instruction == "mul":
        mul(registers, rd, rs1, rs2)
    elif instruction == "mulh":
        mulh(registers, rd, rs1, rs2)
    elif instruction == "mulhsu":
        mulhsu(registers, rd, rs1, rs2)
    elif instruction == "mulhu":
        mulhu(registers, rd, rs1, rs2)
    elif instruction == "div":
        div(registers, rd, rs1, rs2)
    elif instruction == "divu":
        divu(registers, rd, rs1, rs2)
    elif instruction == "rem":
        rem(registers, rd, rs1, rs2)
    elif instruction == "remu":
        remu(registers, rd, rs1, rs2)
    else:
        AND(registers, rd, rs1, rs2)



def add(registers, rd, rs1, rs2):
    registers[int("0b" + rd, 2) + 1] = registers[int("0b" + rs1, 2) + 1] + registers[int("0b" + rs2, 2) + 1]


def sub(registers, rd, rs1, rs2):
    registers[int("0b" + rd, 2) + 1] = registers[int("0b" + rs1, 2) + 1] - registers[int("0b" + rs2, 2) + 1]


def sll(registers, rd, rs1, rs2):
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] << registers[int(rs2, 2) + 1]


def slt(registers, rd, rs1, rs2):
    if (registers[int(rs1, 2) + 1] < registers[int(rs2, 2) + 1]):
        registers[int(rd, 2)] = 1
    else:
        registers[int(rd, 2)] = 0


def sltu(registers, rd, rs1, rs2):
    valOne = convertToUnsigned(registers[int(rs1, 2) + 1])
    valTwo = convertToUnsigned(registers[int(rs2, 2) + 1])
    if (valOne < valTwo):
        registers[int(rd, 2)] = 1
    else:
        registers[int(rd, 2)] = 0


def xor(registers, rd, rs1, rs2):
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] ^ registers[int(rs2, 2) + 1]


def srl(registers, rd, rs1, rs2):
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] >> registers[int(rs2, 2) + 1]


def sra(registers, rd, rs1, rs2):
    length = len(bin(registers[int(rs1, 2) + 1])) - 2
    sign = bin(registers[int(rs1, 2) + 1])[2]
    finalInt = registers[int(rs1, 2) + 1] >> registers[int(rs2, 2) + 1]
    if sign == "1":
        finalBin = bin(finalInt)[2:]
        while(len(finalBin) < length):
            finalBin = sign + finalBin
        finalInt = int(finalBin, 2)
    registers[int(rd, 2) + 1] = finalInt


def OR(registers, rd, rs1, rs2):
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] | registers[int(rs2, 2) + 1]


def AND(registers, rd, rs1, rs2):
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] & registers[int(rs2, 2) + 1]


def mul(registers, rd, rs1, rs2):
    regOne = registers[int(rs1, 2) + 1]
    regTwo = registers[int(rs2, 2) + 1]
    value = regOne * regTwo
    if(value >= 0):
        value = bin(value)[2:]
    else:
        value = bin(value)[3:]
        inverted_str = ''.join('1' if bit == '0' else '0' for bit in value)
        carry = 1
        result_list = []
        for bit in reversed(inverted_str):
            new_bit = (int(bit) + carry) % 2
            carry = (int(bit) + carry) // 2
            result_list.insert(0, str(new_bit))

        value = ''.join(result_list)
    registers[int(rd, 2) + 1] = int(value[-32:], 2)

def mulh(registers, rd, rs1, rs2):
    regOne = registers[int(rs1, 2) + 1]
    regTwo = registers[int(rs2, 2) + 1]
    value = regOne * regTwo
    if (value >= 0):
        value = bin(value)[2:]
    else:
        value = bin(value)[3:]
        inverted_str = ''.join('1' if bit == '0' else '0' for bit in value)
        carry = 1
        result_list = []
        for bit in reversed(inverted_str):
            new_bit = (int(bit) + carry) % 2
            carry = (int(bit) + carry) // 2
            result_list.insert(0, str(new_bit))

        value = ''.join(result_list)
    registers[int(rd, 2) + 1] = int(value[-64:-32], 2)


def mulhsu(registers, rd, rs1, rs2):
    regOne = convertToUnsigned(registers[int(rs1, 2) + 1])
    regTwo = convertToUnsigned(registers[int(rs2, 2) + 1])
    value = regOne * regTwo
    registers[int(rd, 2) + 1] = value[-64:-32]

def mulhu(registers, rd, rs1, rs2):
    regOne = convertToUnsigned(registers[int(rs1, 2) + 1])
    regTwo = convertToUnsigned(registers[int(rs2, 2) + 1])
    value = regOne * regTwo
    registers[int(rd, 2) + 1] = value[-64:-32]

def div(registers, rd, rs1, rs2):
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] / registers[int(rs2, 2) + 1]

def divu(registers, rd, rs1, rs2):
    valOne = convertToUnsigned(registers[int(rs1, 2) + 1])
    valTwo = convertToUnsigned(registers[int(rs2, 2) + 1])

    registers[int(rd, 2) + 1] = valOne / valTwo


def rem(registers, rd, rs1, rs2):
    registers[int(rd, 2) + 1] = registers[int(rs1, 2) + 1] % registers[int(rs2, 2) + 1]


def remu(registers, rd, rs1, rs2):
    valOne = convertToUnsigned(registers[int(rs1, 2) + 1])
    valTwo = convertToUnsigned(registers[int(rs2, 2) + 1])

    registers[int(rd, 2) + 1] = valOne % valTwo


# u format instructions
def executeUInstruction(registers, rd, imm, inst):
    instruction = inst.lower()

    if instruction == "auipc":
        auipc(registers, rd, imm)
    else:
        lui(registers, rd, imm)



def auipc(registers, rd, imm):
    if(len(imm) < 12):
        registers[int(rd, 2) + 1] = registers[0]
    else:
        mask = "1" * (len(imm) - 12) + "0" * 12
        registers[int(rd, 2) + 1] = registers[0] + int(imm, 2) & int(mask, 2)


def lui(registers, rd, imm):
    if(len(imm) < 12):
        registers[int(rd, 2) + 1] = 0
    else:
        mask = "1" * (len(imm) - 12) + "0" * 12
        registers[int(rd, 2) + 1] = int(imm, 2) & int(mask, 2)


# j format instructions
def executeJInstruction(registers, rd, imm, inst):
    jal(registers, rd, imm)



def jal(registers, rd, imm):
    imm = convertToSigned(imm)
    imm = imm[:-1] + '0'
    registers[int(rd, 2) + 1] = registers[0] + 4
    registers[0] = registers[0] + int(imm, 2)