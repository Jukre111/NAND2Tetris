// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
	
	@color //farbe auf weiss
	M=0
	
	
(OUTERLOOP)
	@SCREEN
	D=A
	@address
	M=D
	@KBD
	D=M
	@KEYPRESSED 
	D;JGT
	@color
	M=0
	@INNERLOOP
	0;JMP
	
	(INNERLOOP)
		@color
		D=M // hat die Farbe fuer 16 bits
		@address
		A=M
		M=D
		
		@address
		M=M+1
		D=M
		
		@24576
		D=D-A
		@INNERLOOP
		D;JLT

@OUTERLOOP
0;JMP		
	
(KEYPRESSED)
	@color
	M=-1
	@INNERLOOP
	0;JMP