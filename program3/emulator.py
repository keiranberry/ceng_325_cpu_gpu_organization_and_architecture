from ctypes import sizeof
import sys
import instructions
import byte

def readValuesAndFillMemory(file, memory, fileName):
    offset = 0
    for currentLine in file.read().splitlines():
        colonLocation = currentLine.find(':')
        currentLine = currentLine[colonLocation:]
        byteCount = currentLine[1:3]
        checkSum = currentLine[-2:]
        register = int(currentLine[3:7], 16) + offset
        recordType = currentLine[7:9]
        data = currentLine[9:9 + (int(byteCount, 16) * 2)]
        dataBytes= []
        byteSum = int(byteCount, 16) + int(currentLine[3:5], 16) + int(currentLine[5:7], 16) + int(recordType, 16) + int(checkSum, 16)

        if recordType == "00":
            for i in range(0, len(data), 2):
                dataBytes.append(byte.byte(data[i:i + 2]))
                byteSum += int(data[i:i + 2], 16)

            byteSum = hex(byteSum)

            if byteSum[-2:] != "00":
                print(f"Format error input file: {fileName}")
                sys.exit()

            for i in range(0, len(dataBytes)):
                memory[register + i] = dataBytes[i]
        
        if recordType == "01":
            byteSum = hex(byteSum)
            if byteSum[-2:] != "00":
                print(f"Format error input file: {fileName}")
                sys.exit()
            return

        if recordType == "02":
            byteSum += int(currentLine[9:11], 16)
            byteSum += int(currentLine[11:13], 16)
            byteSum = hex(byteSum)
            if byteSum[-2:] != "00":
                print(f"Format error input file: {fileName}")
                sys.exit()
            
            offset = 16 * int(currentLine[9:13], 16)

def monitor(memory, registers):
    print(">", end=" ")
    request = input()

    if request == "exit":
        print(">>>")
        sys.exit()

    elif request == "info":
        displayInfo(registers)

    elif ":" in request:
        colonLocation = request.find(":")
        address = int(request[0:colonLocation], 16)
        values = request[colonLocation + 1:]


        editMemoryAddress(memory, address, values)

    elif "R" in request or "r" in request:
        address = request[0:len(request) - 1]
        runProgram(memory, address, registers, False)

    elif "S" in request or "s" in request:
        address = request[0:len(request) - 1]
        runProgram(memory, address, registers, True)

    elif "T" in request or "t" in request:
        address = request[0:len(request) - 1]
        disassemble(memory, address)

    elif "." in request:
        periodLocation = request.find(".")
        start = request[0:periodLocation]
        end = request[periodLocation + 1:]
        displayRangeOfMemoryAddresses(memory, int(start, 16), int(end, 16))

    else:
        if int(request, 16) < len(memory):
            address = int(request, 16)
            displayMemoryAddress(memory, address)
        
        else: 
            print("Memory address requested is out of range")
    
    monitor(memory, registers)

