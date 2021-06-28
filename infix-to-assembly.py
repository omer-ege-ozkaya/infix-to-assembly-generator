#!/usr/bin/env python
# coding: utf-8

def find_first_parenthesis_block(text: str) -> (int, int):
    """
    Return the beginning and ending indexes of the first complete parenthesis block.

    Parameters
    ----------
    text : str
        infix string.

    Returns
    -------
    (int, int)
        beginning, ending.

    """
    start_of_parenthesis_block = None
    end_of_parenthesis_block = None
    count_parenthesis = 0
    for i, char in enumerate(text):
        if char == "(":
            if start_of_parenthesis_block is None:
                start_of_parenthesis_block = i
            else:
                count_parenthesis += 1
        elif char == ")":
            if count_parenthesis == 0:
                end_of_parenthesis_block = i
                break
            else:
                count_parenthesis -= 1
    return start_of_parenthesis_block, end_of_parenthesis_block

def ishex(char: chr) -> bool:
    """
    Return whether the char is a legitimate hex digit or not.

    Parameters
    ----------
    char : chr
        character to be tested.

    Returns
    -------
    bool
        true if character is a legitimate hex digit, else false.

    """
    return char.isdigit() or char in "abcdef"

def find_first_number_block(text: str) -> (int, int):
    """
    Return the beginning and ending indexes of the first complete number block.

    Parameters
    ----------
    text : str
        infix string.

    Returns
    -------
    (int, int)
        beginning, ending.
    """
    start_of_number_block = None
    end_of_number_block = None
    for i, char in enumerate(text):
        if ishex(char):
            if start_of_number_block is None:
                start_of_number_block = i
        elif start_of_number_block is not None:
            end_of_number_block = i - 1
            break
    if start_of_number_block is not None and end_of_number_block is None:
        end_of_number_block = i
    return start_of_number_block, end_of_number_block

def find_first_block(text: str) -> (int, int, str):
    """
    Return the beginning, ending indexes and type of the first complete block.
    
    Type of block is either 'number', 'parenthesis' or 'operator'.

    Parameters
    ----------
    text : str
        infix string.

    Returns
    -------
    (int, int, str)
        beginning, ending, type of block(number, parenthesis or operator).

    """
    initial = text[0]
    if ishex(initial):
        start, end = find_first_number_block(text)
        typee = "number"
    elif initial == "(":
        start, end = find_first_parenthesis_block(text)
        typee = "parenthesis"
    else:
        start, end = 0, 0
        typee = "operator"
    return start, end, typee

def text_to_parts(text: str) -> list:
    """
    Return a list of strings of mathematical blocks.
    
    Split the text into blocks of numbers, parenthesis blocks and operators
    and return them in a list.

    Parameters
    ----------
    text : str
        infix string.

    Returns
    -------
    list
        list of strings of mathematical blocks.

    """
    parts = []
    first_block_start, first_block_end, typee = find_first_block(text)
    parts.append(text[first_block_start : first_block_end + 1])
    if len(text) == first_block_end + 1:
        return [text]
    parts.append(text[first_block_end + 1])
    parts += text_to_parts(text[first_block_end + 2 : ])
    return parts

def group_operations(text: str) -> list:
    """
    Return a list of strings of mathematical blocks, considering order of operations.
    
    Split the text into blocks of numbers, parenthesis blocks and operators
    and return them in a list, while considering the order of operations for strings 
    with multiple operators in the same block.

    Parameters
    ----------
    text : str
        infix string.

    Returns
    -------
    list
        list of strings of mathematical blocks.

    """
    
    parts = text_to_parts(text)
    
    def modify_list_group_by(operators):
        i = 0
        len_parts = len(parts)
        while i < len_parts:
            part = parts[i]
            if part[0] in operators:
                part0 = parts.pop(i-1)
                operation = parts.pop(i-1)
                part1 = parts.pop(i-1)
                parts.insert(i-1, "(" + part0 + operation + part1 + ")")
                i -= 1
                len_parts -= 2
            i += 1
        
    for i, part in enumerate(parts):
        if part[0] == "(":
            parts[i] = "".join(group_operations(part[1:-1]))
    
    modify_list_group_by("*/")
    modify_list_group_by("+-")
    
    return parts

def infix_to_postfix(text: str) -> list:
    """
    Return a list of postfix instructions from an infix string.

    Parameters
    ----------
    text : str
        infix string.

    Returns
    -------
    list
        list of strings of postfix instructions.

    """
    
    def unfold_block(text: str) -> list:
        return infix_to_postfix(text) if text[0] == "(" else [text]
    
    grouped = group_operations(text)[0][1:-1]
    first_block, operator, second_block = text_to_parts(grouped)
    first_block = unfold_block(first_block)
    second_block = unfold_block(second_block)
    stack = [*first_block, *second_block, operator]
    return stack

def infix_to_assembly(formula: str) -> str:
    """
    Return an assembly code block which calculates the result of the infix string.

    Parameters
    ----------
    formula : str
        infix string.

    Returns
    -------
    str
        assembly code.

    """
    asm = ""
    postfix = infix_to_postfix(formula)
    for value in postfix:
        if value == "+":
            asm += "\npop bx"
            asm += "\npop ax"
            asm += "\nadd ax, bx"
            asm += "\npush ax"
        elif value == "-":
            asm += "\npop bx"
            asm += "\npop ax"
            asm += "\nsub ax, bx"
            asm += "\npush ax"
        elif value == "*":
            asm += "\npop bx"
            asm += "\npop ax"
            asm += "\nmul bx"
            asm += "\npush ax"
        elif value == "/":
            asm += "\nmov dx, 0h"
            asm += "\npop bx"
            asm += "\npop ax"
            asm += "\ndiv bx"
            asm += "\npush ax"
        else:
            asm += "\npush 0" + value + "h"
    return asm

