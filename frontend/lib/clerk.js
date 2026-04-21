export function isClerkEnabled() {
  const key = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || "";
  if (!key) return false;
  if (key.includes("placeholder") || key.includes("your_key_here")) return false;
  return key.startsWith("pk_test_") || key.startsWith("pk_live_");
}
