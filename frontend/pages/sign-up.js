import { SignUp } from "@clerk/nextjs";
import { isClerkEnabled } from "../lib/clerk";

export default function SignUpPage() {
  if (!isClerkEnabled()) {
    return (
      <main className="container stack gap">
        <div className="card">
          <h2>Clerk Not Configured</h2>
          <p>Add real Clerk keys in `frontend/.env.local` to enable sign-up.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="container stack gap">
      <div className="card">
        <SignUp routing="hash" signInUrl="/sign-in" afterSignUpUrl="/" />
      </div>
    </main>
  );
}
