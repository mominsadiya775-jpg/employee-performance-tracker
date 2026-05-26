import { useEffect, useState } from "react";
import Login from "./Login";
import AdminDashboard from "./AdminDashboard";
import EmployeeDashboard from "./EmployeeDashboard";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // LOAD USER + SESSION CHECK
  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    const token = localStorage.getItem("token");

    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    }

    setLoading(false);
  }, []);

  // AUTO LOGOUT AFTER 30 MIN
  useEffect(() => {
    if (!user) return;

    const timer = setTimeout(() => {
      alert("Session expired. Please login again.");

      localStorage.removeItem("user");
      localStorage.removeItem("token");
      sessionStorage.clear();

      setUser(null);

      window.location.href = "/login";
    }, 30 * 60 * 1000);

    return () => clearTimeout(timer);
  }, [user]);

  // LOGIN
  const handleSetUser = (userData) => {
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
  };

  // LOGOUT
  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    sessionStorage.clear();

    setUser(null);

    window.location.href = "/login";
  };

  // APP LOADING
  if (loading) {
    return <h2 className="text-center mt-5">Loading...</h2>;
  }

  // PROTECTED ROUTE
  if (
    !user ||
    !localStorage.getItem("token")
  ) {
    return <Login setUser={handleSetUser} />;
  }

  // ADMIN DASHBOARD
  if (user.role === "admin") {
    return (
      <AdminDashboard
        key={user.id}
        user={user}
        handleLogout={handleLogout}
      />
    );
  }

  // EMPLOYEE DASHBOARD
  return (
    <EmployeeDashboard
      key={user.id}
      user={user}
      handleLogout={handleLogout}
    />
  );
}

export default App;