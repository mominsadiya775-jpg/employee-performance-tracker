from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_mysqldb import MySQL
import pandas as pd
from io import BytesIO
import os
import datetime
import math

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'kodama.proxy.rlwy.net')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'OoIfUYWpxFTIZfUzVuudYrvBmocsUhmd')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'railway')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 44015))

mysql = MySQL(app)

PERIOD_MONTHS = {
    'Q1': ('January','February','March'),
    'Q2': ('April','May','June'),
    'Q3': ('July','August','September'),
    'Q4': ('October','November','December'),
    'H1': ('January','February','March','April','May','June'),
    'H2': ('July','August','September','October','November','December'),
    'Annual': ('January','February','March','April','May','June','July','August','September','October','November','December'),
    'FY': ('April','May','June','July','August','September','October','November','December','January','February','March')
}

def parse_date(val, month=None):
    if val is None:
        return None
    try:
        day = int(float(str(val)))
        if month and 1 <= day <= 31:
            month_map = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            m = month_map.get(str(month).strip())
            if m:
                return f"2026-{m:02d}-{day:02d}"
    except:
        pass
    try:
        return pd.to_datetime(val).strftime('%Y-%m-%d')
    except:
        return None

def safe_str(val):
    if val is None:
        return None
    try:
        if isinstance(val, float) and math.isnan(val):
            return None
    except:
        pass
    return str(val).strip()

def safe_float(val):
    try:
        f = float(val)
        if math.isnan(f):
            return 0
        return f
    except:
        return 0

