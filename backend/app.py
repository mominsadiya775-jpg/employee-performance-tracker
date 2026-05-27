from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_mysqldb import MySQL
import jwt
import datetime
import pandas as pd
import os
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_123'
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['MYSQL_HOST'] = 'odama.proxy.rlwy.net'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'OoIfUYWpxFTIZfUzVuudYrvBmocsUhmd'
app.config['MYSQL_DB'] = 'railway'
app.config['MYSQL_PORT'] = 44015
app.config['UPLOAD_FOLDER'] = 'uploads'

mysql = MySQL(app)
os.makedirs('uploads', exist_ok=True)

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
        cur.execute("SELECT id, full_name, username, password, role FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()
        if not user:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
        token = jwt.encode({
            'id': user[0],
            'username': user[2],
            'role': user[4],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user[0],
                "full_name": user[1],
                "username": user[2],
                "role": user[4]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/add-entry', methods=['POST'])
def add_entry():
    try:
        data = request.get_json()
        entry_date = data.get('entry_date')
        month = data.get('month')
        type_of_support = data.get('type_of_support')
        data_managed_by = data.get('data_managed_by')
        coordination_done_by = data.get('coordination_done_by')
        customer_name = data.get('customer_name')
        total_receivable = data.get('total_receivable')
        status = data.get('status')
        remarks = data.get('remarks')
        try:
            total_receivable = float(total_receivable)
        except:
            total_receivable = 0
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO ledger_entries (entry_date, month, type_of_support, data_managed_by, coordination_done_by, customer_name, total_receivable, status, remarks) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (entry_date, month, type_of_support, data_managed_by, coordination_done_by, customer_name, total_receivable, status, remarks))
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True, "message": "Entry added successfully"})
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
            try:
                total_receivable = float(row[6]) if row[6] else 0
            except:
                total_receivable = 0
            entries.append({
                "id": row[0],
                "entry_date": str(row[1]),
                "month": row[2],
                "customer_name": row[3],
                "data_managed_by": row[4],
                "coordination_done_by": row[5],
                "total_receivable": total_receivable,
                "status": row[7]
            })
        return jsonify({"success": True, "entries": entries})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/delete-entry/<int:id>', methods=['DELETE'])
def delete_entry(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM ledger_entries WHERE id=%s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True, "message": "Entry deleted successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/update-entry/<int:id>', methods=['PUT'])
def update_entry(id):
    try:
        data = request.get_json()
        customer_name = data.get('customer_name')
        total_receivable = data.get('total_receivable')
        status = data.get('status')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE ledger_entries SET customer_name=%s, total_receivable=%s, status=%s WHERE id=%s", (customer_name, total_receivable, status, id))
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True, "message": "Entry updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No file uploaded"})
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "message": "No selected file"})
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        df = pd.read_excel(filepath)
        cur = mysql.connection.cursor()
        inserted_rows = 0
        for index, row in df.iterrows():
            entry_date = row.get('Date')
            if pd.notna(entry_date):
                try:
                    entry_date = pd.to_datetime(entry_date).strftime('%Y-%m-%d')
                except:
                    entry_date = None
            else:
                entry_date = None
            try:
                total_rec = float(row.get('Total receivable')) if pd.notna(row.get('Total receivable')) else 0
            except:
                total_rec = 0
            values = (
                entry_date,
                str(row.get('Month')) if pd.notna(row.get('Month')) else None,
                str(row.get('Type of support')) if pd.notna(row.get('Type of support')) else None,
                str(row.get('Data Managed By')) if pd.notna(row.get('Data Managed By')) else None,
                str(row.get('Coordination done by')) if pd.notna(row.get('Coordination done by')) else None,
                str(row.get('Customer Name')) if pd.notna(row.get('Customer Name')) else None,
                total_rec,
                str(row.get('Status')) if pd.notna(row.get('Status')) else None,
                str(row.get('Remarks if any')) if pd.notna(row.get('Remarks if any')) else None
            )
            cur.execute("""INSERT INTO ledger_entries (entry_date, month, type_of_support, data_managed_by, coordination_done_by, customer_name, total_receivable, status, remarks) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", values)
            inserted_rows += 1
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True, "message": "Excel uploaded successfully", "rows_inserted": inserted_rows})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin-dashboard', methods=['GET'])
def admin_dashboard():
    try:
        month = request.args.get('month')
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE role='employee'")
        total_employees = cur.fetchone()[0]
        if month:
            cur.execute("SELECT data_managed_by, coordination_done_by, total_receivable FROM ledger_entries WHERE month=%s", (month,))
        else:
            cur.execute("SELECT data_managed_by, coordination_done_by, total_receivable FROM ledger_entries")
        rows = cur.fetchall()
        cur.close()
        performance = {}
        total_company_profit = 0
        total_entries = 0
        for row in rows:
            manager = row[0]
            coordinator = row[1]
            try:
                profit = float(row[2]) if row[2] not in [None, ''] else 0
            except:
                profit = 0
            total_company_profit += profit
            total_entries += 1
            if manager is None or str(manager).strip() == "":
                continue
            if not coordinator or manager == coordinator:
                if manager not in performance:
                    performance[manager] = {"entries": 0, "profit": 0}
                performance[manager]["entries"] += 1
                performance[manager]["profit"] += profit
            else:
                split_profit = profit / 2
                if manager not in performance:
                    performance[manager] = {"entries": 0, "profit": 0}
                performance[manager]["entries"] += 0.5
                performance[manager]["profit"] += split_profit
                if coordinator and str(coordinator).strip() != "":
                    if coordinator not in performance:
                        performance[coordinator] = {"entries": 0, "profit": 0}
                    performance[coordinator]["entries"] += 0.5
                    performance[coordinator]["profit"] += split_profit
        cleaned_performance = {str(k): v for k, v in performance.items() if k is not None and str(k).strip() != ""}
        sorted_performance = sorted(cleaned_performance.items(), key=lambda x: x[1]["profit"], reverse=True)
        return jsonify({"success": True, "month_filter": month, "summary": {"total_employees": total_employees, "total_entries": total_entries, "total_company_profit": total_company_profit}, "top_performers": sorted_performance})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/export-report', methods=['GET'])
def export_report():
    try:
        month = request.args.get('month')
        cur = mysql.connection.cursor()
        if month:
            cur.execute("SELECT entry_date, month, customer_name, data_managed_by, coordination_done_by, total_receivable, status FROM ledger_entries WHERE month=%s", (month,))
        else:
            cur.execute("SELECT entry_date, month, customer_name, data_managed_by, coordination_done_by, total_receivable, status FROM ledger_entries")
        rows = cur.fetchall()
        cur.close()
        data = [{"Date": str(row[0]), "Month": row[1], "Customer Name": row[2], "Managed By": row[3], "Coordination By": row[4], "Total Receivable": float(row[5]), "Status": row[6]} for row in rows]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        output.seek(0)
        return send_file(output, download_name='performance_report.xlsx', as_attachment=True)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)