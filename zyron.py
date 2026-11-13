import ast
import math
import operator
import tkinter as tk

# ==============================
# PROFESSIONAL CALCULATOR
# ==============================

root = tk.Tk()
root.title("NEXUS CALCULATOR")
root.geometry("440x720")
root.minsize(380, 650)
root.configure(bg="#10131c")

BG = "#10131c"
PANEL = "#191e2b"
BTN = "#252c3b"
BTN_HOVER = "#343e52"
ACCENT = "#7c5cff"
TEXT = "#ffffff"
MUTED = "#929bb0"
GREEN = "#39dca5"

expression = ""
history = []
scientific = False
dark = True

# ==============================
# DISPLAY
# ==============================

header = tk.Label(
    root,
    text="N E X U S   /   C A L C U L A T O R",
    bg=BG,
    fg=ACCENT,
    font=("Segoe UI", 12, "bold"),
)
header.pack(pady=(22, 15))

display_frame = tk.Frame(root, bg=PANEL)
display_frame.pack(fill="x", padx=18, pady=8)

display = tk.Entry(
    display_frame,
    font=("Segoe UI", 27),
    bg=PANEL,
    fg=TEXT,
    insertbackground=TEXT,
    bd=0,
    justify="right",
)
display.pack(fill="x", padx=15, pady=(25, 5), ipady=10)

result_label = tk.Label(
    display_frame, text="READY", bg=PANEL, fg=GREEN, font=("Segoe UI", 13), anchor="e"
)
result_label.pack(fill="x", padx=18, pady=(0, 20))

# ==============================
# SAFE CALCULATION
# ==============================

binary_ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

unary_ops = {ast.UAdd: operator.pos, ast.USub: operator.neg}

functions = {
    "sqrt": math.sqrt,
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "log": math.log10,
    "ln": math.log,
    "abs": abs,
}


def calculate_node(node):
    if isinstance(node, ast.Expression):
        return calculate_node(node.body)

    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float):
            return node.value
        raise ValueError("Invalid number")

    if isinstance(node, ast.BinOp):
        op = type(node.op)
        if op not in binary_ops:
            raise ValueError("Invalid operation")

        left = calculate_node(node.left)
        right = calculate_node(node.right)

        if op is ast.Pow and abs(right) > 1000:
            raise ValueError("Exponent too large")

        value = binary_ops[op](left, right)

        if isinstance(value, complex) or abs(value) > 1e100:
            raise ValueError("Result too large")

        return value

    if isinstance(node, ast.UnaryOp):
        op = type(node.op)
        if op not in unary_ops:
            raise ValueError("Invalid operation")
        return unary_ops[op](calculate_node(node.operand))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Invalid function")

        name = node.func.id
        if name not in functions or len(node.args) != 1:
            raise ValueError("Invalid function")

        return functions[name](calculate_node(node.args[0]))

    raise ValueError("Invalid expression")


def evaluate(expression):
    expression = expression.replace("×", "*").replace("÷", "/")
    expression = expression.replace("^", "**")
    expression = expression.replace("π", "pi")

    tree = ast.parse(expression, mode="eval")

    # pi and e are the only allowed constants
    class Constants(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == "pi":
                return ast.copy_location(ast.Constant(math.pi), node)
            if node.id == "e":
                return ast.copy_location(ast.Constant(math.e), node)
            return node

    tree = Constants().visit(tree)
    ast.fix_missing_locations(tree)

    return calculate_node(tree)


# ==============================
# FUNCTIONS
# ==============================


def press(value):
    global expression

    if value == "AC":
        expression = ""
        display.delete(0, tk.END)
        result_label.config(text="CLEARED")
        return

    if value == "DEL":
        expression = expression[:-1]
        display.delete(0, tk.END)
        display.insert(0, expression)
        return

    if value == "=":
        try:
            result = evaluate(expression)
            formatted = f"{result:.12g}"

            history.append(f"{expression} = {formatted}")
            result_label.config(text="= " + formatted)

            expression = formatted
            display.delete(0, tk.END)
            display.insert(0, expression)

        except Exception:
            result_label.config(text="ERROR")
        return

    if value == "√":
        value = "sqrt("
    elif value in ("sin", "cos", "tan", "log", "ln", "abs"):
        value += "("
    elif value == "x²":
        expression += "**2"
        display.delete(0, tk.END)
        display.insert(0, expression)
        return
    elif value == "π":
        value = "π"
    elif value == "1/x":
        expression = f"1/({expression})"
        display.delete(0, tk.END)
        display.insert(0, expression)
        return
    elif value == "%":
        expression += "/100"
        display.delete(0, tk.END)
        display.insert(0, expression)
        return

    expression += value

    display.delete(0, tk.END)
    display.insert(0, expression)


def keyboard_input(event):
    if event.keysym == "Return":
        press("=")
    elif event.keysym == "Escape":
        press("AC")
    elif event.keysym == "BackSpace":
        press("DEL")


root.bind("<Key>", keyboard_input)

# ==============================
# BUTTON DESIGN
# ==============================

button_frame = tk.Frame(root, bg=BG)
button_frame.pack(fill="both", expand=True, padx=18, pady=12)

buttons = [
    ["AC", "DEL", "(", ")"],
    ["sin", "cos", "tan", "√"],
    ["log", "ln", "π", "e"],
    ["7", "8", "9", "÷"],
    ["4", "5", "6", "×"],
    ["1", "2", "3", "-"],
    ["0", ".", "%", "+"],
    ["x²", "^", "1/x", "="],
]


def button_color(value):
    if value == "=":
        return ACCENT
    if value in ["AC", "DEL"]:
        return "#a33f58"
    if value in ["+", "-", "×", "÷", "^"]:
        return "#343e58"
    if value in ["sin", "cos", "tan", "√", "log", "ln", "π", "e"]:
        return "#30304a"
    return BTN


for r, row in enumerate(buttons):
    button_frame.rowconfigure(r, weight=1)

    for c, value in enumerate(row):
        button_frame.columnconfigure(c, weight=1)

        btn = tk.Button(
            button_frame,
            text=value,
            font=("Segoe UI", 15, "bold"),
            bg=button_color(value),
            fg=TEXT,
            activebackground=BTN_HOVER,
            activeforeground=TEXT,
            bd=0,
            relief="flat",
            cursor="hand2",
            command=lambda v=value: press(v),
        )

        btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

# ==============================
# BOTTOM PANEL
# ==============================

bottom = tk.Frame(root, bg=BG)
bottom.pack(fill="x", padx=20, pady=(0, 15))


def show_history():
    window = tk.Toplevel(root)
    window.title("Calculation History")
    window.geometry("350x400")
    window.configure(bg=PANEL)

    tk.Label(
        window, text="HISTORY", bg=PANEL, fg=ACCENT, font=("Segoe UI", 16, "bold")
    ).pack(pady=15)

    box = tk.Listbox(window, bg=BG, fg=TEXT, font=("Segoe UI", 11), bd=0)
    box.pack(fill="both", expand=True, padx=12, pady=12)

    for item in reversed(history):
        box.insert(tk.END, item)


tk.Button(
    bottom,
    text="◷  HISTORY",
    bg=PANEL,
    fg=MUTED,
    activebackground=BTN_HOVER,
    bd=0,
    font=("Segoe UI", 11, "bold"),
    command=show_history,
).pack(side="left", ipadx=12, ipady=9)

tk.Label(
    bottom, text="NEXUS v1.0", bg=BG, fg=ACCENT, font=("Segoe UI", 10, "bold")
).pack(side="right")

root.mainloop()
