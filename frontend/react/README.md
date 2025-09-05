# React FE Placeholder

Use these example calls to integrate with the Flask backend.

```ts
// Example fetch (TypeScript/React)
async function login(email: string, password: string) {
  const res = await fetch("http://localhost:5000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

async function sampleRecs() {
  const res = await fetch("http://localhost:5000/api/recs/sample");
  return res.json();
}
```
