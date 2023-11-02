from ctypes import sizeof
import sys

class byte:
        def __init__(self, value):
            self.hexString = value
            self.hexValue = int(self.hexString, 16)

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
                dataBytes.append(byte(data[i:i + 2]))
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
        for i in range(32):
            print(("x" + str(i)).rjust(3), "00000000")

    elif ":" in request:
        colonLocation = request.find(":")
        address = int(request[0:colonLocation], 16)
        values = request[colonLocation + 1:]


        editMemoryAddress(memory, address, values)

    elif "R" in request or "r" in request:
        address = request[0:len(request) - 1]
        runProgram(memory, address)

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

def runProgram(memory, address):
    instructionArray = []
    opc = ""

    print("   PC        OPC    INST    Rd     Rs1   Rs2/imm   ")

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

        print(hex(intAddress)[2:].zfill(5), end = " ")
        
        if(groupId == "00000" or groupId == "00100" or groupId == "11001"):
            inst, rd, rs1, imm = I_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rd.rjust(6), "", rs1.rjust(6), imm)
        
        elif(groupId == "01000"):
            inst, rs1, rs2, imm = S_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rs1.rjust(14), rs2 + " " + imm)

        elif(groupId == "11000"):
            inst, rs1, rs2, imm = B_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rs1.rjust(14), rs2 + " " + imm)
        
        elif(groupId == "01100"):
            inst, rd, rs1, rs2 = R_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rd.rjust(6), "", rs1.rjust(6), rs2)
        
        elif(groupId == "00101" or groupId == "01101"):
            inst, rd, imm = U_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rd.rjust(6), "       ", imm)
        
        elif(groupId == "11011"):
            inst, rd, imm = J_format(instruction)
            print(opc.rjust(12), inst.rjust(6), rd.rjust(6), "       ", imm)
        
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
    
    print(hex(intAddress), "   ", opc, "   EBREAK")

    

def editMemoryAddress(memory, address, values):
    newValues = values.split()
    j = 0

    for i in range(address, address + len(newValues)):
        memory[i] = byte(newValues[j])
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
                print(inst.lower().rjust(7), ("x" + str(rd) + ",").rjust(4), ("x" + str(rs1) + ",").rjust(4), "", immInt)
            else:
                print(inst.lower().rjust(7),  ("x" + str(rd) + ", ").rjust(5), " " + str(immInt) + "(x" + str(rs1) + ")")
        
        elif(groupId == "01000"):
            inst, rs1, rs2, imm = S_format(instruction)
            rs1 = int("0b" + rs1, 2)
            rs2 = int("0b" + rs2, 2)
            immInt = int("0b" + imm, 2)
            if (immInt & (1 << (len(imm) - 1))) != 0:
                immInt = immInt - (1 << len(imm)) 
            print(inst.lower().rjust(7), ("x" + str(rs2) + ", ").rjust(5), " " + str(immInt) + "(x" + str(rs1) + ")")

        elif(groupId == "11000"):
            inst, rs1, rs2, imm = B_format(instruction)
            rs1 = int("0b" + rs1, 2)
            rs2 = int("0b" + rs2, 2)
            immInt = int("0b" + imm, 2)
            if (immInt & (1 << (len(imm) - 1))) != 0:
                immInt = immInt - (1 << len(imm)) 
            print(inst.lower().rjust(7), ("x" + str(rs1) + ", ").rjust(5), ("x" + str(rs2) + ", ").rjust(4), str(immInt))
        
        elif(groupId == "01100"):
            inst, rd, rs1, rs2 = R_format(instruction)
            rd = int("0b" + rd, 2)
            rs1 = int("0b" + rs1, 2)
            rs2 = int("0b" + rs2, 2)
            print(inst.lower().rjust(7), ("x" + str(rd) + ",").rjust(4), ("x" + str(rs1) + ",").rjust(4), ("x" + str(rs2)).rjust(3))
        
        elif(groupId == "00101" or groupId == "01101"):
            inst, rd, imm = U_format(instruction)
            rd = int("0b" + rd, 2)
            immInt = int("0b" + imm, 2)
            if (immInt & (1 << (len(imm) - 1))) != 0:
                immInt = immInt - (1 << len(imm)) 
            print(inst.lower().rjust(7), ("x" + str(rd) + ", ").rjust(5), "", str(immInt))
        
        elif(groupId == "11011"):
            inst, rd, imm = J_format(instruction)
            rd = int("0b" + rd, 2)
            immInt = int("0b" + imm, 2)
            if (immInt & (1 << (len(imm) - 1))) != 0:
                immInt = immInt - (1 << len(imm)) 
            print(inst.lower().rjust(7), ("x" + str(rd) + ", ").rjust(5), "", str(immInt))
        
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
            if(imm[0:8] == "0000000"):
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

    if(funct3 == "000"):
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


registers = [0 for i in range(33)]
memory = [byte("00") for i in range(1048576)]

if len(sys.argv) > 1:
    fileName = sys.argv[1]
    openFile = open(fileName)
    readValuesAndFillMemory(openFile, memory, fileName)

monitor(memory, registers)