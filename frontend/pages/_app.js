import { ClerkProvider } from "@clerk/nextjs";
import { isClerkEnabled } from "../lib/clerk";
import "../styles/globals.css";

const clerkEnabled = isClerkEnabled();

export default function App({ Component, pageProps }) {
  if (!clerkEnabled) {
    return <Component {...pageProps} />;
  }

  return (
    <ClerkProvider {...pageProps}>
      <Component {...pageProps} />
    </ClerkProvider>
  );
}
