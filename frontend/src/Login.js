import { useState } from "react";
import axios from "axios";

function Login({ setUser }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!username || !password) {
      alert("Please enter username and password");
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(
        "https://employee-performance-tracker-gtez.onrender.com/login",
        {
          username: username.trim(),
          password: password.trim(),
        }
      );

      console.log("LOGIN RESPONSE:", response.data);

      if (response.data.success) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");

        if (response.data.token) {
          localStorage.setItem("token", response.data.token);
        }

        if (response.data.user) {
          localStorage.setItem("user", JSON.stringify(response.data.user));
          if (setUser) {
            setUser(response.data.user);
          }
        }

      } else {
        alert(response.data.message || "Invalid Credentials");
      }

    } catch (error) {
      console.error("LOGIN ERROR:", error.response?.data || error.message);
      alert(error.response?.data?.message || "Login Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-4">
          <div className="card p-4 shadow">
            <h2 className="text-center mb-4">Login</h2>
            <form onSubmit={handleLogin}>
              <div className="mb-3">
                <label>Username</label>
                <input
                  type="text"
                  className="form-control"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="mb-3">
                <label>Password</label>
                <input
                  type="password"
                  className="form-control"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <button
                type="submit"
                className="btn btn-primary w-100"
                disabled={loading}
              >
                {loading ? "Logging in..." : "Login"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;