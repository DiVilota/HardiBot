import ast
import operator


_OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def evaluar_expresion(expresion: str):
    expresion = expresion.strip()
    if not expresion:
        raise ValueError("Expresion vacia")
    try:
        arbol = ast.parse(expresion, mode="eval")
        return _eval_ast(arbol.body)
    except SyntaxError as e:
        raise ValueError(f"Error de sintaxis: {e}") from e


def _eval_ast(nodo):
    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)):
        return nodo.value
    if isinstance(nodo, ast.BinOp):
        op = _OPERADORES.get(type(nodo.op))
        if op is None:
            raise ValueError(f"Operacion no permitida: {type(nodo.op).__name__}")
        return op(_eval_ast(nodo.left), _eval_ast(nodo.right))
    if isinstance(nodo, ast.UnaryOp):
        op = _OPERADORES.get(type(nodo.op))
        if op is None:
            raise ValueError(f"Operacion no permitida: {type(nodo.op).__name__}")
        return op(_eval_ast(nodo.operand))
    raise ValueError(f"Expresion no valida: {type(nodo).__name__}")
