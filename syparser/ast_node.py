from .ast_node_type import AstNodeType


class AstNode:
    type: AstNodeType
    value: str
    child_nodes: list

    def __init__(self, type_: AstNodeType, value_: str = "", op1=None, op2=None, op3=None, op4=None):
        self.type = type_
        self.value = value_

        self.op1 = op1
        self.op2 = op2
        self.op3 = op3
        self.op4 = op4

    def hangup_child1(self, child):
        if child is not None and child != self:
            self.child_nodes.append(child)

    @staticmethod
    def is_comparison_operator(type_: AstNodeType):
        return type_ == AstNodeType.LESS or \
               type_ == AstNodeType.GREATER or \
               type_ == AstNodeType.LESS_EQUAL or \
               type_ == AstNodeType.GREATER_EQUAL or \
               type_ == AstNodeType.EQUAL or \
               type_ == AstNodeType.NOT_EQUAL
