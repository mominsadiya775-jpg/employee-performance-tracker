import { useState } from "react";
import axios from "axios";

function AddEntryForm() {

    const [formData, setFormData] = useState({

        entry_date: "",
        month: "",
        type_of_support: "",

        data_managed_by: "",
        coordination_done_by: "",

        customer_name: "",

        total_receivable: "",

        status: "",

        remarks: ""
    });

    const handleChange = (e) => {

        setFormData({

            ...formData,

            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {

        e.preventDefault();

        try {

            const response = await axios.post(
                "https://employee-performance-tracker-gtez.onrender.com/add-entry",
                formData
            );

            alert(response.data.message);

            // RESET FORM
            setFormData({

                entry_date: "",
                month: "",
                type_of_support: "",

                data_managed_by: "",
                coordination_done_by: "",

                customer_name: "",

                total_receivable: "",

                status: "",

                remarks: ""
            });

        } catch (error) {

            console.log(error);

            alert("Error adding entry");
        }
    };

    return (

        <div className="card shadow p-4 mt-4">

            <h3 className="mb-4">
                Add New Entry
            </h3>

            <form onSubmit={handleSubmit}>

                <div className="row">

                    <div className="col-md-4 mb-3">

                        <label>Date</label>

                        <input
                            type="date"
                            className="form-control"
                            name="entry_date"
                            value={formData.entry_date}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="col-md-4 mb-3">

                        <label>Month</label>

                        <input
                            type="text"
                            className="form-control"
                            name="month"
                            value={formData.month}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="col-md-4 mb-3">

                        <label>Type of Support</label>

                        <input
                            type="text"
                            className="form-control"
                            name="type_of_support"
                            value={formData.type_of_support}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="col-md-6 mb-3">

                        <label>Managed By</label>

                        <input
                            type="text"
                            className="form-control"
                            name="data_managed_by"
                            value={formData.data_managed_by}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="col-md-6 mb-3">

                        <label>Coordination By</label>

                        <input
                            type="text"
                            className="form-control"
                            name="coordination_done_by"
                            value={formData.coordination_done_by}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="col-md-6 mb-3">

                        <label>Customer Name</label>

                        <input
                            type="text"
                            className="form-control"
                            name="customer_name"
                            value={formData.customer_name}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="col-md-6 mb-3">

                        <label>Total Receivable</label>

                        <input
                            type="number"
                            className="form-control"
                            name="total_receivable"
                            value={formData.total_receivable}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="col-md-6 mb-3">

                        <label>Status</label>

                        <input
                            type="text"
                            className="form-control"
                            name="status"
                            value={formData.status}
                            onChange={handleChange}
                        />

                    </div>

                    <div className="col-md-6 mb-3">

                        <label>Remarks</label>

                        <input
                            type="text"
                            className="form-control"
                            name="remarks"
                            value={formData.remarks}
                            onChange={handleChange}
                        />

                    </div>

                </div>

                <button
                    type="submit"
                    className="btn btn-success"
                >
                    Add Entry
                </button>

            </form>

        </div>
    );
}

export default AddEntryForm;