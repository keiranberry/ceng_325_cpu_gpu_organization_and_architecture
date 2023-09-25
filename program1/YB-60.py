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

    elif ":" in request:
        colonLocation = request.find(":")
        address = int(request[0:colonLocation], 16)
        values = request[colonLocation + 1:]


        editMemoryAddress(memory, address, values)

    elif "R" in request:
        address = request[0:len(request) - 1]
        runProgram(memory, address)

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
    print("   PC        OPC    INST    Rd   Rs1   Rs2       ")
    print(" ", end = "")
    print(hex(int(address, 16))[2:].zfill(5), end = "    ")
    print("00000000 xxxxxx 12345 12345 12345")

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

registers = []
memory = [byte("00") for i in range(524288)]

if len(sys.argv) > 1:
    fileName = sys.argv[1]
    openFile = open(fileName)
    readValuesAndFillMemory(openFile, memory, fileName)

monitor(memory, registers)