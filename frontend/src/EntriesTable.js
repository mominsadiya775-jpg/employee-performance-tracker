import { useEffect, useState } from "react";
import axios from "axios";

function EntriesTable() {

    // =========================
    // STATES
    // =========================

    const [entries, setEntries] = useState([]);

    const [search, setSearch] = useState("");


    // =========================
    // FETCH ENTRIES
    // =========================

    const fetchEntries = async () => {

        try {

            const response = await axios.get(
                "http://127.0.0.1:5000/all-entries"
            );

            setEntries(response.data.entries);

        } catch (error) {

            console.log(error);

        }
    };


    // =========================
    // LOAD DATA
    // =========================

    useEffect(() => {

        fetchEntries();

    }, []);


    // =========================
    // DELETE FUNCTION
    // =========================

    const handleDelete = async (id) => {

        const confirmDelete = window.confirm(
            "Are you sure you want to delete?"
        );

        if (!confirmDelete) {

            return;
        }

        try {

            await axios.delete(
                `http://127.0.0.1:5000/delete-entry/${id}`
            );

            alert("Entry deleted successfully");

            fetchEntries();

        } catch (error) {

            console.log(error);

        }
    };


    // =========================
    // EDIT FUNCTION
    // =========================

    const handleEdit = async (entry) => {

        const customer_name = prompt(
            "Enter customer name",
            entry.customer_name
        );

        const total_receivable = prompt(
            "Enter receivable amount",
            entry.total_receivable
        );

        const status = prompt(
            "Enter status",
            entry.status
        );

        if (
            !customer_name ||
            !total_receivable ||
            !status
        ) {

            return;
        }

        try {

            await axios.put(
                `http://127.0.0.1:5000/update-entry/${entry.id}`,
                {
                    customer_name,
                    total_receivable,
                    status
                }
            );

            alert("Entry updated successfully");

            fetchEntries();

        } catch (error) {

            console.log(error);

        }
    };


    // =========================
    // FILTERED DATA
    // =========================

    const filteredEntries = entries.filter((entry) =>

        (entry.customer_name || "")
            .toLowerCase()
            .includes(search.toLowerCase())

    );


    // =========================
    // UI
    // =========================

    return (

        <div className="card shadow p-4 mt-4">

            <h3 className="mb-3">
                All Entries
            </h3>


            {/* SEARCH */}

            <input
                type="text"
                className="form-control mb-3"
                placeholder="Search Customer..."
                value={search}
                onChange={(e) =>
                    setSearch(e.target.value)
                }
            />


            {/* TABLE */}

            <table className="table table-bordered table-striped">

                <thead>

                    <tr>

                        <th>ID</th>

                        <th>Date</th>

                        <th>Month</th>

                        <th>Customer</th>

                        <th>Manager</th>

                        <th>Coordinator</th>

                        <th>Receivable</th>

                        <th>Status</th>

                        <th>Actions</th>

                    </tr>

                </thead>

                <tbody>

                    {
                        filteredEntries.length > 0 ? (

                            filteredEntries.map((entry) => (

                                <tr key={entry.id}>

                                    <td>
                                        {entry.id}
                                    </td>

                                    <td>
                                        {entry.entry_date}
                                    </td>

                                    <td>
                                        {entry.month}
                                    </td>

                                    <td>
                                        {entry.customer_name}
                                    </td>

                                    <td>
                                        {entry.data_managed_by}
                                    </td>

                                    <td>
                                        {entry.coordination_done_by}
                                    </td>

                                    <td>
                                        ₹{entry.total_receivable}
                                    </td>

                                    <td>
                                        {entry.status}
                                    </td>

                                    <td>

                                        <button
                                            className="btn btn-primary btn-sm me-2"
                                            onClick={() =>
                                                handleEdit(entry)
                                            }
                                        >
                                            Edit
                                        </button>

                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() =>
                                                handleDelete(entry.id)
                                            }
                                        >
                                            Delete
                                        </button>

                                    </td>

                                </tr>

                            ))

                        ) : (

                            <tr>

                                <td
                                    colSpan="9"
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
    );
}

export default EntriesTable;