def runProgram(memory, address, registers, step):
    instructionArray = []
    opc = ""

    print("   PC        OPC    INST    Rd     Rs1   Rs2/imm   ")

    tempAddress = int(address, 16)
    for i in range(4):
        instructionArray.append(memory[tempAddress])
        tempAddress += 1
    instructionArray.reverse()
    registers[0] = int(address, 16)
    for i in range(4):
        opc += instructionArray[i].hexString

    while(opc != "00100073"):
        instruction = int(opc, 16)
        instruction = bin(instruction)
        instruction = instruction[2:].zfill(32)
        groupId = instruction[25:30]
        currentPC = registers[0]

        print(hex(registers[0])[2:].zfill(5), end = " ")
        
        if(groupId == "00000" or groupId == "00100" or groupId == "11001"):
            inst, rd, rs1, imm = I_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rd.rjust(6), "", rs1.rjust(6), imm)
            instructions.executeIInstruction(memory, registers, rd, rs1, imm, inst)
            if(step):
                print(">", end = "")
                userInput = input()
                if(userInput == "info"):
                    displayInfo(registers)
        
        elif(groupId == "01000"):
            inst, rs1, rs2, imm = S_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rs1.rjust(14), rs2 + " " + imm)
            instructions.executeSInstruction(memory, registers, rs1, rs2, imm, inst)
            if(step):
                print(">", end = "")
                userInput = input()
                if (userInput == "info"):
                    displayInfo(registers)

        elif(groupId == "11000"):
            inst, rs1, rs2, imm = B_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rs1.rjust(14), rs2 + " " + imm)
            instructions.executeBInstruction(registers, rs1, rs2, imm, inst)
            if(step):
                print(">", end = "")
                userInput = input()
                if (userInput == "info"):
                    displayInfo(registers)
        
        elif(groupId == "01100"):
            inst, rd, rs1, rs2 = R_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rd.rjust(6), "", rs1.rjust(6), rs2)
            instructions.executeRInstruction(registers, rd, rs1, rs2, inst)
            if(step):
                print(">", end = "")
                userInput = input()
                if (userInput == "info"):
                    displayInfo(registers)
        
        elif(groupId == "00101" or groupId == "01101"):
            inst, rd, imm = U_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rd.rjust(6), "       ", imm)
            instructions.executeUInstruction(registers, rd, imm, inst)
            if(step):
                print(">", end = "")
                userInput = input()
                if (userInput == "info"):
                    displayInfo(registers)
        
        elif(groupId == "11011"):
            inst, rd, imm = J_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rd.rjust(6), "       ", imm)
            instructions.executeJInstruction(registers, rd, imm, inst)
            if(step):
                print(">", end = "")
                userInput = input()
                if (userInput == "info"):
                    displayInfo(registers)
        
        else:
            print("Invalid instruction or starting register")
            return
        if currentPC == registers[0]:
            registers[0] += 4
        instructionArray = []
        opc = ""
        tempAddress = registers[0]
        for i in range(4):
            instructionArray.append(memory[tempAddress])
            tempAddress += 1
        instructionArray.reverse()
        for i in range(4):
            opc += instructionArray[i].hexString
        registers[1] = 0

    print(hex(registers[0]), "   ", opc, "   EBREAK")

    

def editMemoryAddress(memory, address, values):
    newValues = values.split()
    j = 0

    for i in range(address, address + len(newValues)):
        memory[i] = byte.byte(newValues[j])
        j = j + 1
    
def displayMemoryAddress(memory, address):
    print(" ", end = "")
    print(hex(address)[2:], end = "   ")
    print(memory[address].hexString)

def displayRangeOfMemoryAddresses(memory, start, end):
    registersToDisplay = end - start + 1
    if registersToDisplay % 8 != 0:
        registersToDisplay += 8 - (registersToDisplay % 8)

    for i in range(0, registersToDisplay):
        if i % 8 == 0:
            if i != 0:
                print()
            print(hex(start + i)[2:].zfill(5), end = "   ")
        print(memory[start + i].hexString, end = " ")
    
    print()