def create_complete_assembly_code(formula: str) -> str:
    """
    Return an assembly code block which calculates and prints the result of an infix string.

    Parameters
    ----------
    formula : str
        infix string.

    Returns
    -------
    str
        assembly code.

    """
    asm = "org 100h\n"
    asm += infix_to_assembly(formula)
    asm += """\n
pop bx ; number to write to stdout
mov ch, 02h ; counter for bytes to to print

print_routine:
    cmp ch, 0h
    je end_print_routine ; while bytes to print > 0
    
    cmp ch, 01h ; check if first or second byte, 02h is the first byte to print
    je get_second_byte
    get_first_byte:
        mov ah, 0h
        mov al, bh
        dec ch
        jmp print_byte
    get_second_byte:
        mov ah, 0h
        mov al, bl
        dec ch
    
    print_byte: ; do not alter registers bx, ch in here. ax carries the byte to print
        ; as a single byte will cover 2 digits from 0x00 to 0xff on the screen we will loop twice
        ;  and use integer division to get the most and least significant bits
        mov dl, 010h
        div dl
        ; xor swap (remainder, division) -> (division, remainder)
        xor ah, al
        xor al, ah
        xor ah, al
        
        mov cl, 02h ; loop counter for the higher and lower 4 bits of register a
        loop:
            cmp cl, 01h ; 02h -> print ah, 01h -> print al
            je print_al
            print_ah:
                mov dl, ah
                jmp print_digit
            print_al:
                mov dl, al
            
            print_digit:
                cmp dl, 0ah ; to convert byte into human-readable character
                jge number_to_ascii_lowercase_letter
                number_to_ascii_number:
                    add dl, 30h
                    jmp to_stdout
                number_to_ascii_lowercase_letter:
                    add dl, 87

                to_stdout:
                    mov ah, 02h ; int 21h/02h for writing character to standard output
                    mov dh, al
                    int 21h ; the 2 lines before and after is to keep al's value as interrupt alters it
                    mov al, dh
                    dec cl
                    jnz loop
                    jmp print_routine
        
end_print_routine:
    int 20h
"""
    return asm

import re

def check_formula_and_create_assembly_code(formula: str) -> str:
    """
    Return an assembly code block which calculates and prints the result of an infix string.
    
    If the formula is not legitimate, print warning.

    Parameters
    ----------
    formula : str
        DESCRIPTION.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    str
        DESCRIPTION.

    """
    formula = re.sub(r"(?is)[^0-9a-f+*/\-()]", "", formula)
    # print (formula)
    try:
        asm = create_complete_assembly_code(formula)
    except Exception as e:
        # print(e)
        asm = "Please check your formula for errors!"
        raise Exception(asm)
    return asm

import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
        
def print_help():
    """
    Print help.

    Returns
    -------
    None.

    """
    print(bcolors.OKBLUE, "    ", "="*80, bcolors.ENDC, sep="")
    print("""    HELP
    
    No arg: Enter formula and get assembly printed on the screen
    1 arg : Enter file and get file.asm (excluding the keyword "help")
    >2 arg: This screen shows up
""")
    print(bcolors.OKBLUE, "    ", "="*80, bcolors.ENDC, sep="", end="\n\n")

def cli():
    """
    Print the assembly code of the infix formula to the terminal.

    Returns
    -------
    None.

    """
    print_help()
    while True:
        formula = input('Please enter formula (or type "exit"):\n')
        if formula == "exit":
            return
        elif formula == "help":
            print_help()
            break
        try:
            print(";" + "="*80)
            print(check_formula_and_create_assembly_code(formula))
            print(";" + "="*80)
        except Exception as e:
            print(bcolors.FAIL, e, bcolors.ENDC)

import os

def handle_file(path: str):
    """
    Save the assembly code of the infix "file" to "file.asm".

    Parameters
    ----------
    path : str
        infix .

    Returns
    -------
    None.

    """
    try:
        with open(path) as f:
            formula = f.read()
        asm = check_formula_and_create_assembly_code(formula)
        path = path + ".asm"
        with open(path, mode="w") as f:
            f.write(asm)
            fullpath = os.path.realpath(f.name)
        filename = os.path.basename(fullpath)
        print(bcolors.OKGREEN, "The assembly file \"" + filename + "\" has been created.", bcolors.ENDC,
              sep="")
        print(bcolors.HEADER, "Path:\n", bcolors.ENDC, path, 
              sep="")
        print(bcolors.HEADER, "Absolute Path:\n", bcolors.ENDC, fullpath, 
              sep="")
        print(bcolors.HEADER, "Formula:\n", bcolors.ENDC, '"', formula, '"', 
              sep="")
    except (FileNotFoundError) as e:
        print(bcolors.FAIL, e, bcolors.ENDC)
        print_help()
    except Exception as e:
        print(bcolors.FAIL, e, bcolors.ENDC)
    finally:
        return

arg_length = len(sys.argv) - 1
if arg_length == 0:
    cli()
elif arg_length == 1:
    handle_file(sys.argv[1])
else:
    print_help()

sys.exit()
