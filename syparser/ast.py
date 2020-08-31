from .ast_node_type import AstNodeType
from .ast_node import AstNode

from .var_table import VariableTable


class AST:
    tree: AstNode

    variables: VariableTable

    def __init__(self):
        self.tree = None
        self.variables = VariableTable()

    def print_recursive(self, current_node: AstNode, level: int, out=print):
        if current_node is None:
            return

        temp = '   ' * level + "+-" + self.calculate_name(current_node.type) + ''

        if current_node.value != "":
            temp = f"{temp} '{current_node.value}'"

        out(temp)

        self.print_recursive(current_node.op1, level + 1, out)
        self.print_recursive(current_node.op2, level + 1, out)
        self.print_recursive(current_node.op3, level + 1, out)
        self.print_recursive(current_node.op4, level + 1, out)

    def print(self):
        self.print_recursive(self.tree, 0, print)

    def log_out(self):
        file = open("ast", "w")
        self.print_recursive(self.tree, 0, file.write)
        file.close()

    @staticmethod
    def calculate_name(node_type: AstNodeType) -> str:
        return str(node_type).split('.')[1].upper()