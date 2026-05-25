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
                if pd.isna(val) if hasattr(val, '__class__') else False:
                    return None
                try:
                    import math
                    if math.isnan(float(val)):
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

            cur.execute("""
                INSERT INTO ledger_entries 
                (entry_date, month, type_of_support, data_managed_by, coordination_done_by, customer_name, total_receivable, status, remarks)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                entry_date,
                g('Month'),
                g('Type of support'),
                g('Data Managed By'),
                g('Help Taken From'),
                g('customer Name'),
                total_rec,
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
        if month and month != "":
            cur.execute("SELECT data_managed_by, coordination_done_by, total_receivable FROM ledger_entries WHERE month=%s", (month,))
        else:
            cur.execute("SELECT data_managed_by, coordination_done_by, total_receivable FROM ledger_entries")
        rows = cur.fetchall()
        cur.close()
        performance = {}
        total_profit = 0
        total_entries = len(rows)
        for row in rows:
            manager = str(row[0]).strip() if row[0] else None
            coordinator = str(row[1]).strip() if row[1] else None
            try:
                profit = float(row[2]) if row[2] else 0
            except:
                profit = 0
            total_profit += profit
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

@app.route('/all-entries', methods=['GET'])
def all_entries():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, entry_date, month, customer_name, data_managed_by, coordination_done_by, total_receivable, status FROM ledger_entries ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        entries = []
        for row in rows:
            entries.append({
                "id": row[0],
                "entry_date": str(row[1]),
                "month": row[2],
                "customer_name": row[3],
                "data_managed_by": row[4],
                "coordination_done_by": row[5],
                "total_receivable": float(row[6]) if row[6] else 0,
                "status": row[7]
            })
        return jsonify({"success": True, "entries": entries})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/add-entry', methods=['POST'])
def add_entry():
    try:
        data = request.get_json()
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO ledger_entries (entry_date, month, type_of_support, data_managed_by, coordination_done_by, customer_name, total_receivable, status, remarks)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (data.get('entry_date'), data.get('month'), data.get('type_of_support'),
             data.get('data_managed_by'), data.get('coordination_done_by'),
             data.get('customer_name'), float(data.get('total_receivable') or 0),
             data.get('status'), data.get('remarks')))
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