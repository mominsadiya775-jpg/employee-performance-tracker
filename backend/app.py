from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_mysqldb import MySQL
import pandas as pd
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'kodama.proxy.rlwy.net')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'OoIfUYWpxFTIZfUzVuudYrvBmocsUhmd')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'railway')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 44015))

mysql = MySQL(app)

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
            def g(col):
                val = row.get(col)
                try:
                    import math
                    if val is None or (isinstance(val, float) and math.isnan(val)):
                        return None
                except:
                    pass
                return str(val).strip() if val is not None else None

            entry_date = row.get('Date')
            try:
                entry_date = pd.to_datetime(entry_date).strftime('%Y-%m-%d')
            except:
                entry_date = None

            try:
                total_rec = float(row.get('Total receivable') or 0)
            except:
                total_rec = 0

            try:
                total_pay = float(row.get('T Payable A') or 0)
            except:
                total_pay = 0

            cur.execute("""
                INSERT INTO ledger_entries 
                (entry_date, month, type_of_support, data_managed_by, coordination_done_by, customer_name, total_receivable, total_payable, status, remarks)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                entry_date,
                g('Month'),
                g('Type of support'),
                g('Data Managed By'),
                g('Help Taken From'),
                g('customer Name'),
                total_rec,
                total_pay,
                g('Status'),
                g('Entry status Given / Not Given\nRemarks if any\nPayment status (Paid / Unpaid / Hold )')
            ))
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
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE role='employee'")
        total_employees = cur.fetchone()[0]

        query = "SELECT data_managed_by, coordination_done_by, total_receivable, total_payable FROM ledger_entries"
        params = []
        if month and month != "":
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
            try:
                receivable = float(row[2]) if row[2] else 0
            except:
                receivable = 0
            try:
                payable = float(row[3]) if row[3] else 0
            except:
                payable = 0

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

        return jsonify({
            "success": True,
            "summary": {
                "total_employees": total_employees,
                "total_entries": total_entries,
                "total_company_profit": total_profit
            },
            "top_performers": sorted_perf
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/employee-dashboard', methods=['GET'])
def employee_dashboard():
    try:
        username = request.args.get('username')
        month = request.args.get('month')

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

        if month and month != "":
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
            receivable = float(row[2]) if row[2] else 0
            payable = float(row[3]) if row[3] else 0
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
            entries.append({
                "customer": customer,
                "entry_type": entry_type,
                "profit_share": my_profit,
                "status": status,
                "date": entry_date,
                "month": entry_month
            })

        return jsonify({
            "success": True,
            "summary": {
                "total_entries": solo + shared,
                "solo_entries": solo,
                "shared_entries": shared,
                "total_profit": total_profit
            },
            "entries": entries
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/all-entries', methods=['GET'])
def all_entries():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, entry_date, month, customer_name, data_managed_by, coordination_done_by, total_receivable, total_payable, status FROM ledger_entries ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        entries = []
        for row in rows:
            receivable = float(row[6]) if row[6] else 0
            payable = float(row[7]) if row[7] else 0
            entries.append({
                "id": row[0],
                "entry_date": str(row[1]),
                "month": row[2],
                "customer_name": row[3],
                "data_managed_by": row[4],
                "coordination_done_by": row[5],
                "total_receivable": receivable,
                "total_payable": payable,
                "profit": receivable - payable,
                "status": row[8]
            })
        return jsonify({"success": True, "entries": entries})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/add-member', methods=['POST'])
def add_member():
    try:
        data = request.get_json()
        full_name = data.get('full_name')
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'employee')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (full_name, username, password, role, status) VALUES (%s,%s,%s,%s,'active')",
            (full_name, username, password, role))
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True, "message": "Member added successfully"})
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
        cur = mysql.connection.cursor()
        if month and month != "":
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
        return send_file(output, as_attachment=True, download_name="report.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)