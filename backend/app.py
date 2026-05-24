from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_mysqldb import MySQL
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)

# ==========================================
# MYSQL CONFIG
# ==========================================

app.config['MYSQL_HOST'] = os.environ.get('MYSQLHOST', 'kodama.proxy.rlwy.net')
app.config['MYSQL_USER'] = os.environ.get('MYSQLUSER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQLPASSWORD', 'OoIfUYWpxFTIZfUzVuudYrVBmocsUhmd')
app.config['MYSQL_DB'] = os.environ.get('MYSQLDATABASE', 'railway')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQLPORT', 44015))

mysql = MySQL(app)


# ==========================================
# HOME ROUTE
# ==========================================

@app.route('/')
def home():
    return "Employee Performance Tracker Running Successfully"


# ==========================================
# LOGIN API
# ==========================================

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, full_name, username, role
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
# ADMIN DASHBOARD API
# ==========================================

@app.route('/admin-dashboard', methods=['GET'])
def admin_dashboard():
    try:
        month = request.args.get('month')

        cur = mysql.connection.cursor()

        if month and month != "":
            cur.execute(
                "SELECT * FROM ledger_entries WHERE month=%s",
                (month,)
            )
        else:
            cur.execute("SELECT * FROM ledger_entries")

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()

        total_profit = 0

        for row in rows:
            try:
                # If total_receivable is in another index, adjust here
                total_profit += float(row[5]) if row[5] else 0
            except:
                pass

        summary = {
            "total_employees": 0,
            "total_entries": len(rows),
            "total_company_profit": total_profit
        }

        return jsonify({
            "success": True,
            "entries": rows,
            "summary": summary,
            "top_performers": []
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==========================================
# EXPORT REPORT
# ==========================================

@app.route('/export-report', methods=['GET'])
def export_report():
    try:
        month = request.args.get('month')

        cur = mysql.connection.cursor()

        if month and month != "":
            cur.execute(
                "SELECT * FROM ledger_entries WHERE month=%s",
                (month,)
            )
        else:
            cur.execute("SELECT * FROM ledger_entries")

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()

        df = pd.DataFrame(rows, columns=columns)

        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="employee_report.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

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