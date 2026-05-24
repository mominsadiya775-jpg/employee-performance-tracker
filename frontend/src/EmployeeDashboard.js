import { useEffect, useState } from "react";
import axios from "axios";

function EmployeeDashboard({ user, handleLogout }) {

    // =====================================
    // STATES
    // =====================================

    const [dashboardData, setDashboardData] = useState(null);

    const [selectedMonth, setSelectedMonth] = useState("");

    const [loading, setLoading] = useState(true);


    // =====================================
    // FETCH DASHBOARD
    // =====================================

    const fetchDashboard = async () => {

        try {

            setLoading(true);

            const response = await axios.get(
                `https://employee-performance-tracker-gtez.onrender.com/employee-dashboard/${encodeURIComponent(user.full_name)}?month=${selectedMonth}`
            );

            console.log("Dashboard Response:", response.data);

            if (response.data.success) {

                setDashboardData(response.data.dashboard);

            } else {

                setDashboardData({
                    total_entries: 0,
                    solo_entries: 0,
                    shared_entries: 0,
                    total_profit: 0,
                    entries: []
                });
            }

        } catch (error) {

            console.log("Dashboard Error:", error);

            setDashboardData({
                total_entries: 0,
                solo_entries: 0,
                shared_entries: 0,
                total_profit: 0,
                entries: []
            });

        } finally {

            setLoading(false);
        }
    };


    // =====================================
    // USE EFFECT
    // =====================================

    useEffect(() => {

        if (user && user.full_name) {

            fetchDashboard();
        }

    }, [selectedMonth, user]);


    // =====================================
    // LOADING SCREEN
    // =====================================

    if (loading) {

        return (

            <div className="container mt-5 text-center">

                <h2>
                    Loading Dashboard...
                </h2>

            </div>
        );
    }


    // =====================================
    // FALLBACK
    // =====================================

    if (!dashboardData) {

        return (

            <div className="container mt-5 text-center">

                <h2>
                    No Dashboard Data Found
                </h2>

            </div>
        );
    }


    // =====================================
    // UI
    // =====================================

    return (

        <div className="container mt-4">

            {/* HEADER */}

            <div className="d-flex justify-content-between align-items-center mb-4">

                <div>

                    <h1>
                        Employee Dashboard
                    </h1>

                    <h5>
                        Welcome, {user.full_name}
                    </h5>

                </div>

                <button
                    className="btn btn-danger"
                    onClick={handleLogout}
                >
                    Logout
                </button>

            </div>


            {/* MONTH FILTER */}

            <div className="mb-4">

                <label className="form-label">
                    Select Month
                </label>

                <select
                    className="form-select"
                    value={selectedMonth}
                    onChange={(e) =>
                        setSelectedMonth(e.target.value)
                    }
                >

                    <option value="">
                        All Months
                    </option>

                    <option value="January">
                        January
                    </option>

                    <option value="February">
                        February
                    </option>

                    <option value="March">
                        March
                    </option>

                    <option value="April">
                        April
                    </option>

                    <option value="May">
                        May
                    </option>

                    <option value="June">
                        June
                    </option>

                    <option value="July">
                        July
                    </option>

                    <option value="August">
                        August
                    </option>

                    <option value="September">
                        September
                    </option>

                    <option value="October">
                        October
                    </option>

                    <option value="November">
                        November
                    </option>

                    <option value="December">
                        December
                    </option>

                </select>

            </div>


            {/* SUMMARY CARDS */}

            <div className="row">

                {/* TOTAL ENTRIES */}

                <div className="col-md-3 mb-3">

                    <div className="card shadow p-3">

                        <h6>
                            Total Entries
                        </h6>

                        <h3>
                            {dashboardData.total_entries}
                        </h3>

                    </div>

                </div>


                {/* SOLO ENTRIES */}

                <div className="col-md-3 mb-3">

                    <div className="card shadow p-3">

                        <h6>
                            Solo Entries
                        </h6>

                        <h3>
                            {dashboardData.solo_entries}
                        </h3>

                    </div>

                </div>


                {/* SHARED ENTRIES */}

                <div className="col-md-3 mb-3">

                    <div className="card shadow p-3">

                        <h6>
                            Shared Entries
                        </h6>

                        <h3>
                            {dashboardData.shared_entries}
                        </h3>

                    </div>

                </div>


                {/* TOTAL PROFIT */}

                <div className="col-md-3 mb-3">

                    <div className="card shadow p-3">

                        <h6>
                            Total Profit
                        </h6>

                        <h3>
                            ₹{dashboardData.total_profit}
                        </h3>

                    </div>

                </div>

            </div>


            {/* RECENT ENTRIES TABLE */}

            <div className="card shadow p-4 mt-4">

                <h3 className="mb-3">
                    Recent Entries
                </h3>

                <table className="table table-bordered table-striped">

                    <thead>

                        <tr>

                            <th>
                                Customer
                            </th>

                            <th>
                                Entry Type
                            </th>

                            <th>
                                Profit Share
                            </th>

                            <th>
                                Status
                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {
                            dashboardData.entries &&
                            dashboardData.entries.length > 0 ? (

                                dashboardData.entries.map(
                                    (entry, index) => (

                                        <tr key={index}>

                                            <td>
                                                {entry.customer_name}
                                            </td>

                                            <td>
                                                {entry.entry_type}
                                            </td>

                                            <td>
                                                ₹{entry.profit_share}
                                            </td>

                                            <td>
                                                {entry.status}
                                            </td>

                                        </tr>
                                    )
                                )

                            ) : (

                                <tr>

                                    <td
                                        colSpan="4"
                                        className="text-center"
                                    >

                                        No Entries Found

                                    </td>

                                </tr>
                            )
                        }

                    </tbody>

                </table>

            </div>

        </div>
    );
}

export default EmployeeDashboard;