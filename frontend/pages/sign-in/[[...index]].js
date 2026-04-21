import { SignIn } from "@clerk/nextjs";
import { isClerkEnabled } from "../../lib/clerk";

export default function Page() {
  if (!isClerkEnabled()) {
    return (
      <main className="container stack gap">
        <div className="card">
          <h2>Clerk Not Configured</h2>
          <p>Add real Clerk keys in `frontend/.env.local` to enable sign-in.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="container stack gap">
      <div className="card">
        <SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" afterSignInUrl="/" />
      </div>
    </main>
  );
}
