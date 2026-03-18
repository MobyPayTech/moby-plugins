# MobyPay POS-KIOSK Integration

Secure TCP communication system for integrating MobyPay Kiosk with POS terminals. Supports card payments, Buy Now Pay Later (BNPL), DuitNow QR, and Installment Payment Plans (IPP).

> **Universal Deployment:** The same protocol works whether your Kiosk and POS are on the **same device**, on the **same LAN**, or connected over the **internet**. Only the IP address changes.

---

## 📚 Documentation

- **[INTEGRATION.md](INTEGRATION.md)** — API specs, system architecture, security model, same-device vs remote deployment, and platform code examples (Android, iOS, Windows)
- **[TESTING.md](TESTING.md)** — Installation, testing procedures for all deployment scenarios, and a complete Python POS test client
- **[kiosk.py](kiosk.py)** — Reference implementation (TCP server with interactive menu)
- **[POS - KIOSK Integration.pdf](POS%20-%20KIOSK%20Integration.pdf)** — Detailed technical reference

---

## ✨ Features

- **Universal TCP protocol** — identical on same-device, LAN, and internet deployments
- **Cross-platform** — Windows, Android, iOS, Linux, and embedded POS systems
- **Secure messaging** — HMAC-SHA256 signing and nonce validation
- **Multiple payment methods** — Card, BNPL, DuitNow QR, and IPP
- **Real-time transaction processing**
- **Replay attack protection** — 60-second timestamp validation + nonce tracking
- **Multiple concurrent POS connections**
- **IPP plan selection** with installment details

---

## 🚀 Quick Start

| I want to... | Start here |
|---|---|
| Understand the architecture & API | [INTEGRATION.md](INTEGRATION.md) |
| Test the integration on my machine | [TESTING.md](TESTING.md) |
| Integrate from Android / iOS / Windows | [INTEGRATION.md → Platform Examples](INTEGRATION.md#platform-integration-examples) |

---

> ⚠️ This is a secure payment integration. Always use a production-grade secret key, synchronized clocks (NTP), and TLS for internet-facing deployments.
