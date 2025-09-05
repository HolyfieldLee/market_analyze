# SwiftUI FE Placeholder

Use URLSession to call the Flask backend.

```swift
struct LoginPayload: Codable { let email: String; let password: String }
struct TokenResponse: Codable { let access_token: String }

func login(email: String, password: String) async throws -> TokenResponse {
    let url = URL(string: "http://localhost:5000/api/auth/login")!
    var req = URLRequest(url: url)
    req.httpMethod = "POST"
    req.addValue("application/json", forHTTPHeaderField: "Content-Type")
    req.httpBody = try JSONEncoder().encode(LoginPayload(email: email, password: password))
    let (data, _) = try await URLSession.shared.data(for: req)
    return try JSONDecoder().decode(TokenResponse.self, from: data)
}
```
