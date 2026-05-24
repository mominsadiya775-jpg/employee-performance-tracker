import AddEntryForm from "./AddEntryForm";
import EntriesTable from "./EntriesTable";
import Layout from "./Layout";
import AnalyticsChart from "./AnalyticsChart";

import { useEffect, useState } from "react";
import axios from "axios";

function AdminDashboard({ user, handleLogout }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState("");

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(
        `https://employee-performance-tracker-gtez.onrender.com/admin-dashboard?month=${selectedMonth}`
      );

      setDashboardData(response.data);
    } catch (error) {
      console.log("Dashboard Error:", error);
    }
  };

  const handleExport = () => {
    window.open(
      `https://employee-performance-tracker-gtez.onrender.com/export-report?month=${selectedMonth}`
    );
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

          <select
            className="form-select"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
          >
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

        <button
          className="btn btn-success mb-4"
          onClick={handleExport}
        >
          Export Excel Report
        </button>

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
              {dashboardData.top_performers &&
              dashboardData.top_performers.length > 0 ? (
                dashboardData.top_performers.map(
                  (employee, index) => (
                    <tr key={index}>
                      <td>{employee[0]}</td>
                      <td>{employee[1].entries}</td>
                      <td>₹{employee[1].profit}</td>
                    </tr>
                  )
                )
              ) : (
                <tr>
                  <td colSpan="3" className="text-center">
                    No Data Found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <AnalyticsChart
          topPerformers={dashboardData.top_performers || []}
        />

        <div className="mt-4">
          <AddEntryForm />
        </div>

        <div className="mt-4">
          <EntriesTable />
        </div>
      </div>
    </Layout>
  );
}

export default AdminDashboard;