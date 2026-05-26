import { useEffect, useState } from "react";
import axios from "axios";

const API = "https://employee-performance-tracker-gtez.onrender.com";

function EmployeeDashboard({ user, handleLogout }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${API}/employee-dashboard?username=${user.username}&month=${selectedMonth}`
      );
      if (response.data.success) {
        setDashboardData({
          total_entries: response.data.summary.total_entries,
          solo_entries: response.data.summary.solo_entries,
          shared_entries: response.data.summary.shared_entries,
          total_profit: response.data.summary.total_profit,
          entries: response.data.entries
        });
      } else {
        setDashboardData({ total_entries: 0, solo_entries: 0, shared_entries: 0, total_profit: 0, entries: [] });
      }
    } catch (error) {
      console.log("Dashboard Error:", error);
      setDashboardData({ total_entries: 0, solo_entries: 0, shared_entries: 0, total_profit: 0, entries: [] });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user && user.username) fetchDashboard();
  }, [selectedMonth, user]);

  if (loading) return <div className="container mt-5 text-center"><h2>Loading...</h2></div>;
  if (!dashboardData) return <div className="container mt-5 text-center"><h2>No Data Found</h2></div>;

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Employee Dashboard</h1>
          <h5>Welcome, {user.full_name}</h5>
        </div>
        <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
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

      <div className="row">
        <div className="col-md-3 mb-3">
          <div className="card shadow p-3">
            <h6>Total Entries</h6>
            <h3>{dashboardData.total_entries}</h3>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card shadow p-3">
            <h6>Solo Entries</h6>
            <h3>{dashboardData.solo_entries}</h3>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card shadow p-3">
            <h6>Shared Entries</h6>
            <h3>{dashboardData.shared_entries}</h3>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card shadow p-3">
            <h6>Total Profit</h6>
            <h3>₹{dashboardData.total_profit}</h3>
          </div>
        </div>
      </div>

      <div className="card shadow p-4 mt-4">
        <h3 className="mb-3">Recent Entries</h3>
        <table className="table table-bordered table-striped">
          <thead>
            <tr>
              <th>Customer</th>
              <th>Month</th>
              <th>Entry Type</th>
              <th>Profit Share</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {dashboardData.entries && dashboardData.entries.length > 0 ? (
              dashboardData.entries.map((entry, index) => (
                <tr key={index}>
                  <td>{entry.customer}</td>
                  <td>{entry.month}</td>
                  <td>{entry.entry_type}</td>
                  <td>₹{entry.profit_share}</td>
                  <td>{entry.status}</td>
                </tr>
              ))
            ) : (
              <tr><td colSpan="5" className="text-center">No Entries Found</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default EmployeeDashboard;