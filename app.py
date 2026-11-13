
import ast
from flask import Flask, jsonify, request

app = Flask(__name__)

ACCOUNTS = {
    "1001": {
        "customer": "Customer A",
        "balance": 50000
    },
    "1002": {
        "customer": "Customer B",
        "balance": 75000
    }
}

@app.get("/")
def home():
    return jsonify({
        "application": "SecureBank",
        "version": "1.0",
        "status": "running"
    })


@app.get("/health")
def health():
    return jsonify({"status": "healthy"})


@app.get("/accounts/<account_id>")
def get_account(account_id):

    account = ACCOUNTS.get(account_id)

    if not account:
        return jsonify({
            "error": "Account not found"
        }), 404

    return jsonify(account)


@app.post("/transactions")
def create_transaction():

    data = request.get_json(silent=True) or {}

    account_id = data.get("account_id")
    amount = data.get("amount", 0)

    if account_id not in ACCOUNTS:
        return jsonify({
            "error": "Invalid account"
        }), 400

    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({
            "error": "Invalid transaction amount"
        }), 400

    if amount > ACCOUNTS[account_id]["balance"]:
        return jsonify({
            "error": "Insufficient balance"
        }), 400

    ACCOUNTS[account_id]["balance"] -= amount

    return jsonify({
        "status": "success",
        "account_id": account_id,
        "transaction_amount": amount
    })


def _safe_eval_arithmetic(expression):
    allowed_bin_ops = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a ** b,
    }
    allowed_unary_ops = {
        ast.UAdd: lambda a: +a,
        ast.USub: lambda a: -a,
    }

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Num):  # compatibility for older Python AST
            return node.n
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_bin_ops:
            return allowed_bin_ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_unary_ops:
            return allowed_unary_ops[type(node.op)](_eval(node.operand))
        raise ValueError("Invalid expression")

    tree = ast.parse(expression, mode="eval")
    return _eval(tree)


@app.get("/calculate")
def calculate():

    expression = request.args.get("expression", "1+1")

    try:
        result = _safe_eval_arithmetic(expression)
    except Exception:
        return jsonify({
            "error": "Invalid expression"
        }), 400

    return jsonify({
        "expression": expression,
        "result": result
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
