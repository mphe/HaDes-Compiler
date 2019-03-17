# HaDes Compiler

A proof-of-concept HaDes Compiler written from scratch in Python.<br/>
The compiler transforms higher level code to HaDes assembly code that can then be compiled using the HaDes assembler.

## Background

From the respective university hardware design course:

> The HaDes Lab is about deeply understanding the internal concepts, structure, and operation of micro-
> controllers (MCU). By the end of this course, you will have implemented a specific MCU in a Hardware
> Description Language (HDL) and software for your MCU in Assembly (ASM). You will have extended
> both your skills for describing digital logic, implementing low level code, and debugging hardware and
> software using various tools. The exercises will be done in VHDL on a Xilinx ® Artix TM -7 FPGA, which will
> be provided on the BASYS3 development board from Digilent, as depicted in Figure 1.1.

Dialog during development of the software:

> Me: Do you think it's faster to write a compiler than writing this assembly code by hand?<br/>
> Other Guy: Probably.


## Features / Missing features
The parser accepts grammar rules in BNF-like format, as seen in `grammar.py`.<br/>
The compiler supports basic language features as seen in `test.txt`.

**Lacks**:

* global variables
* comments
* important functions like interrupts, periphery controls, etc.
* error detection
* code optimization
* ...

## Notes

Both the parser and the compiler are proof-of-concept. They work and can be extended as required.

The parser becomes very slow with complex nested expressions like `(a + b * (c - d * a) + (x + f(y)))`.
This could be fixed by preprocessing the source code to split codeblocks and statements and then invoking the parser on single statements rather than the whole code.

The compiler generates working, but not very efficient, assembler code.

## Usage

Install Python3

Then run:
```
$ ./main.py <codefile> -o <outputfile>
```


## Conclusion
It was not faster to write the compiler than writing assembler code by hand.

But it was an interesting experience.
