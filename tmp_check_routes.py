import ast
from pathlib import Path

source = Path("garutvon/backend/routes.py").read_text()
try:
    ast.parse(source)
    print("ok")
except SyntaxError as exc:
    print(exc)
    print("line", exc.lineno)
    print("offset", exc.offset)
