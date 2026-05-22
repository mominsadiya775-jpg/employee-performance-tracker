function Layout({ children, user, handleLogout }) {

    return (

        <div className="d-flex">

            {/* SIDEBAR */}

            <div
                className="bg-dark text-white p-3"
                style={{
                    width: "250px",
                    minHeight: "100vh"
                }}
            >

                <h3 className="mb-4">
                    Tracker CRM
                </h3>

                <hr />

                <p>
                    Welcome
                </p>

                <h5>
                    {user.full_name}
                </h5>

                <p>
                    Role: {user.role}
                </p>

                <button
                    className="btn btn-danger mt-3"
                    onClick={handleLogout}
                >
                    Logout
                </button>

            </div>

            {/* MAIN CONTENT */}

            <div
                className="flex-grow-1 p-4 bg-light"
                style={{
                    minHeight: "100vh"
                }}
            >

                {children}

            </div>

        </div>
    );
}

export default Layout;