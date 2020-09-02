import random
from enum import Enum, auto

from syparser.ast import AST
from syparser.ast_node_type import AstNodeType
from syparser.ast_node import AstNode
from syparser.variable import Variable

from .asmconstants import *


class CodeGenPlace(Enum):
    """
    Перечисление для того места, куда мы записываем данные
    """
    DATA = auto(),  # сегмент данных
    BEFORE_MAIN = auto(),  # до метки __start:
    MAIN = auto()  # main


class CodeGenPlaceString:
    value: str

    def __init__(self):
        self.value = ''

    def append(self, string: str):
        self.value += string


class CodeGen:
    ast: AST

    filename: str

    # asm places
    data: CodeGenPlaceString
    before_main: CodeGenPlaceString
    main: CodeGenPlaceString
    current_place_for_writing: CodeGenPlaceString

    byte_on_stack: int

    def __init__(self, filename: str, ast: AST):
        self.ast = ast
        self.filename = filename

        self.data: CodeGenPlaceString = CodeGenPlaceString()
        self.before_main: CodeGenPlaceString = CodeGenPlaceString()
        self.main: CodeGenPlaceString = CodeGenPlaceString()

        self.current_place_for_writing = self.main
        self.byte_on_stack = 8

        self.file = open(filename, 'w')

        self.ast.print()
        self.count_compare = 0

    def generate(self):  # генерируем
        self.init_variables()  # переменные
        self.init_operands_for_division()  # операнды для деления

        self.init_print_function()  # printf -  оператор

        self.block_to_asm()

        self.write(asm_header)  # .586
        self.write(start_data)
        self.write(self.data.value)
        self.write(end_data)
        self.write(text_start)
        self.write(self.before_main.value)
        self.write(label_start)
        self.write(proc_prolog + str(len(self.ast.variables.table) * 4 + 8) + ", 0")
        self.write(self.main.value)
        self.write(proc_epilogue)
        self.write(function_return)
        self.write(text_end)
        self.write(label_end)

        self.file.close()

    def init_print_function(self):
        self.set_place_for_writing(CodeGenPlace.DATA)
        self.raw(tab + "print_format db \"%d \", 0\n")
        self.set_place_for_writing(CodeGenPlace.BEFORE_MAIN)

        self.raw("print PROC\n   enter 0, 0\n")

        self.mov(eax, "[ebp + 8]")
        self.raw(tab + "invoke crt_printf, offset print_format, eax\n")

        self.raw("   leave \n   ret 4\nprint ENDP")

        self.set_place_for_writing(CodeGenPlace.MAIN)

    def init_variables(self):
        for variable in self.ast.variables.table:
            self.stack_variable(variable)

    def init_operands_for_division(self):
        self.set_place_for_writing(CodeGenPlace.DATA)
        self.raw(tab + "div_op_1 dd 0\n")
        self.raw(tab + "div_op_2 dd 0\n")
        self.set_place_for_writing(CodeGenPlace.MAIN)

    def block_to_asm(self):
        self.block_to_asm_recursive(self.ast.tree)

    def block_to_asm_recursive(self, current_node: AstNode):
        """
        Тут мы обрабатываем разные блоки нашего языка - if, for, описание переменной и тд..
        Все рекурсивно
        """
        if current_node is None:
            return

        if current_node.type == AstNodeType.SET:
            op1: AstNode = current_node.op1
            op2: AstNode = current_node.op2

            if op1.type == AstNodeType.USING_VARIABLE or op1.type == AstNodeType.VARIABLE_DECLARATION:
                variable_name: str = op1.value
                self.expression_recursive(op2)
                self.pop(eax)
                self.mov(self.local_var(variable_name), eax)
                return

        elif AstNode.is_comparison_operator(current_node.type):
            self.relation_expression_recursive(current_node)
            return
        elif current_node.type == AstNodeType.IF or current_node.type == AstNodeType.IF_ELSE:
            condition: AstNode = current_node.op1
            statement: AstNode = current_node.op2
            elseStatement: AstNode = current_node.op3

            randId: int = random.randint(0, 1000000)

            startLabel: str = "_if_start_" + str(randId)
            endLabel: str = "_if_end_" + str(randId)
            elseLabel: str = "_if_else_" + str(randId)

            self.block_to_asm_recursive(condition)  # black box
            self.pop(eax)  # последнее сравнение, там обязательно должен быть результат 0/1
            self.cmp(eax, null)

            endOrElseLabel: str = endLabel

            if current_node.type == AstNodeType.IF_ELSE:
                endOrElseLabel = elseLabel

            self.je(endOrElseLabel)

            if current_node.type == AstNodeType.IF_ELSE:
                self.label(startLabel)
                self.block_to_asm_recursive(statement)
                self.jmp(endLabel)
                self.label(elseLabel)
                self.block_to_asm_recursive(elseStatement)
                self.label(endLabel)
            elif current_node.type == AstNodeType.IF:
                self.label(startLabel)
                self.block_to_asm_recursive(statement)
                self.label(endLabel)

            return

        elif current_node.type == AstNodeType.FOR:
            prevention: AstNode = current_node.op1
            condition: AstNode = current_node.op2
            aftereffects: AstNode = current_node.op3
            statement: AstNode = current_node.op4

            randId: int = random.randint(0, 1000000)

            startLabel: str = "_loop_start_" + str(randId)
            endLabel: str = "_loop_end_" + str(randId)
            aftereffectsLabel: str = "_loop_aftereffects_" + str(randId)

            self.block_to_asm_recursive(prevention)
            self.label(startLabel)
            self.block_to_asm_recursive(condition)
            self.pop(eax)
            self.cmp(eax, null)
            self.je(endLabel)
            self.block_to_asm_recursive(statement)
            self.label(aftereffectsLabel)
            self.block_to_asm_recursive(aftereffects)
            self.jmp(startLabel)
            self.label(endLabel)

            return

        elif current_node.type == AstNodeType.EXPRESSION:
            self.block_to_asm_recursive(current_node.op1)
            return
        elif current_node.type == AstNodeType.PRINT:
            self.expression_recursive(current_node.op1)
            self.pop(eax)
            self.push(eax)
            self.raw(tab + "call print\n")
            return

        self.block_to_asm_recursive(current_node.op1)
        self.block_to_asm_recursive(current_node.op2)
        self.block_to_asm_recursive(current_node.op3)
        self.block_to_asm_recursive(current_node.op4)

    def expression_recursive(self, current_node: AstNode):
        if current_node is None:
            return

        if current_node.type == AstNodeType.ADD:
            self.expression_recursive(current_node.op1)
            self.expression_recursive(current_node.op2)
            self.pop(eax)
            self.pop(ebx)
            self.add(eax, ebx)
            self.push(eax)
        elif current_node.type == AstNodeType.SUB:
            self.expression_recursive(current_node.op1)
            self.expression_recursive(current_node.op2)
            self.pop(ebx)
            self.pop(eax)
            self.sub(eax, ebx)
            self.push(eax)
        elif current_node.type == AstNodeType.MUL:
            self.expression_recursive(current_node.op1)
            self.expression_recursive(current_node.op2)
            self.pop(eax)
            self.pop(ebx)
            self.imul(eax, ebx)
            self.push(eax)
        elif current_node.type == AstNodeType.DIV:
            self.expression_recursive(current_node.op1)
            self.expression_recursive(current_node.op2)
            self.pop(ebx)
            self.pop(eax)
            self.mov("div_op_1", eax)
            self.mov("div_op_2", ebx)
            self.finit()
            self.fild("div_op_2")
            self.fild("div_op_1")
            self.fdiv("st(0)", "st(1)")
            self.fist("div_op_1")
            self.push("div_op_1")
        elif current_node.type == AstNodeType.UNARY_MINUS:
            self.expression_recursive(current_node.op1)
            self.pop(eax)
            self.imul(eax, minus_one)
            self.push(eax)
        elif current_node.type == AstNodeType.INTEGER_CONST:
            numberValue: str = current_node.value
            self.push(numberValue)
        elif current_node.type == AstNodeType.USING_VARIABLE:
            variableName: str = current_node.value
            self.push(self.local_var(variableName))
        elif AstNode.is_comparison_operator(current_node.type):
            self.relation_expression_recursive(current_node)
        elif current_node.type == AstNodeType.EXPRESSION:
            self.expression_recursive(current_node.op1)

    def relation_expression_recursive(self, current_node: AstNode):
        if current_node is None:
            return

        if current_node.type == AstNodeType.INTEGER_CONST:
            value_ = int(current_node.value)

            if value_ == 0:
                self.push(null)
            else:
                self.push(one)

        elif current_node.type == AstNodeType.USING_VARIABLE:
            self.count_compare += 1

            label_if_not_equal: str = "_compare_not_equal" + str(self.count_compare)
            label_compare_end: str = "_compare_end" + str(self.count_compare)

            variable_name = current_node.value
            self.cmp(self.local_var(variable_name), null)
            self.jne(label_if_not_equal)
            self.push(null)
            self.jmp(label_compare_end)
            self.label(label_if_not_equal)
            self.push(one)
            self.label(label_compare_end)

        elif current_node.type == AstNodeType.EXPRESSION:
            self.relation_expression_recursive(current_node.op1)
            return
        else:
            self.count_compare += 1
            op1 = current_node.op1
            op2 = current_node.op2
            self.expression_recursive(op1)
            self.pop(ecx)
            self.expression_recursive(op2)
            self.pop(edx)
            self.cmp(ecx, edx)

            label_if_not_equal = "_compare_not_equal" + str(self.count_compare)
            label_compare_end = "_compare_end" + str(self.count_compare)

            if current_node.type == AstNodeType.LESS:
                self.jge(label_if_not_equal)
            elif current_node.type == AstNodeType.LESS_EQUAL:
                self.jg(label_if_not_equal)
            elif current_node.type == AstNodeType.GREATER:
                self.jle(label_if_not_equal)
            elif current_node.type == AstNodeType.GREATER_EQUAL:
                self.jl(label_if_not_equal)
            elif current_node.type == AstNodeType.EQUAL:
                self.jne(label_if_not_equal)
            elif current_node.type == AstNodeType.NOT_EQUAL:
                self.je(label_if_not_equal)

            self.push(one)
            self.jmp(label_compare_end)
            self.label(label_if_not_equal)
            self.push(null)
            self.label(label_compare_end)

            return

    def set_place_for_writing(self, place: CodeGenPlace):
        if place == CodeGenPlace.DATA:
            self.current_place_for_writing = self.data
        elif place == CodeGenPlace.BEFORE_MAIN:
            self.current_place_for_writing = self.before_main
        elif place == CodeGenPlace.MAIN:
            self.current_place_for_writing = self.main

    def write(self, string: str):
        self.file.write(string + '\n')

    def local_var(self, name: str):
        return name + "_variable[ebp]"

    def stack_variable(self, variable: Variable):
        variable_name = variable.name
        self.before_main.append(variable_name + "_variable = " + "-" + str(self.byte_on_stack) + "\n")
        self.byte_on_stack += 4

    # а тут удобные функции, соответсвующие командам ассемблера
    def push(self, value: str):
        self.current_place_for_writing.append(tab + "push " + value + "\n")

    def pop(self, value: str):
        self.current_place_for_writing.append(tab + "pop " + value + "\n")

    def add(self, value1: str, value2: str):
        self.current_place_for_writing.append(tab + "add " + value1 + ", " + value2 + "\n")

    def sub(self, value1: str, value2: str):
        self.current_place_for_writing.append(tab + "sub " + value1 + ", " + value2 + "\n")

    def imul(self, value1: str, value2: str):
        self.current_place_for_writing.append(tab + "imul " + value1 + ", " + value2 + "\n")

    def mov(self, value1: str, value2: str):
        self.current_place_for_writing.append(tab + "mov " + value1 + ", " + value2 + "\n")

    def raw(self, value: str):
        self.current_place_for_writing.append(value)

    def cmp(self, value1: str, value2: str):
        self.current_place_for_writing.append(tab + "cmp " + value1 + ", " + value2 + "\n")

    def jmp(self, value: str):
        self.current_place_for_writing.append(tab + "jmp " + value + "\n")

    def je(self, value: str):
        self.current_place_for_writing.append(tab + "je " + value + "\n")

    def jne(self, value: str):
        self.current_place_for_writing.append(tab + "jne " + value + "\n")

    def jl(self, value: str):
        self.current_place_for_writing.append(tab + "jl " + value + "\n")

    def jle(self, value: str):
        self.current_place_for_writing.append(tab + "jle " + value + "\n")

    def jg(self, value: str):
        self.current_place_for_writing.append(tab + "jg " + value + "\n")

    def jge(self, value: str):
        self.current_place_for_writing.append(tab + "jge " + value + "\n")

    def label(self, value: str):
        self.current_place_for_writing.append(value + ":\n")

    def finit(self):
        self.current_place_for_writing.append(tab + "finit\n")

    def fild(self, value: str):
        self.current_place_for_writing.append(tab + "fild " + value + "\n")

    def fdiv(self, value1: str, value2: str):
        self.current_place_for_writing.append(tab + "fdiv " + value1 + ", " + value2 + "\n")

    def fist(self, value: str):
        self.current_place_for_writing.append(tab + "fist " + value + "\n")
