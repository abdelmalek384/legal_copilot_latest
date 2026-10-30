# Install Legal Copilot on a phone or computer

Legal Copilot can be installed as a Progressive Web App (PWA) from a compatible browser. It remains the same web application and uses the same server, account, firm access controls, and network connection.

## Requirements

- Serve the application over HTTPS. Browsers generally permit service workers on `localhost` for local development.
- Use a current browser that supports web app manifests and service workers.
- Sign in normally after installation. Installation does not create an account or grant access to a firm.

## Installation

- **Android (Chrome):** open the HTTPS application URL, open the browser menu, and choose **Install app** or **Add to Home screen** when offered.
- **Windows/macOS/Linux (supported Chrome or Edge):** open the HTTPS application URL and use the install icon in the address bar or the browser menu's **Install app** action when offered.
- **iPhone/iPad (Safari):** open the HTTPS application URL, use **Share**, choose **Add to Home Screen**, enable **Open as Web App** when offered, then tap **Add**. A dedicated 180×180 PNG home-screen icon is supplied; available options and icon rendering still vary by iOS version, so confirm on the target device.

## Offline and privacy behavior

The service worker caches only the static bilingual offline notice. It does **not** cache the application HTML, API responses, authentication/session data, case records, uploaded files, legal research, or other firm data. When the network is unavailable, the app root displays the offline notice; the application is not an offline case-management client.

The app's normal response policy remains `Cache-Control: no-store`. The service worker only handles a top-level `GET /` navigation and otherwise leaves requests to the network. Do not loosen these boundaries to make matter data available offline without a separate security and privacy design review.

## Verification still required

Automated contract tests verify the manifest metadata, service-worker scope, and cache boundary. They do not prove installation UX or icon rendering on every browser/device. Before release, record manual installation and offline-fallback results on at least one Android device, one iPhone/iPad if supported, and one desktop browser.
