import { useAuth0 } from "@auth0/auth0-react";
import { Link } from "react-router-dom";

export default function Header() {
  const { loginWithRedirect, logout, isAuthenticated } = useAuth0();

  return (
    <header style={{ display: "flex", gap: "1rem", padding: "1rem" }}>
      <Link to="/">Home</Link>

      {isAuthenticated && (
        <Link to="/investigations">Previous Investigations</Link>
      )}

      {!isAuthenticated ? (
        <button onClick={() => loginWithRedirect()}>Log In</button>
      ) : (
        <button
          onClick={() =>
            logout({ logoutParams: { returnTo: window.location.origin } })
          }
        >
          Log Out
        </button>
      )}
    </header>
  );
}