@app.route('/')
def home():
    return "Employee Performance Tracker Running Successfully"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, full_name, username, role FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            return jsonify({"success": True, "user": {"id": user[0], "full_name": user[1], "username": user[2], "role": user[3]}})
        return jsonify({"success": False, "message": "Invalid Credentials"}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file uploaded"})
        file = request.files['file']
        df = pd.read_excel(file)
        cur = mysql.connection.cursor()
        inserted = 0
        for _, row in df.iterrows():
            ref_no = safe_str(
                row.get('Reference No\n(Support Count Number)') or
                row.get('Reference No(Support Count Number)') or
                row.get('Reference No') or
                row.get('Ref No')
            )
            month = safe_str(row.get('Month'))
            entry_date = parse_date(row.get('Date'), month)
            type_of_support = safe_str(row.get('Type of support'))
            data_managed_by = safe_str(row.get('Data Managed By'))
            coordination_done_by = safe_str(row.get('Help Taken From'))
            customer_name = safe_str(row.get('customer Name'))
            total_rec = safe_float(row.get('Total receivable'))
            total_pay = safe_float(row.get('T Payable A'))
            status = safe_str(row.get('Status'))
            remarks = safe_str(row.get('Entry status Given / Not Given\nRemarks if any\nPayment status (Paid / Unpaid / Hold )'))

            cur.execute("""INSERT INTO ledger_entries 
                (reference_no, entry_date, month, type_of_support, data_managed_by, coordination_done_by, customer_name, total_receivable, total_payable, status, remarks)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (ref_no, entry_date, month, type_of_support, data_managed_by, coordination_done_by, customer_name, total_rec, total_pay, status, remarks))
            inserted += 1
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True, "rows_inserted": inserted})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin-dashboard', methods=['GET'])
def admin_dashboard():
    try:
        month = request.args.get('month')
        period = request.args.get('period')
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE role='employee'")
        total_employees = cur.fetchone()[0]
        query = "SELECT data_managed_by, coordination_done_by, total_receivable, total_payable FROM ledger_entries"
        params = []
        if period and period in PERIOD_MONTHS:
            months = PERIOD_MONTHS[period]
            placeholders = ','.join(['%s'] * len(months))
            query += f" WHERE month IN ({placeholders})"
            params = list(months)
        elif month and month != "":
            query += " WHERE month=%s"
            params.append(month)
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        performance = {}
        total_receivable = 0
        total_payable = 0
        total_entries = len(rows)
        for row in rows:
            manager = str(row[0]).strip() if row[0] else None
            coordinator = str(row[1]).strip() if row[1] else None
            receivable = safe_float(row[2])
            payable = safe_float(row[3])
            profit = receivable - payable
            total_receivable += receivable
            total_payable += payable
            if not manager:
                continue
            if not coordinator or manager == coordinator:
                if manager not in performance:
                    performance[manager] = {"entries": 0, "profit": 0}
                performance[manager]["entries"] += 1
                performance[manager]["profit"] += profit
            else:
                split = profit / 2
                if manager not in performance:
                    performance[manager] = {"entries": 0, "profit": 0}
                performance[manager]["entries"] += 0.5
                performance[manager]["profit"] += split
                if coordinator not in performance:
                    performance[coordinator] = {"entries": 0, "profit": 0}
                performance[coordinator]["entries"] += 0.5
                performance[coordinator]["profit"] += split
        total_profit = total_receivable - total_payable
        sorted_perf = sorted(performance.items(), key=lambda x: x[1]["profit"], reverse=True)
        return jsonify({"success": True, "summary": {"total_employees": total_employees, "total_entries": total_entries, "total_company_profit": round(total_profit, 2)}, "top_performers": [[k, {"entries": round(v["entries"], 1), "profit": round(v["profit"], 2)}] for k, v in sorted_perf]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/employee-dashboard', methods=['GET'])
def employee_dashboard():
    try:
        username = request.args.get('username')
        month = request.args.get('month')
        period = request.args.get('period', '')
        cur = mysql.connection.cursor()
        cur.execute("SELECT full_name FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        full_name = user[0]
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name_initial = name_parts[-1][0] if len(name_parts) > 1 else ""
        short_name = f"{first_name} {last_name_initial}"
        query = """SELECT customer_name, type_of_support, total_receivable, total_payable,
                   coordination_done_by, data_managed_by, status, entry_date, month
                   FROM ledger_entries
                   WHERE data_managed_by LIKE %s OR coordination_done_by LIKE %s"""
        params = [f"{short_name}", f"{short_name}"]
        if period and period in PERIOD_MONTHS:
            months = PERIOD_MONTHS[period]
            placeholders = ','.join(['%s'] * len(months))
            query += f" AND month IN ({placeholders})"
            params.extend(list(months))
        elif month and month != "":
            query += " AND month=%s"
            params.append(month)
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        solo = 0
        shared = 0
        total_profit = 0
        entries = []
        for row in rows:
            customer = row[0]
            receivable = safe_float(row[2])
            payable = safe_float(row[3])
            coordinator = str(row[4]).strip() if row[4] else ""
            manager = str(row[5]).strip() if row[5] else ""
            status = row[6]
            entry_date = str(row[7])
            entry_month = row[8]
            profit = receivable - payable
            if not coordinator or short_name.lower() in manager.lower():
                if not coordinator or manager == coordinator:
                    entry_type = "Solo"
                    my_profit = profit
                    solo += 1
                else:
                    entry_type = "Shared"
                    my_profit = profit / 2
                    shared += 1
            else:
                entry_type = "Shared"
                my_profit = profit / 2
                shared += 1
            total_profit += my_profit
            entries.append({"customer": customer, "entry_type": entry_type, "profit_share": round(my_profit, 2), "status": status, "date": entry_date, "month": entry_month})
        return jsonify({"success": True, "summary": {"total_entries": solo + shared, "solo_entries": solo, "shared_entries": shared, "total_profit": round(total_profit, 2)}, "entries": entries})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/all-entries', methods=['GET'])
def all_entries():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, reference_no, entry_date, month, customer_name, data_managed_by, coordination_done_by, total_receivable, total_payable, status FROM ledger_entries ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        entries = []
        for row in rows:
            receivable = safe_float(row[7])
            payable = safe_float(row[8])
            entries.append({
                "id": row[0],
                "reference_no": row[1],
                "entry_date": str(row[2]),
                "month": row[3],
                "customer_name": row[4],
                "data_managed_by": row[5],
                "coordination_done_by": row[6],
                "total_receivable": round(receivable, 2),
                "total_payable": round(payable, 2),
                "profit": round(receivable - payable, 2),
                "status": row[9]
            })
        return jsonify({"success": True, "entries": entries})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/add-member', methods=['POST'])
def add_member():
    try:
        data = request.get_json()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (full_name, username, password, role, status) VALUES (%s,%s,%s,%s,'active')",
            (data.get('full_name'), data.get('username'), data.get('password'), data.get('role', 'employee')))
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True, "message": "Member added successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get-members', methods=['GET'])
def get_members():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, full_name, username, role, status FROM users ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        members = [{"id": r[0], "full_name": r[1], "username": r[2], "role": r[3], "status": r[4]} for r in rows]
        return jsonify({"success": True, "members": members})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/delete-member/<int:id>', methods=['DELETE'])
def delete_member(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/delete-entry/<int:id>', methods=['DELETE'])
def delete_entry(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM ledger_entries WHERE id=%s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/export-report', methods=['GET'])
def export_report():
    try:
        month = request.args.get('month')
        period = request.args.get('period')
        cur = mysql.connection.cursor()
        if period and period in PERIOD_MONTHS:
            months = PERIOD_MONTHS[period]
            placeholders = ','.join(['%s'] * len(months))
            cur.execute(f"SELECT * FROM ledger_entries WHERE month IN ({placeholders})", list(months))
        elif month and month != "":
            cur.execute("SELECT * FROM ledger_entries WHERE month=%s", (month,))
        else:
            cur.execute("SELECT * FROM ledger_entries")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cur.close()
        df = pd.DataFrame(rows, columns=columns)
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return send_file(output, as_attachment=True, download_name="report.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)