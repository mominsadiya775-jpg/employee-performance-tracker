from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
from flask_mysqldb import MySQL
import pandas as pd
import os
import io

app = Flask(__name__)
CORS(app)

# ==========================================
# MYSQL CONFIG
# ==========================================

app.config['MYSQL_HOST'] = os.environ.get(
    'MYSQLHOST',
    'kodama.proxy.rlwy.net'
)

app.config['MYSQL_USER'] = os.environ.get(
    'MYSQLUSER',
    'root'
)

app.config['MYSQL_PASSWORD'] = os.environ.get(
    'MYSQLPASSWORD',
    'YOUR_PASSWORD'
)

app.config['MYSQL_DB'] = os.environ.get(
    'MYSQLDATABASE',
    'railway'
)

app.config['MYSQL_PORT'] = int(
    os.environ.get('MYSQLPORT', 44015)
)

mysql = MySQL(app)

# ==========================================
# HOME
# ==========================================

@app.route('/')
def home():
    return "Employee Performance Tracker Running Successfully"

# ==========================================
# LOGIN
# ==========================================

@app.route('/login', methods=['POST'])
def login():

    try:

        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT
                id,
                full_name,
                username,
                role
            FROM users
            WHERE username=%s AND password=%s
        """, (username, password))

        user = cur.fetchone()

        cur.close()

        if user:

            return jsonify({
                "success": True,
                "user": {
                    "id": user[0],
                    "full_name": user[1],
                    "username": user[2],
                    "role": user[3]
                }
            })

        return jsonify({
            "success": False,
            "message": "Invalid Credentials"
        }), 401

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==========================================
# EMPLOYEE DASHBOARD
# ==========================================

@app.route('/employee-dashboard/<employee_name>', methods=['GET'])
def employee_dashboard(employee_name):

    try:

        month = request.args.get('month')

        cur = mysql.connection.cursor()

        if month and month != "":

            cur.execute("""
                SELECT
                    data_managed_by,
                    coordination_done_by,
                    total_receivable,
                    customer_name,
                    status
                FROM ledger_entries
                WHERE month=%s
            """, (month,))

        else:

            cur.execute("""
                SELECT
                    data_managed_by,
                    coordination_done_by,
                    total_receivable,
                    customer_name,
                    status
                FROM ledger_entries
            """)

        rows = cur.fetchall()

        cur.close()

        dashboard = {
            "employee_name": employee_name,
            "total_entries": 0,
            "solo_entries": 0,
            "shared_entries": 0,
            "total_profit": 0,
            "entries": []
        }

        for row in rows:

            manager = str(row[0]).strip() if row[0] else ""
            coordinator = str(row[1]).strip() if row[1] else ""

            try:
                profit = float(row[2]) if row[2] else 0
            except:
                profit = 0

            customer_name = row[3]
            status = row[4]

            # SOLO ENTRY
            if coordinator == "" or manager == coordinator:

                if manager == employee_name:

                    dashboard["total_entries"] += 1
                    dashboard["solo_entries"] += 1
                    dashboard["total_profit"] += profit

                    dashboard["entries"].append({
                        "customer_name": customer_name,
                        "profit_share": profit,
                        "status": status,
                        "entry_type": "solo"
                    })

            # SHARED ENTRY
            else:

                split_profit = profit / 2

                if manager == employee_name:

                    dashboard["total_entries"] += 0.5
                    dashboard["shared_entries"] += 0.5
                    dashboard["total_profit"] += split_profit

                    dashboard["entries"].append({
                        "customer_name": customer_name,
                        "profit_share": split_profit,
                        "status": status,
                        "entry_type": "shared"
                    })

                if coordinator == employee_name:

                    dashboard["total_entries"] += 0.5
                    dashboard["shared_entries"] += 0.5
                    dashboard["total_profit"] += split_profit

                    dashboard["entries"].append({
                        "customer_name": customer_name,
                        "profit_share": split_profit,
                        "status": status,
                        "entry_type": "shared"
                    })

        return jsonify({
            "success": True,
            "dashboard": dashboard
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==========================================
# RUN APP
# ==========================================

if __name__ == '__main__':
    app.run(debug=True)