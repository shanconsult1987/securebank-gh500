
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


@app.get("/calculate")
def calculate():

    expression = request.args.get("expression", "1+1")

    # INTENTIONALLY VULNERABLE TRAINING CODE
    result = eval(expression)

    return jsonify({
        "expression": expression,
        "result": result
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
