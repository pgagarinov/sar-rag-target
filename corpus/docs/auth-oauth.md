# FluxAPI Authentication: OAuth 2.0

FluxAPI supports OAuth 2.0 for delegated authorization. Use OAuth when third-party applications need to access FluxAPI resources on behalf of users. OAuth tokens are scoped, time-limited, and revocable.

## Supported OAuth Flows

FluxAPI supports three OAuth 2.0 flows: Authorization Code (with PKCE), Client Credentials, and Device Authorization. The Authorization Code flow with PKCE is recommended for user-facing applications including web apps, mobile apps, and CLI tools. Use Client Credentials for server-to-server communication where no user context is needed. Device Authorization is for input-constrained devices like IoT hardware. All flows use the authorization server at `https://auth.fluxapi.io`. Register your application at **Settings > OAuth Apps** to obtain a client ID and client secret.

## Authorization Code with PKCE

For browser-based and mobile applications, use Authorization Code with PKCE (Proof Key for Code Exchange). PKCE prevents authorization code interception attacks and eliminates the need to store client secrets on public clients. Flow steps: (1) Generate a random code verifier (43-128 chars) and compute SHA-256 code challenge. (2) Redirect user to `GET /oauth/authorize` with `response_type=code`, `client_id`, `redirect_uri`, `code_challenge`, `code_challenge_method=S256`, and `scope`. (3) User authenticates and grants consent. (4) FluxAPI redirects back with an authorization code. (5) Exchange the code for tokens via `POST /oauth/token` with `grant_type=authorization_code`, the authorization code, and the code verifier. The response includes an access token (valid 1 hour), a refresh token (valid 30 days), and token metadata.

## Client Credentials Flow

For machine-to-machine authentication, use the Client Credentials flow. This is ideal for backend services, cron jobs, and automated pipelines that act as their own identity rather than on behalf of a user. Send `POST /oauth/token` with `grant_type=client_credentials`, `client_id`, `client_secret`, and `scope`. The response includes only an access token (no refresh token). Access tokens issued via client credentials are valid for 1 hour. To maintain continuous access, request a new token before the current one expires.

## Token Refresh and Revocation

Refresh tokens allow obtaining new access tokens without re-authentication. Send `POST /oauth/token` with `grant_type=refresh_token` and the refresh token value. Each refresh rotates the refresh token — the old refresh token is invalidated and a new one is issued. Refresh tokens expire after 30 days of inactivity. Revoke tokens via `POST /oauth/revoke` with the token value. Revoking a refresh token also invalidates all associated access tokens.
