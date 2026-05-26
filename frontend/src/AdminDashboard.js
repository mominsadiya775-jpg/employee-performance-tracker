import EntriesTable from "./EntriesTable";
import Layout from "./Layout";
import AnalyticsChart from "./AnalyticsChart";
import { useEffect, useState } from "react";
import axios from "axios";

const API = "https://employee-performance-tracker-gtez.onrender.com";

function AdminDashboard({ user, handleLogout }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [showAddMember, setShowAddMember] = useState(false);
  const [newMember, setNewMember] = useState({ full_name: "", username: "", password: "", role: "employee" });

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API}/admin-dashboard?month=${selectedMonth}`);
      setDashboardData(response.data);
    } catch (error) {
      console.log("Dashboard Error:", error);
    }
  };

  const handleExport = () => {
    window.open(`${API}/export-report?month=${selectedMonth}`);
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post(`${API}/upload-excel`, formData);
      if (res.data.success) {
        alert(`${res.data.rows_inserted} rows uploaded successfully!`);
        fetchDashboard();
      } else {
        alert("Upload failed: " + res.data.error);
      }
    } catch (err) {
      alert("Upload error: " + err.message);
    }
  };

  const handleAddMember = async () => {
    try {
      const res = await axios.post(`${API}/add-member`, newMember);
      if (res.data.success) {
        alert("Member added successfully!");
        setShowAddMember(false);
        setNewMember({ full_name: "", username: "", password: "", role: "employee" });
        fetchDashboard();
      } else {
        alert("Failed: " + res.data.error);
      }
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [selectedMonth]);

  if (!dashboardData) {
    return <h2 className="text-center mt-5">Loading...</h2>;
  }

  return (
    <Layout user={user} handleLogout={handleLogout}>
      <div className="container mt-4">
        <div className="mb-4">
          <h1>Admin Dashboard</h1>
          <h5>Welcome, {user.full_name}</h5>
        </div>

        <div className="mb-4">
          <label className="form-label">Select Month</label>
          <select className="form-select" value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)}>
            <option value="">All Months</option>
            <option value="January">January</option>
            <option value="February">February</option>
            <option value="March">March</option>
            <option value="April">April</option>
            <option value="May">May</option>
            <option value="June">June</option>
            <option value="July">July</option>
            <option value="August">August</option>
            <option value="September">September</option>
            <option value="October">October</option>
            <option value="November">November</option>
            <option value="December">December</option>
          </select>
        </div>

        <div className="d-flex gap-3 mb-4 flex-wrap">
          <button className="btn btn-success" onClick={handleExport}>Export Excel Report</button>
          <label className="btn btn-primary">
            Upload Master Sheet (Excel)
            <input type="file" accept=".xlsx,.xls" hidden onChange={handleUpload} />
          </label>
          <button className="btn btn-warning" onClick={() => setShowAddMember(!showAddMember)}>
            {showAddMember ? "Cancel" : "Add New Member"}
          </button>
        </div>

        {showAddMember && (
          <div className="card shadow p-4 mb-4">
            <h4>Add New Member</h4>
            <div className="row">
              <div className="col-md-6 mb-3">
                <label>Full Name</label>
                <input className="form-control" value={newMember.full_name}
                  onChange={(e) => setNewMember({...newMember, full_name: e.target.value})} />
              </div>
              <div className="col-md-6 mb-3">
                <label>Username</label>
                <input className="form-control" value={newMember.username}
                  onChange={(e) => setNewMember({...newMember, username: e.target.value})} />
              </div>
              <div className="col-md-6 mb-3">
                <label>Password</label>
                <input className="form-control" type="password" value={newMember.password}
                  onChange={(e) => setNewMember({...newMember, password: e.target.value})} />
              </div>
              <div className="col-md-6 mb-3">
                <label>Role</label>
                <select className="form-select" value={newMember.role}
                  onChange={(e) => setNewMember({...newMember, role: e.target.value})}>
                  <option value="employee">Employee</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </div>
            <button className="btn btn-success" onClick={handleAddMember}>Save Member</button>
          </div>
        )}

        <div className="row">
          <div className="col-md-4 mb-3">
            <div className="card shadow p-3">
              <h5>Total Employees</h5>
              <h2>{dashboardData?.summary?.total_employees || 0}</h2>
            </div>
          </div>
          <div className="col-md-4 mb-3">
            <div className="card shadow p-3">
              <h5>Total Entries</h5>
              <h2>{dashboardData?.summary?.total_entries || 0}</h2>
            </div>
          </div>
          <div className="col-md-4 mb-3">
            <div className="card shadow p-3">
              <h5>Total Company Profit</h5>
              <h2>₹{dashboardData?.summary?.total_company_profit || 0}</h2>
            </div>
          </div>
        </div>

        <div className="card shadow p-4 mt-4">
          <h3 className="mb-3">Top Performers</h3>
          <table className="table table-bordered table-striped">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Total Entries</th>
                <th>Total Profit</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData.top_performers && dashboardData.top_performers.length > 0 ? (
                dashboardData.top_performers.map((employee, index) => (
                  <tr key={index}>
                    <td>{employee[0]}</td>
                    <td>{employee[1].entries}</td>
                    <td>₹{employee[1].profit}</td>
                  </tr>
                ))
              ) : (
                <tr><td colSpan="3" className="text-center">No Data Found</td></tr>
              )}
            </tbody>
          </table>
        </div>

        <AnalyticsChart topPerformers={dashboardData.top_performers || []} />

        <div className="mt-4">
          <EntriesTable />
        </div>
      </div>
    </Layout>
  );
}

export default AdminDashboard;