import { useEffect, useState } from "react";
import Login from "./Login";
import AdminDashboard from "./AdminDashboard";
import EmployeeDashboard from "./EmployeeDashboard";

function App() {

    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // LOAD USER
    useEffect(() => {

        const savedUser = localStorage.getItem("user");

        if (savedUser) {
            setUser(JSON.parse(savedUser));
        }

        setLoading(false);

    }, []);

    // LOGIN
    const handleSetUser = (userData) => {

        localStorage.removeItem("user");

        localStorage.setItem(
            "user",
            JSON.stringify(userData)
        );

        setUser(null);

        setTimeout(() => {
            setUser(userData);
        }, 100);
    };

    // LOGOUT
    const handleLogout = () => {

        localStorage.removeItem("user");

        setUser(null);

        window.location.reload();
    };

    // APP LOADING
    if (loading) {
        return <h2 className="text-center mt-5">Loading...</h2>;
    }

    // LOGIN SCREEN
    if (!user) {
        return <Login setUser={handleSetUser} />;
    }

    // ADMIN
    if (user.role === "admin") {
        return (
            <AdminDashboard
                key={user.id}
                user={user}
                handleLogout={handleLogout}
            />
        );
    }

    // EMPLOYEE
    return (
        <EmployeeDashboard
            key={user.id}
            user={user}
            handleLogout={handleLogout}
        />
    );
}

export default App;