import { useEffect, useState } from "react";
import axios from "axios";

const API = "https://employee-performance-tracker-gtez.onrender.com";

function EntriesTable() {
  const [entries, setEntries] = useState([]);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState("");

  const fetchEntries = async () => {
    try {
      const response = await axios.get(`${API}/all-entries`);
      setEntries(response.data.entries);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure?")) return;
    try {
      await axios.delete(`${API}/delete-entry/${id}`);
      alert("Deleted!");
      fetchEntries();
    } catch (error) {
      console.log(error);
    }
  };

  const ALL_EMPLOYEES = [
    "Ibrahim Hawai", "Asha Madam", "Shabnam Shaikh",
    "Aman Shaikh", "Ayan Shaikh", "Rubeena Shaikh",
    "Simran Rawat", "Musab Pathan", "Abdul Rehman"
  ];

  const filteredEntries = entries.filter((entry) => {
    const monthMatch = selectedMonth === "" || entry.month === selectedMonth;
    const empMatch = selectedEmployee === "" || 
      (entry.data_managed_by && entry.data_managed_by.includes(selectedEmployee.split(" ")[0]));
    return monthMatch && empMatch;
  });

  return (
    <div className="card shadow p-4 mt-4">
      <h3 className="mb-3">All Entries</h3>

      <div className="d-flex gap-3 mb-3 flex-wrap">
        <select className="form-select w-auto" value={selectedMonth}
          onChange={(e) => setSelectedMonth(e.target.value)}>
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

        <select className="form-select w-auto" value={selectedEmployee}
          onChange={(e) => setSelectedEmployee(e.target.value)}>
          <option value="">All Employees</option>
          <option value="Ibrahim Hawai">Ibrahim Hawai</option>
          <option value="Shabnam Shaikh">Shabnam Shaikh</option>
          <option value="Ayan Shaikh">Ayan Shaikh</option>
          <option value="Aman Shaikh">Aman Shaikh</option>
          <option value="Asha Madam">Asha Madam</option>
          <option value="Rubeena Shaikh">Rubeena Shaikh</option>
          <option value="Simran Rawat">Simran Rawat</option>
          <option value="Musab Pathan">Musab Pathan</option>
          <option value="Abdul Rehman">Abdul Rehman</option>
        </select>

        <button className="btn btn-secondary" onClick={() => { setSelectedMonth(""); setSelectedEmployee(""); }}>
          Clear Filter
        </button>
      </div>

      <div style={{overflowX: "auto"}}>
        <table className="table table-bordered table-striped">
          <thead>
            <tr>
              <th>Ref No</th>
              <th>Date</th>
              <th>Month</th>
              <th>Customer</th>
              <th>Manager</th>
              <th>Help Taken From</th>
              <th>Receivable</th>
              <th>Payable</th>
              <th>Profit</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredEntries.length > 0 ? (
              filteredEntries.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.reference_no || entry.id}</td>
                  <td>{entry.entry_date}</td>
                  <td>{entry.month}</td>
                  <td>{entry.customer_name}</td>
                  <td>{entry.data_managed_by}</td>
                  <td>{entry.coordination_done_by}</td>
                  <td>₹{Number(entry.total_receivable).toFixed(2)}</td>
                  <td>₹{Number(entry.total_payable).toFixed(2)}</td>
                  <td>₹{Number(entry.profit).toFixed(2)}</td>
                  <td>{entry.status}</td>
                  <td>
                    <button className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(entry.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="11" className="text-center">No Entries Found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default EntriesTable;