def disassemble(memory, address):
    instructionArray = []
    opc = ""

    tempAddress = int(address, 16)
    for i in range(4):
        instructionArray.append(memory[tempAddress])
        tempAddress += 1
    instructionArray.reverse()
    intAddress = int(address, 16)
    for i in range(4):
        opc += instructionArray[i].hexString

    while(opc != "00100073"):
        instruction = int(opc, 16)
        instruction = bin(instruction)
        instruction = instruction[2:].zfill(32)
        groupId = instruction[25:30]
        
        if(groupId == "00000" or groupId == "00100" or groupId == "11001"):
            inst, rd, rs1, imm = I_format(instruction)
            rd = int("0b" + rd, 2)
            rs1 = int("0b" + rs1, 2)
            immInt = int("0b" + imm, 2)
            if (immInt & (1 << (len(imm) - 1))) != 0:
                immInt = immInt - (1 << len(imm)) 
            if(inst == "ADDI" or inst == "SLLI"):
                print(inst.lower().rjust(7), (formatRegisterForOutput(rd) + ",").rjust(4), (formatRegisterForOutput(rs1) + ",").rjust(4), "", immInt)
            else:
                print(inst.lower().rjust(7),  (formatRegisterForOutput(rd) + ", ").rjust(5), " " + str(immInt) + "(" + formatRegisterForOutput(rs1) + ")")
        
        elif(groupId == "01000"):
            inst, rs1, rs2, imm = S_format(instruction)
            rs1 = int("0b" + rs1, 2)
            rs2 = int("0b" + rs2, 2)
            immInt = int("0b" + imm, 2)
            if (immInt & (1 << (len(imm) - 1))) != 0:
                immInt = immInt - (1 << len(imm)) 
            print(inst.lower().rjust(7), (formatRegisterForOutput(rs2) + ", ").rjust(5), " " + str(immInt) + "(" + formatRegisterForOutput(rs1) + ")")

        elif(groupId == "11000"):
            inst, rs1, rs2, imm = B_format(instruction)
            rs1 = int("0b" + rs1, 2)
            rs2 = int("0b" + rs2, 2)
            immInt = int("0b" + imm, 2)
            if (immInt & (1 << (len(imm) - 1))) != 0:
                immInt = immInt - (1 << len(imm)) 
            print(inst.lower().rjust(7), (formatRegisterForOutput(rs1) + ", ").rjust(5), (formatRegisterForOutput(rs2) + ", ").rjust(4), str(immInt))
        
        elif(groupId == "01100"):
            inst, rd, rs1, rs2 = R_format(instruction)
            rd = int("0b" + rd, 2)
            rs1 = int("0b" + rs1, 2)
            rs2 = int("0b" + rs2, 2)
            print(inst.lower().rjust(7), (formatRegisterForOutput(rd) + ",").rjust(4), (formatRegisterForOutput(rs1) + ",").rjust(4), formatRegisterForOutput(rs2).rjust(3))
        
        elif(groupId == "00101" or groupId == "01101"):
            inst, rd, imm = U_format(instruction)
            rd = int("0b" + rd, 2)
            immInt = int("0b" + imm, 2)
            if (immInt & (1 << (len(imm) - 1))) != 0:
                immInt = immInt - (1 << len(imm)) 
            print(inst.lower().rjust(7), (formatRegisterForOutput(rd) + ", ").rjust(5), "", str(immInt))
        
        elif(groupId == "11011"):
            inst, rd, imm = J_format(instruction)
            rd = int("0b" + rd, 2)
            immInt = int("0b" + imm, 2)
            if (immInt & (1 << (len(imm) - 1))) != 0:
                immInt = immInt - (1 << len(imm)) 
            print(inst.lower().rjust(7), (formatRegisterForOutput(rd) + ", ").rjust(5), "", str(immInt))
        
        else:
            print("Invalid instruction or starting register")
            return
        
        intAddress += 4
        instructionArray = []
        opc = ""
        tempAddress = intAddress
        for i in range(4):
            instructionArray.append(memory[tempAddress])
            tempAddress += 1
        instructionArray.reverse()
        for i in range(4):
            opc += instructionArray[i].hexString
    
    print("ebreak")

