// ProtectedPreviousReports.jsx
import { withAuthenticationRequired } from "@auth0/auth0-react";
import PreviousReports from "./PreviousReports.jsx";

export default withAuthenticationRequired(PreviousReports, {
  onRedirecting: () => <p>Redirecting to login…</p>,
});
