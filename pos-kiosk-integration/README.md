# MobyPay POS-KIOSK Integration

Secure TCP communication between a MobyPay Kiosk and any POS terminal — on the **same device**, same LAN, or over the internet. Supports Card, BNPL, DuitNow QR, and IPP payments.

---

## ⚡ 5-Minute Quick Start

> **New here? Start with this.** Connect your POS to the Kiosk and run your first transaction in 5 steps.

### Step 1 — Run the Kiosk server

Requires Python 3.7+. No extra packages needed.

```bash
git clone https://github.com/MobyPayTech/moby-plugins.git
cd moby-plugins/pos-kiosk-integration
python3 kiosk.py
# → Enter port (default 8080): [press Enter]
# → 🚀 Server started on 192.168.1.100:8080
```

### Step 2 — Connect your POS (pick your platform)

**Same device?** Use `127.0.0.1`. **Different device?** Use the IP shown above.

<details>
<summary>🤖 Android (Kotlin)</summary>

```kotlin
val client = MobyPosClient(host = "127.0.0.1") // or "192.168.1.100" for LAN
client.connect()
```

Full example → [Android](#android-kotlin)
</details>

<details>
<summary>🍎 iOS (Swift)</summary>

```swift
let client = MobyPosClient(host: "127.0.0.1") // or "192.168.1.100" for LAN
client.connect { /* on ready */ }
```

Full example → [iOS](#ios--swift)
</details>

<details>
<summary>🪟 Windows / C# (.NET)</summary>

```csharp
using var client = new MobyPosClient(host: "127.0.0.1"); // or "192.168.1.100" for LAN
client.Connect();
```

Full example → [Windows](#windows--c-net)
</details>

<details>
<summary>🐍 Python (testing/scripting)</summary>

```python
import socket, json, hmac, hashlib, uuid
from datetime import datetime

KIOSK_HOST = "127.0.0.1"   # same device
# KIOSK_HOST = "192.168.1.100"  # LAN
KIOSK_PORT = 8080
SECRET     = "POS-KIOSK-SECRET-KEY-2024"  # replace in production
```

Full example → [TESTING.md](TESTING.md#example-pos-test-client)
</details>

### Step 3 — Send a payment request

From the **Kiosk server menu**, select a payment method and enter an amount:

```
📋 Available Commands:
1. 💳 Card Payment       → select 1, enter amount e.g. 25.50
2. 🛒 BNPL              → select 2
3. 📱 DuitNow QR        → select 3
4. 🏦 IPP               → select 4
5. 🚫 Cancel Transaction
```

### Step 4 — Handle the response on your POS

Your POS receives a signed JSON message over TCP and sends back an ACK + result:

```json
// Kiosk → POS: payment request
{ "payload": { "type": "transaction_request", "txn_id": "TXN1705123456789",
               "amount": 25.50, "payment_mode": "card", ... }, "signature": "..." }

// POS → Kiosk: acknowledge
{ "payload": { "type": "ack", "txn_id": "TXN1705123456789", "status": "processing", ... }, "signature": "..." }

// POS → Kiosk: final result
{ "payload": { "type": "transaction_result", "txn_id": "TXN1705123456789",
               "status": "success", "authorization_code": "AUTH123", ... }, "signature": "..." }
```

### Step 5 — Go live checklist

Before deploying to production:

- [ ] Replace `POS-KIOSK-SECRET-KEY-2024` with a securely generated secret (min 32 chars)
- [ ] Enable NTP on both Kiosk and POS devices (clocks must be within 60 seconds)
- [ ] For internet-facing deployments: wrap TCP in TLS or use a VPN
- [ ] For Android: add `INTERNET` permission and network security config for your Kiosk IP
- [ ] Test all payment modes: `card`, `bnpl`, `duitnow_qr`, `ipp`

---

## 📚 Documentation

| Document | What's inside |
|---|---|
| **[QUICKSTART.md](QUICKSTART.md)** | Platform-by-platform setup guide with full working code |
| **[INTEGRATION.md](INTEGRATION.md)** | Full API reference, message formats, security model, architecture |
| **[TESTING.md](TESTING.md)** | Test scenarios, Python POS simulator, troubleshooting |
| **[kiosk.py](kiosk.py)** | Reference Kiosk server implementation |
| **[POS - KIOSK Integration.pdf](POS%20-%20KIOSK%20Integration.pdf)** | Printable technical reference |

---

## ✨ Feature Summary

| Feature | Detail |
|---|---|
| **Protocol** | TCP with newline-delimited JSON |
| **Security** | HMAC-SHA256 signing + nonce + 60s timestamp window |
| **Platforms** | Android, iOS, Windows, Linux, embedded POS |
| **Deployment** | Same-device (127.0.0.1), LAN, or internet |
| **Payment methods** | Card, BNPL, DuitNow QR, IPP |
| **Concurrent POS** | Multiple POS terminals per Kiosk |

---

> ⚠️ Always use a production-grade secret key, NTP-synced clocks, and TLS for internet-facing deployments.
