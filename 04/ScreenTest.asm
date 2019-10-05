


//16 mal 16 Schwarz gefolgt von 16 mal 16 Weiß 

@SCREEN
D=A
@addr
M=D
M=M-1

@color
M=-1

@16
D=A
@n
M=D
@0
D=A
@counter1
M=-1
@counter2
M=D

@511
D=A
@m
M=D


(LOOP1)

	

	@m
	D=M
	@counter1
	D=D-M
	@END
	D;JLE
	
	@counter1
	M=M+1
	@counter2
	M=0
	@addr
	M=M+1
	
	@LOOP2
	0;JMP
	
	
	
	
	(LOOP2)
		@n
		D=M
		@counter2
		D=D-M
		@CHANGE
		D;JLE
		// färben
		@color
		D=M
		@addr
		A=M
		M=D
		
		@addr
		M=M+1
		
		//++
		@counter2
		M=M+1
		@LOOP2
		0;JMP
	
(CHANGE)
	@color
	M=!M
	@LOOP1
	0;JMP
		
		
(END)
@END
0;JMP