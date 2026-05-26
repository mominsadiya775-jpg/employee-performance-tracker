import { useEffect, useState } from "react";
import Login from "./Login";
import AdminDashboard from "./AdminDashboard";
import EmployeeDashboard from "./EmployeeDashboard";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem("user");

    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }

    setLoading(false);
  }, []);

  const handleSetUser = (userData) => {
    localStorage.setItem(
      "user",
      JSON.stringify(userData)
    );

    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    setUser(null);
  };

  if (loading) {
    return <h2>Loading...</h2>;
  }

  if (!user) {
    return <Login setUser={handleSetUser} />;
  }

  if (user.role === "admin") {
    return (
      <AdminDashboard
        user={user}
        handleLogout={handleLogout}
      />
    );
  }

  return (
    <EmployeeDashboard
      user={user}
      handleLogout={handleLogout}
    />
  );
}

export default App;