def I_format(opc):
    rd = opc[20:25]
    rs1 = opc[12:17]
    funct3 = opc[17:20]
    groupId = opc[25:30]
    imm = opc[0:12]
    if(funct3 == "000"):
        if(groupId =="00000"):
            inst = "LB"
        elif(groupId == "00100"):
            inst = "ADDI"
        elif(groupId == "11001"):
            inst = "JALR"
    elif(funct3 == "001"):
        if(groupId == "00000"):
            inst = "LH"
        elif(groupId == "00100"):
            inst = "SLLI"
    elif(funct3 == "010"):
        if(groupId == "00000"):
            inst = "LW"
        elif(groupId == "00100"):
            inst = "SLTI"
    elif(funct3 == "011"):
        if(groupId == "00100"):
            inst = "SLTIU"
    elif(funct3 == "100"):
        if(groupId == "00000"):
            inst = "LBU"
        elif(groupId == "00100"):
            inst = "XORI"
    elif(funct3 == "101"):
        if(groupId == "00000"):
            inst = "LHU"
        elif(groupId == "00100"):
            if(imm[0:7] == "0000000"):
                inst = "SRLI"
            else:
                inst = "SRAI"
    elif(funct3 == "110"):
        if(groupId == "00100"):
            inst = "ORI"
    elif(funct3 == "111"):
        if(groupId == "00100"):
            inst = "ANDI"

    return inst, rd, rs1, imm

def S_format(opc):
    funct3 = opc[17:20]
    rs1 = opc[12:17]
    rs2 = opc[7:12]
    imm = opc[0:7] + opc[20:25]

    if(funct3 == "000"):
        inst = "SB"
    elif(funct3 == "001"):
        inst = "SH"
    elif(funct3 == "010"):
        inst = "SW"
    
    return inst, rs1, rs2, imm

def B_format(opc):
    rs1 = opc[12:17]
    rs2 = opc[7:12]
    imm = opc[0] + opc[24] + opc[1:7] + opc[20:24] + "0"
    funct3 = opc[17:20]

    if(funct3 == "000"):
        inst = "BEQ"
    elif(funct3 == "001"):
        inst = "BNE"
    elif(funct3 == "100"):
        inst = "BLT"
    elif(funct3 == "101"):
        inst = "BGE"
    elif(funct3 == "110"):
        inst = "BLTU"
    else:
        inst = "BGEU"
    return inst, rs1, rs2, imm

def R_format(opc):
    rd = opc[20:25]
    rs1 = opc[12:17]
    rs2 = opc[7:12]
    funct3 = opc[17:20]
    funct7 = opc[0:7]
    inst = ""
    if(funct7 == "0000001"):
        if(funct3 == "000"):
            inst = "MUL"
        elif(funct3 == "001"):
            inst = "MULH"
        elif(funct3 == "010"):
            inst = "MULHSU"
        elif(funct3 == "011"):
            inst = "MULHU"
        elif(funct3 == "100"):
            inst = "DIV"
        elif(funct3 == "101"):
            inst = "DIVU"
        elif(funct3 == "110"):
            inst = "REM"
        elif(funct3 == "111"):
            inst = "REMU"
    elif(funct3 == "000"):
        if(funct7 == "0000000"):
            inst = "ADD"
        else:
            inst = "SUB"
    elif(funct3 == "001"):
        inst = "SLL"
    elif(funct3 == "010"):
        inst = "SLT"
    elif(funct3 == "011"):
        inst = "SLTU"
    elif(funct3 == "100"):
        inst = "XOR"
    elif(funct3 == "101"):
        if(funct7 == "0000000"):
            inst = "SRL"
        else:
            inst = "SRA"
    elif(funct3 == "110"):
        inst = "OR"
    else:
        inst = "AND"

    return inst, rd, rs1, rs2

def U_format(opc):
    imm = opc[0:20]
    rd = opc[20:25]
    opCode = opc[25:]

    if(opCode == "0010111"):
        inst = "AUIPC"
    else:
        inst = "LUI"

    return inst, rd, imm

def J_format(opc):
    imm = opc[0] + opc[12:20] + opc[11] + opc[1:11] + "0"
    inst = "JAL"
    rd = opc[20:25]
    return inst, rd, imm


def formatForOutput(value):
    if value < 0:
        value = bin(value)[3:].zfill(32)
        inverted_str = ''.join('1' if bit == '0' else '0' for bit in value)
        carry = 1
        result_list = []
        for bit in reversed(inverted_str):
            new_bit = (int(bit) + carry) % 2
            carry = (int(bit) + carry) // 2
            result_list.insert(0, str(new_bit))

        value = ''.join(result_list)
        value = int(value, 2)
    return hex(value)[2:].zfill(8).upper()

