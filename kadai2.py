import ast
import operator as op
import tkinter as tk
from tkinter import ttk


_BIN_OPS: dict[type[ast.AST], object] = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
}
_UNARY_OPS: dict[type[ast.AST], object] = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}


def _safe_eval(expr: str) -> float:
    """
    Evaluate expression consisting of numbers, + - * / and parentheses.
    """
    expr = expr.strip()
    if not expr:
        raise ValueError("empty")

    node = ast.parse(expr, mode="eval")

    def _eval(n: ast.AST) -> float:
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN_OPS:
            return _BIN_OPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _UNARY_OPS:
            return _UNARY_OPS[type(n.op)](_eval(n.operand))
        if isinstance(n, ast.Call):
            raise ValueError("function call not allowed")
        raise ValueError("invalid expression")

    return _eval(node)


class CalculatorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("電卓")
        self.resizable(False, False)

        self._expr = tk.StringVar(value="")
        self._result = tk.StringVar(value="")

        root = ttk.Frame(self, padding=12)
        root.grid(row=0, column=0, sticky="nsew")

        display = ttk.Entry(
            root,
            textvariable=self._expr,
            justify="right",
            font=("Segoe UI", 16),
            width=18,
        )
        display.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 8))
        display.focus_set()

        result = ttk.Label(
            root,
            textvariable=self._result,
            anchor="e",
            font=("Segoe UI", 11),
            foreground="#555555",
        )
        result.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 10))

        buttons: list[tuple[str, int, int, int]] = [
            ("C", 2, 0, 1),
            ("⌫", 2, 1, 1),
            ("(", 2, 2, 1),
            (")", 2, 3, 1),
            ("7", 3, 0, 1),
            ("8", 3, 1, 1),
            ("9", 3, 2, 1),
            ("÷", 3, 3, 1),
            ("4", 4, 0, 1),
            ("5", 4, 1, 1),
            ("6", 4, 2, 1),
            ("×", 4, 3, 1),
            ("1", 5, 0, 1),
            ("2", 5, 1, 1),
            ("3", 5, 2, 1),
            ("−", 5, 3, 1),
            ("0", 6, 0, 2),
            (".", 6, 2, 1),
            ("+", 6, 3, 1),
            ("=", 7, 0, 4),
        ]

        for text, r, c, cs in buttons:
            b = ttk.Button(root, text=text, command=lambda t=text: self._on_press(t))
            b.grid(row=r, column=c, columnspan=cs, sticky="nsew", padx=3, pady=3)

        for c in range(4):
            root.columnconfigure(c, weight=1)

        self.bind("<Return>", lambda _e: self._calculate())
        self.bind("<KP_Enter>", lambda _e: self._calculate())
        self.bind("<Escape>", lambda _e: self._clear())
        self.bind("<BackSpace>", lambda _e: self._backspace())

        for ch in "0123456789.+-*/()":
            self.bind(ch, self._key_append)

    def _key_append(self, event: tk.Event) -> None:
        self._append(event.char)

    def _on_press(self, t: str) -> None:
        if t == "C":
            self._clear()
            return
        if t == "⌫":
            self._backspace()
            return
        if t == "=":
            self._calculate()
            return

        if t == "÷":
            self._append("/")
        elif t == "×":
            self._append("*")
        elif t == "−":
            self._append("-")
        else:
            self._append(t)

    def _append(self, s: str) -> None:
        self._expr.set(self._expr.get() + s)
        self._preview()

    def _clear(self) -> None:
        self._expr.set("")
        self._result.set("")

    def _backspace(self) -> None:
        cur = self._expr.get()
        self._expr.set(cur[:-1])
        self._preview()

    def _preview(self) -> None:
        expr = self._expr.get()
        if not expr.strip():
            self._result.set("")
            return
        try:
            val = _safe_eval(expr)
            self._result.set(str(self._format_number(val)))
        except Exception:
            self._result.set("")

    def _calculate(self) -> None:
        expr = self._expr.get()
        try:
            val = _safe_eval(expr)
        except ZeroDivisionError:
            self._result.set("0で割れません")
            return
        except Exception:
            self._result.set("式が正しくありません")
            return

        self._expr.set(str(self._format_number(val)))
        self._result.set("")

    @staticmethod
    def _format_number(v: float) -> float | int:
        if abs(v - round(v)) < 1e-12:
            return int(round(v))
        return v


def main() -> None:
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
