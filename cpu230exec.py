import sys

#https://stackoverflow.com/questions/510357/how-to-read-a-single-character-from-the-user
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()

class _GetchUnix:
    def __init__(self):
        import tty, sys
    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
registers={1:"a" ,2: "b",3:"c",4:"d",5:"e",6:"s",0:"pc" }
#registers are symbolically put into memory to make it more useful. Memory spaces are one byte starting from 0.
memory={"a":0,"b":0,"c":0,"d":0,"e":0,"s":65534,"pc":0}

flags={"SF":0,"ZF":0,"CF":0}
inputfile= open(sys.argv[1], 'r')
#creates an txt file with the same name as the bin file
progname= sys.argv[1][:sys.argv[1].index(".bin")]
outputfile=open(progname+".txt","w")
getch= _Getch()
#integer program counter
pc=0
#if first char is 1, sign flag is on
def setSF(num):
    if num[0]=="1":
        flags["SF"]=1
    else:
        flags["SF"]=0
#if it is all zeros, sign flag is on
def setZF(num):
    if num== 16*"0" or num== 17*"0":
        flags["ZF"]=1
    else:
        flags["ZF"]=0

#splits the binary form of a decimal value into two 8 bit-parts and turns them into decimal again
def split(value):
    ibin = format(value, '016b')
    firstHalf= int(ibin[:8],2)
    secondHalf= int(ibin[8:],2)
    return (firstHalf,secondHalf)

def mynot(num):   #not function
    ibin= format(num, '016b')
    notnum=""
    for i in ibin:
        if i=='0':
            notnum+= "1"
        else:
            notnum+= "0"
    setSF(notnum)
    setZF(notnum)   
    return int(notnum,2)

def neg(num):  #take number's not,then adds 1
    return add(mynot(num),1)  

def xor(num1, num2): #bitwise xor
    bin1= format(num1, '016b')
    bin2= format(num2, '016b')
    xornum=""
    for i in range(16):
        if bin1[i]==bin2[i]:
            xornum+="0"
        else:
            xornum+="1"
    setSF(xornum)
    setZF(xornum)
    return int(xornum,2)

def myand(num1, num2): #bitwise and
    bin1= format(num1, '016b')
    bin2= format(num2, '016b')
    andnum=""
    for i in range(16):
        if bin1[i]=="1" and bin2[i]=="1":
            andnum+="1"
        else:
            andnum+="0"
    setZF(andnum)
    setSF(andnum)
    return int(andnum,2)

def myor(num1, num2): #bitwise or
    bin1= format(num1, '016b')
    bin2= format(num2, '016b')
    ornum=""
    for i in range(16):
        if bin1[i]=="1" or bin2[i]=="1":
            ornum+="1"
        else:
            ornum+="0"
    setZF(ornum)
    setSF(ornum)
    return int(ornum,2)
    
def mynot(num):   #takes the complement of the num
    ibin= format(num, '016b')
    notnum=""
    for i in ibin:
        if i=='0':
            notnum+= "1"
        else:
            notnum+= "0"
    setSF(notnum)
    setZF(notnum)   
    return int(notnum,2)

def add(num1, num2):  # adds two decimal numbers and sets the flags
    a = str(format(num1, '016b'))
    b = str(format(num2, '016b'))
    result = ""
    carry = 0
    signa= a[0]
    signb= b[0]
    
    for x in range(16):
        if (a[-1] == '1' and b[-1] == '1' and carry == 1):  # 3
            
            result = "1" +result  # carry is still 1
        elif (a[-1] == '1' and b[-1] == '1') or ((a[-1] == '1' or b[-1] == '1') and carry == 1):  # 2
            carry = 1  # carry =1
            result =  "0"+result
            
        elif (a[-1] == '1' or b[-1] == '1') or (a[-1] == '0' and b[-1] == '0' and carry == 1):  # 1
            carry = 0
            result =  "1"+result
            
        else:
            result = "0"+result  # carry 0 olmaya devam

        a = a[:-1]
        b = b[:-1]

    if carry == 1:
        flags["CF"] = 1
    else:
        flags["CF"] = 0
    setZF(result)
    setSF(result)
    #if the numbers are negative but their sum is positive it is an overflow
    if signa==1 and signb==1 and flag["SF"]==0:
        sys.exit("Overflow") 
    #if numbers are positive but their sum is negative it is an overflow
    elif signa==0 and signb==0 and flag["SF"]==1:
        sys.exit("Overflow")
    return int(result, 2)


