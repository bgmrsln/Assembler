import re
import sys
#cpu230assemble just does the translations

def checkHex(s):
	for ch in s:
		if (ch<'0' or ch>'9') and (ch<'A' or ch>'F') :
			return False
	#Hexes are not allowed to start with a letter
	if s[0]>='A' and s[0]<='F':
		return False
	return True

inp= open(sys.argv[1], 'r')
progname= sys.argv[1][:sys.argv[1].index(".asm")]

o=open(progname+".bin","w")

#numbers in hex
labels={}
instructions={"HALT":1,"LOAD":2,"STORE":3,"ADD":4,"SUB":5,"INC":6,"DEC":7, "XOR":8,"AND":9,"OR":10,"NOT":11,"SHL":12,"SHR":13,"NOP":14,"PUSH":15,"POP":16,"CMP":17, "JMP":18,"JZ":19,"JE":19,"JNZ":20,"JNE":20,"JC":21,"JNC":22,"JA":23, "JAE":24, "JB":25,"JBE":26,"READ":27,"PRINT":28}
address=0
registers={"A":1,"B":2,"C":3,"D":4,"E":5,"S":6}
#it is to know line number, to know where the syntax error occurs
i=0
#traverse the input for label's adress values
for line in inp:
	#delete blank spaces before and after
	line=line.strip()
	#empty lines are skipped
	if not line:
		continue
	#label lines are the ones with a ":" symbol
	if re.search(":",line):
		#there can be space between labelName and ":"
		tokens=[x for x in re.split(":| ",line) if x]
		if tokens[0] in labels:
			sys.exit("There can't be two label with the same name")
		
		#label format check
		if len(tokens)>1:
			sys.exit(("You write something you should have not write in line",i,"\nI was expecting one token-label"))
		#labelName check
		if tokens[0][0]<= '9' and  tokens[0][0]>= '0':
			sys.exit(("Label name is wrong\nCould not produce bin file in line",i))
		labels[tokens[0]]= address

	else:
		#address is increased by 3 in each instruction
		address= address+3
	i+=1
	

i=0
inp2 =open(sys.argv[1],'r')
for line in inp2:
	line= line.strip()
	#to have case insensitive hex numbers, and also instructions, is it okay
	if line.count("'")>=2  :
		ind= line.index("'")
		line= line[:ind].upper()+ line[ind:]

	elif line.count('"')>=2 :
		ind= line.index('"')
		line= line[:ind].upper()+ line[ind:]
	else:
		line.upper()
	
	#empty lines are skipped
	if not line:
		i+=1
		continue
		
	#label lines are skipped
	if not(re.search(":",line)):
		tokens= re.split(" ",line)
		# if " or ' is a token, this means we had a blank space between " " or ' '. it is corrected here.
		if ('"' in tokens) :
			tokens.remove("\"")
			tokens.remove("\"")
			tokens.append("' '")
		if ("'" in tokens):
			tokens.remove("'")
			tokens.remove("'")
			tokens.append("' '")
		if(len(tokens)>2):
			sys.exit(("Operand should be one token in line:",i))
		opcode= instructions[tokens[0]]
		addrmode=0
		operand=0
		
		if tokens[0]=="HALT" or tokens[0]=="NOP":
			addrmode=0
		#immediate data is given as hex,turn it into decimal
		elif checkHex(tokens[1]):
			operand= int(tokens[1], 16)
		#immediate data is given as char
		elif re.search(r"'", tokens[1]) or re.search(r'"', tokens[1]):
			addrmode=0
			#turn value to ascii, and it is operand
			operand= ord(tokens[1][1:-1])	
		#memory address is given	
		#if [B] addrmode is 2,  if [xxxx] addrmode is 3
		elif re.search(']', tokens[1]) :
			#find register with dic and take its address
			soperand=tokens[1][1:-1]
			#just to be cautious
			soperand= soperand.strip()
			if soperand in registers:
				addrmode=2	
				operand= registers[soperand]
				
			elif checkHex(soperand):
				addrmode=3
				operand= int(soperand,16)
			else:
				sys.exit(("You need to give a hex number or a register name in line",i))
		#operand is in given register
		elif tokens[1] in registers:
			addrmode= 1
			operand= registers[tokens[1]]
		#operand is the address of the label
		elif tokens[1] in labels:			
			addrmode=0
			operand= labels[tokens[1]]
			
		else:
			sys.exit(("error in ",i))

		i+=1
	
		#now we have 3 parts, lets translate them into hex
		bopcode = format(opcode, '06b') 
		baddrmode = format(addrmode, '02b') 
		boperand = format(operand, '016b') 
		bin= '0b' + bopcode+ baddrmode+ boperand
		ibin= int(bin[2:],2);
		instr= format(ibin, '06x')
		o.write(instr.upper()+'\n')


o.close()
inp.close()
inp2.close()
		