def formatRegisterForOutput(register):
    if register == 0:
        return "zero"
    elif register == 1:
        return "ra"
    elif register == 2:
        return "sp"
    elif register == 3:
        return "gb"
    elif register == 4:
        return "tp"
    elif register == 5:
        return "t0"
    elif register == 6:
        return "t1"
    elif register == 7:
        return "t2"
    elif register == 8:
        return "s0"
    elif register == 9:
        return "s1"
    elif register == 10:
        return "a0"
    elif register == 11:
        return "a1"
    elif register == 12:
        return "a2"
    elif register == 13:
        return "a3"
    elif register == 14:
        return "a4"
    elif register == 15:
        return "a5"
    elif register == 16:
        return "a6"
    elif register == 17:
        return "a7"
    elif register == 18:
        return "s2"
    elif register == 19:
        return "s3"
    elif register == 20:
        return "s4"
    elif register == 21:
        return "s5"
    elif register == 22:
        return "s6"
    elif register == 23:
        return "s7"
    elif register == 24:
        return "s8"
    elif register == 25:
        return "s9"
    elif register == 26:
        return "s10"
    elif register == 27:
        return "s11"
    elif register == 28:
        return "t3"
    elif register == 29:
        return "t4"
    elif register == 30:
        return "t5"
    else:
        return "t6"

def displayInfo(registers):
    print("zero", formatForOutput(registers[1]))
    print("ra".rjust(4), formatForOutput(registers[2]))
    print("sp".rjust(4), formatForOutput(registers[3]))
    print("gb".rjust(4), formatForOutput(registers[4]))
    print("tp".rjust(4), formatForOutput(registers[5]))
    print("t0".rjust(4), formatForOutput(registers[6]))
    print("t1".rjust(4), formatForOutput(registers[7]))
    print("t2".rjust(4), formatForOutput(registers[8]))
    print("s0".rjust(4), formatForOutput(registers[9]))
    print("s1".rjust(4), formatForOutput(registers[10]))
    print("a0".rjust(4), formatForOutput(registers[11]))
    print("a1".rjust(4), formatForOutput(registers[12]))
    print("a2".rjust(4), formatForOutput(registers[13]))
    print("a3".rjust(4), formatForOutput(registers[14]))
    print("a4".rjust(4), formatForOutput(registers[15]))
    print("a5".rjust(4), formatForOutput(registers[16]))
    print("a6".rjust(4), formatForOutput(registers[17]))
    print("a7".rjust(4), formatForOutput(registers[18]))
    print("s2".rjust(4), formatForOutput(registers[19]))
    print("s3".rjust(4), formatForOutput(registers[20]))
    print("s4".rjust(4), formatForOutput(registers[21]))
    print("s5".rjust(4), formatForOutput(registers[22]))
    print("s6".rjust(4), formatForOutput(registers[23]))
    print("s7".rjust(4), formatForOutput(registers[24]))
    print("s8".rjust(4), formatForOutput(registers[25]))
    print("s9".rjust(4), formatForOutput(registers[26]))
    print("s10".rjust(4), formatForOutput(registers[27]))
    print("s11".rjust(4), formatForOutput(registers[28]))
    print("t3".rjust(4), formatForOutput(registers[29]))
    print("t4".rjust(4), formatForOutput(registers[30]))
    print("t5".rjust(4), formatForOutput(registers[31]))
    print("t6".rjust(4), formatForOutput(registers[32]))


registers = [0 for i in range(33)]
registers[3] = 1048575
memory = [byte.byte("00") for i in range(1048576)]

if len(sys.argv) > 1:
    fileName = sys.argv[1]
    openFile = open(fileName)
    readValuesAndFillMemory(openFile, memory, fileName)

monitor(memory, registers)