def imr(addrmode,operand)  :
    if addrmode==0 :                #00 operand	is	immediate data
        return operand
    elif addrmode==1 :              #01 operand is given in	the register
        return memory[registers[operand]] #if it is in a register already two bytes, no need to pair
    elif addrmode==2 :              #10 operand’s	memory address is given	in the register
       return pair(memory[ registers[operand]]) #returns to consecutive 2 bytes
    else:                           # 11 operand is	a memory address
       return pair(operand)         #2byte info

def pair(operand) :  # pairs the consecutive memory blocks. If any is empty, 0 is taken instead.
    
    if (operand in memory) and (operand+1 in memory) :
        return  int((format(memory[operand],'02x')+format(memory[operand+1],'02x')),16)
    elif (operand in memory):
        return int((format(memory[operand],'02x')+"00"),16)
    elif (operand+1 in memory):
        return int(format(memory[operand+1],'02x'),16)
    else:
        return 0
        

def mr(addrmode, operand):  #returns memory address
    if addrmode == 1:       #01 operand	is	in	given in the register
        return registers[operand]
    elif addrmode == 2:     #10 operand’s	memory	address	is	given in the register
        return memory[registers[operand]]
    elif addrmode==3:       # 11 operand is	a memory address
        return operand
    else:
        sys.exit(("operand type is not compatible in line", i))


