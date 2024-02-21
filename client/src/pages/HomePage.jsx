import { useAuth } from "../context/auth";
import { Link } from "react-router-dom";
import LogoutButton from "../components/LogoutButton";

const HomePage = () => {
  const [auth] = useAuth();

  return (
    <div>
      HomePage
      <pre>{JSON.stringify(auth, null, 4)}</pre>
      {auth.token ? <LogoutButton /> : <Link to="/login">Login</Link>}

      {auth?.user?.role === "user" ? (
        <button className="bg-blue-500 text-white rounded py-2 px-4 mx-4">
          <Link to="/user-upload">User</Link>
        </button>
      ) : (
        <></>
      )}

      {auth?.user?.role === "admin" ? (
        <button className="bg-blue-500 text-white rounded py-2 px-4 mx-4">
          <Link to="/admin-saves">Admin</Link>
        </button>
      ) : (
        <></>
      )}
    </div>
  );
};

export default HomePage;
