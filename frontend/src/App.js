import { useEffect, useState } from "react";

import Login from "./Login";

import AdminDashboard from "./AdminDashboard";

import EmployeeDashboard from "./EmployeeDashboard";

function App() {

    const [user, setUser] = useState(null);

    // LOAD USER FROM LOCAL STORAGE
    useEffect(() => {

        const savedUser = localStorage.getItem("user");

        if (savedUser) {

            setUser(JSON.parse(savedUser));
        }

    }, []);

    // SAVE USER TO LOCAL STORAGE
    const handleSetUser = (userData) => {

        localStorage.setItem(
            "user",
            JSON.stringify(userData)
        );

        setUser(userData);
    };

    // LOGOUT
    const handleLogout = () => {

        localStorage.removeItem("user");

        setUser(null);
    };

    // LOGIN PAGE
    if (!user) {

        return <Login setUser={handleSetUser} />;
    }

    // ADMIN
    if (user.role === "admin") {

        return (
            <AdminDashboard
                user={user}
                handleLogout={handleLogout}
            />
        );
    }

    // EMPLOYEE
    return (
        <EmployeeDashboard
            user={user}
            handleLogout={handleLogout}
        />
    );
}

export default App;