def func(opcode,operand,addrmode) :          # if reg a is empty, throw an error????
    global pc
    global getch
    if opcode == 2:  # loads operand to reg a        
        memory["a"] = imr(addrmode, operand)

    elif opcode == 3:  # store what is in reg a to the operand, reg a is 2 byte,
        twoByte = split(memory["a"])
        # don't have to split to store at a register
        if (addrmode == 1):
            memory[mr(addrmode, operand)] = memory["a"]
        # put firstbyte to memory operand, second to operand+1
        else:
            memory[mr(addrmode, operand)] = twoByte[0]
            memory[mr(addrmode, operand) + 1] = twoByte[1]

    elif opcode == 4: #add
        memory["a"] = add(memory["a"], imr(addrmode, operand))

    elif opcode == 5: #sub
        memory["a"] = add(memory["a"], neg(imr(addrmode, operand)))

    elif opcode == 6:# increments the operand
        if addrmode == 1:  
                memory[mr(addrmode, operand)] = add(1, memory[mr(addrmode, operand)])
        else: 
            address = mr(addrmode, operand)
            twoByte = split(add(pair(address), 1))
            memory[address] = twoByte[0]
            memory[address + 1] = twoByte[1]

    elif opcode == 7: #decrements the operand       
        if addrmode == 1:
            value= add (neg(1),memory[mr(addrmode, operand)]) 
            memory[mr(addrmode, operand)] = value

        else:
            address = mr(addrmode, operand)
            value=add(pair(address), neg(1))
            twoByte = split(value)
            memory[address] = twoByte[0]
            memory[address + 1] = twoByte[1]
            
    elif opcode == 8: #xor
        memory["a"] = xor(imr(addrmode, operand), memory["a"])
    elif opcode == 9: #and    
        memory["a"] = myand(imr(addrmode, operand), memory["a"])

    elif opcode == 10: #or
        memory["a"] = myor(imr(addrmode, operand), memory["a"])

    elif opcode == 11: #not. Writes on to the operand, after takin its not
        address = mr(addrmode, operand)
        if addrmode == 1:
            memory[address] = mynot(memory[address])
        else:
            twoByte = split(mynot(pair(address)))
            memory[address] = twoByte[0]
            memory[address + 1] = twoByte[1]

    elif opcode == 12: ##shift the bits of register one position to the left
        if (memory[operand]!=None) and addrmode==1 : 
            s = format(memory[mr(addrmode,operand)], '016b')
            flags["CF"] = s[0]
            memory[mr(addrmode,operand)] = int(s[1:16] + "0", 2)
            setZF(s[1:16] + "0")
            setSF(s[1:16] + "0")
        else:
            sys.exit("it should be register name")
    elif opcode==13:   #shift the bits of register one position to the right     
    #address of the register
        if addrmode!=1:
            sys.exit("Register name is required")
        address= mr(addrmode,operand)
        value= memory[address]
        value= value//2
        valuebin= format(value,'16b')
        setZF(valuebin)
        setSF(valuebin)
        memory[address]= value

    elif opcode == 15: # push
        if addrmode!=1:
            sys.exit("Register name is required")
        twoByte = split(imr(addrmode, operand))
        memory[memory["s"]] = twoByte[0]
        memory[memory["s"]+1] = twoByte[1]
        memory["s"]-=2

    elif opcode == 16:#pop data on top of the stack , put it into the necessary register and increase S by 2.
        if addrmode!=1:
            sys.exit("Register name is required")
        memory["s"]+=2
        memory[mr(addrmode,operand)]=pair(memory["s"])
        

    elif opcode==17: #cmp, A- operand's value
        value = imr(addrmode, operand)
        add(memory["a"], neg(value)) # does sub and set flags

    elif opcode == 18: #jmp
        if addrmode !=0:
            sys.exit("Immediate data should be given")
        pc= operand
        memory["pc"]=pc

    elif opcode == 19: #jz, je
        if addrmode !=0:    # it only takes immediate data
            sys.exit("Immediate data should be given")
                
        if flags["ZF"] == 1:            
            memory["pc"] = operand
            pc = operand
            
    elif opcode == 20:        #jnz jne
        if addrmode !=0:
            sys.exit("Immediate data should be given")
                
        if flags["ZF"]==0 :
            pc = operand
            memory["pc"] = pc

    elif opcode == 21:  #jc
        if addrmode !=0:
            sys.exit("Immediate data should be given")       
        if flags["CF"] == 1:
            memory["pc"] = operand
            pc = operand
        
    elif opcode ==  22:   #jnc
        if addrmode !=0:
            sys.exit("Immediate data should be given")
        if flags["CF"] == 0:
            pc = operand
            memory["pc"] = pc
        
    elif opcode == 23: #ja
        if addrmode !=0:
            sys.exit("Immediate data should be given")
        if flags["SF"] == 0 and flags["ZF"] == 0:
            memory["pc"] = operand
            pc = operand
    
    elif opcode == 24: #jae
        if addrmode !=0:
            sys.exit("Immediate data should be given")

        if flags["SF"]==0 :
            pc = operand    #operand should be immediate
            memory["pc"] = pc

    elif opcode==25:      #jb
     # sanirim burada da immediate olmasi lazim alttaki addrmode ifini kopyalayalim Begume sor oyle yapalim yoksa ilk kodda da kontrol edebiliriz syntax kisminda
        if addrmode !=0:
            sys.exit("Immediate data should be given")
        if  flags["SF"]==1 :
            memory["pc"]=operand
            pc=operand
    elif opcode == 26:  #jbe
        if addrmode !=0:
            sys.exit("Immediate data should be given")               
        if flags["SF"] == 1  or flags["ZF"]==1:
            pc = operand  # operand should be immediate
            memory["pc"] = pc
     
    elif opcode==27:    #read one char with pressing enter
        address= mr(addrmode, operand)
        ch= getch()
        memory[address]= ord(ch)

    elif opcode == 28:   #prints the operand as a character
        prchr=  chr(imr(addrmode,operand))
        outputfile.write(prchr+"\n")


p=0
#put instructions into memory
for line in inputfile:
    line= line.strip()
    instr = format(int(line,16), '024b')   #split instruction into 3 parts that are 1-byte and
    memory[p] = int(instr[0:8],2)     #loaded them into memory as 3 consecutive memory blocks
    memory[p + 1] = int(instr[8:16],2)
    memory[p + 2] = int(instr[16:],2)
    p+=3  #stores the number of required memory blocks to load an instruction

i=0
while pc < p:  # reads each instruction from memory
    ist=str(format(memory[pc],'08b'))+str(format(memory[pc+1],'08b'))+str(format(memory[pc+2],'08b'))
    addrmode = int(ist[6:8],2)
    opcode = int(ist[0:6],2)
    operand = int(ist[8:],2)

    memory["pc"] += 3
    pc += 3
    if opcode == 1:  #HALT
        break
    elif opcode == 14: #NOP, no operation
        continue
    func(opcode, operand, addrmode)
    i+=1

