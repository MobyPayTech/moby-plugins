# MobyPay POS-KIOSK Integration — API Reference

> 🚀 **New to this integration?** Start with **[QUICKSTART.md](QUICKSTART.md)** — get a working POS connection on any platform in under 5 minutes, with full copy-paste code for Android, iOS, and Windows.
>
> This document is the **complete API reference** covering all message formats, security model, and architecture details.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Same Device vs Different Device](#same-device-vs-different-device)
- [Security Architecture](#security-architecture)
- [System Architecture](#system-architecture)
- [Payment Methods](#payment-methods)
- [API Documentation](#api-documentation)
- [Integration Workflow](#integration-workflow)
- [Network Configuration](#network-configuration)

---

## Overview

The MobyPay POS-KIOSK integration enables secure TCP-based communication between kiosk terminals and Point of Sale (POS) systems. The system supports multiple payment methods including card payments, Buy Now Pay Later (BNPL), DuitNow QR, and Installment Payment Plans (IPP).

**The protocol is identical regardless of whether the Kiosk and POS are on the same physical device or on different devices connected over a network.** The only difference is the IP address used to connect:

| Scenario | Kiosk IP to use |
|---|---|
| Same device (co-located) | `127.0.0.1` (localhost) |
| Different devices, same LAN | Local IP, e.g. `192.168.1.100` |
| Different devices, over internet | Public IP or hostname, e.g. `pos.merchant.com` |

### Key Features

- **Universal TCP Communication:** Works on same-device, LAN, and internet-connected deployments
- **Cross-Platform:** Compatible with Windows, Android, iOS, Linux, and embedded POS systems
- **Secure Messaging:** HMAC-SHA256 message signing with nonce validation
- **Multiple Payment Methods:** Card, BNPL, DuitNow QR, and IPP support
- **Real-time Processing:** Instant communication between Kiosk and POS
- **Replay Attack Protection:** Nonce-based security prevents message replay
- **Timestamp Validation:** 60-second window validation

---

## Same Device vs Different Device

### The Golden Rule

The TCP protocol and all message formats are **100% identical** whether the apps are on the same device or different devices. Only the connection target IP changes.

```
POS Client  ──────────────────────────────→  Kiosk Server (TCP listener)

Same device:   connect("127.0.0.1", 8080)
Same LAN:      connect("192.168.1.100", 8080)
Internet:      connect("pos.merchant.com", 8080)
```

### Same Device Deployment

When the MobyPay Kiosk app and the POS app run on the **same device** (Android, Windows, etc.), the POS client should connect to `127.0.0.1` (localhost) on the configured port. No network infrastructure is required.

```
Single Device
┌──────────────────────────────────────────┐
│  [Kiosk App]  ←── TCP ──→  [POS App]   │
│  listens on 127.0.0.1:8080               │
└──────────────────────────────────────────┘
```

> **Android:** Even for localhost TCP connections, the app must declare `<uses-permission android:name="android.permission.INTERNET" />` in `AndroidManifest.xml`.

> **iOS:** Localhost TCP is supported via the `Network` framework. For App Store distribution, ensure background network entitlements are configured. For enterprise/kiosk deployments no additional steps are needed.

### Different Device Deployment (LAN or Internet)

When Kiosk and POS are on different devices, the POS connects to the Kiosk's IP address or hostname.

```
LAN:
[POS Terminal @ 192.168.1.50]  ──→  [Kiosk @ 192.168.1.100:8080]

Internet:
[POS Terminal]  ──→  [Kiosk @ public-ip-or-hostname:8080]
```

Ensure:
1. The Kiosk device has a **static or reserved IP** (LAN) or stable hostname/public IP (internet).
2. **Port 8080** (or your configured port) is open and reachable from the POS device.
3. For internet-facing deployments, **wrap the TCP connection in TLS/SSL** or use a VPN — raw TCP over the public internet is not encrypted by default.

---

## 🔒 Security Architecture

### Message Signing

All messages are signed using HMAC-SHA256. The signature is calculated over the payload JSON after:

- Sorting keys alphabetically
- Using compact separators (`,` for array/object elements, `:` for key-value pairs)
- Encoding with UTF-8

> ⚠️ **Production Security Warning:** The shared secret `POS-KIOSK-SECRET-KEY-2024` is for **development and testing only**. In production, replace it with a securely generated random string (minimum 32 characters) and distribute it to POS terminals out-of-band (never transmit it over the TCP channel itself). Rotate the key periodically.

### Nonce Validation

- Unique nonce (UUID v4) is included in every message
- Each nonce can only be used once (prevents replay attacks)
- Nonces are tracked server-side; old nonces are cleared periodically

> ⚠️ **Production Note:** The default in-memory nonce store clears after 1,000 entries. For high-volume production environments, use a persistent nonce store (e.g., Redis with 60-second TTL) to prevent replay attacks under load.

### Timestamp Validation

- Timestamps are in milliseconds since epoch
- Requests must be within a 60-second window from current time
- Protects against time-shifted replay attacks
- **Ensure device clocks are synchronized** via NTP on both Kiosk and POS devices

### Validation Sequence

1. Verify message structure (payload and signature present)
2. Verify HMAC-SHA256 signature matches
3. Validate nonce uniqueness
4. Validate timestamp within acceptable range

---

## 🏗 System Architecture

```
┌─────────────────┐                    ┌─────────────────┐
│   Kiosk App     │  ←── TCP ──────→  │   POS Terminal  │
│   (TCP Server)  │  (port 8080)       │   (TCP Client)  │
│                 │                    │                  │
│ - TCP Listener  │                    │ - TCP Connector  │
│ - Msg Sender    │                    │ - Msg Parser     │
│ - Resp Handler  │                    │ - Txn Processor  │
│ - IPP Handler   │                    │ - Plan Provider  │
└─────────────────┘                    └─────────────────┘
       ▲
       │ Connect to 127.0.0.1:8080 (same device)
       │           OR
       │ Connect to <kiosk-ip>:8080 (different device)
```

### Component Responsibilities

**Kiosk (TCP Server):**
- Listen for incoming POS connections on configured port
- Send payment requests to connected POS terminals
- Receive and process transaction responses
- Manage multiple concurrent POS connections
- Handle IPP plan selection flow

**POS Terminal (TCP Client):**
- Connect to Kiosk server (127.0.0.1 for same-device, or IP/hostname for remote)
- Receive payment requests
- Process transactions through the payment hardware/SDK
- Send ACK and transaction result messages
- Provide IPP plan options when applicable

---

## 💳 Payment Methods

| Payment Mode | Description |
|---|---|
| `card` | Direct card-present transaction — credit and debit with real-time authorization |
| `bnpl` | Buy Now Pay Later — installment-based, flexible terms, instant approval |
| `duitnow_qr` | DuitNow QR — Malaysia national QR payment, bank and e-wallet integration |
| `ipp` | Installment Payment Plans — available for MobyPay BNPL holders, interactive plan selection |

---

## 📡 API Documentation

### Message Framing

All messages use **newline-delimited JSON**. Each message is a single JSON object followed by a newline character (`\n`). This newline is the message frame delimiter and **must always be appended** when sending, and read with a `readLine()`-style call on the receiver.

```
<JSON object>\n
```

### Message Envelope

All messages (both directions) use this signed envelope structure:

```json
{
  "payload": {
    "type": "message_type",
    "txn_id": "unique-transaction-id",
    "timestamp": "milliseconds-since-epoch",
    "nonce": "uuid-v4-string",
    "kiosk_id": "KIOSK001"
  },
  "signature": "hmac-sha256-hex-digest"
}
```

> The `signature` is computed over the `payload` object only — keys sorted alphabetically, compact separators (`,` and `:`), UTF-8 encoded. See [QUICKSTART.md](QUICKSTART.md) for per-platform signing code.

---

### Request Types (Kiosk → POS)

#### 1. Transaction Request

Initiates a payment. Sent by the Kiosk when the operator triggers a payment.

```json
{
  "payload": {
    "type": "transaction_request",
    "txn_id": "TXN1705123456789",
    "amount": 50.00,
    "payment_mode": "card",
    "kiosk_id": "KIOSK001",
    "timestamp": "1705123456789",
    "nonce": "550e8400-e29b-41d4-a716-446655440000"
  },
  "signature": "a1b2c3d4e5f6..."
}
```

| Field | Type | Description |
|---|---|---|
| `txn_id` | string | Unique transaction ID — format: `TXN` + epoch milliseconds |
| `amount` | number | Transaction amount in RM |
| `payment_mode` | string | One of: `card`, `bnpl`, `duitnow_qr`, `ipp` |
| `kiosk_id` | string | Identifier of the Kiosk terminal |
| `timestamp` | string | Milliseconds since epoch (string) |
| `nonce` | string | UUID v4, unique per message |

#### 2. Cancel Transaction

Cancels an in-progress transaction. POS must ACK and abort any in-flight hardware operation.

```json
{
  "payload": {
    "type": "cancel_transaction",
    "txn_id": "TXN1705123456789",
    "kiosk_id": "KIOSK001",
    "timestamp": "1705123456789",
    "nonce": "550e8400-e29b-41d4-a716-446655440000"
  },
  "signature": "a1b2c3d4e5f6..."
}
```

#### 3. IPP Plan Selection

Sent by Kiosk after the user selects an installment plan from the options provided by the POS.

```json
{
  "payload": {
    "type": "ipp_plan_selection",
    "txn_id": "TXN1705123456789",
    "plan_id": "IPP_3M",
    "kiosk_id": "KIOSK001",
    "timestamp": "1705123456789",
    "nonce": "550e8400-e29b-41d4-a716-446655440000"
  },
  "signature": "a1b2c3d4e5f6..."
}
```

---

### Response Types (POS → Kiosk)

#### 1. Acknowledgment (ACK)

Sent immediately by POS upon receiving any request. Confirms receipt before processing begins.

```json
{
  "payload": {
    "type": "ack",
    "txn_id": "TXN1705123456789",
    "status": "processing",
    "timestamp": "1705123456789",
    "nonce": "550e8400-e29b-41d4-a716-446655440000"
  },
  "signature": "a1b2c3d4e5f6..."
}
```

| `status` | Meaning |
|---|---|
| `received` | Request has been received |
| `processing` | Request is being processed |

#### 2. Transaction Result

Final outcome of the transaction. Sent by POS after the payment hardware/SDK responds.

```json
{
  "payload": {
    "type": "transaction_result",
    "txn_id": "TXN1705123456789",
    "status": "success",
    "authorization_code": "AUTH123",
    "card_last4": "1234",
    "timestamp": "1705123456789",
    "nonce": "550e8400-e29b-41d4-a716-446655440000"
  },
  "signature": "a1b2c3d4e5f6..."
}
```

| `status` | Meaning |
|---|---|
| `success` | Transaction completed successfully |
| `approved` | Transaction approved (alternative to success) |
| `failed` | Transaction failed |
| `ipp_plans` | IPP plans available — Kiosk will display them for user selection |

**Optional result fields by payment mode:**

| Field | Present when | Description |
|---|---|---|
| `authorization_code` | Card / BNPL success | Auth code from payment network |
| `card_last4` | Card success | Last 4 digits of card number |
| `plans` | status = `ipp_plans` | Array of installment plan objects (see IPP below) |

**IPP Plans Response:**

```json
{
  "payload": {
    "type": "transaction_result",
    "txn_id": "TXN1705123456789",
    "status": "ipp_plans",
    "amount": 100.00,
    "plans": [
      {
        "planId": "IPP_3M",
        "frequency": "Monthly",
        "totalInstallments": 3,
        "installmentDetails": [
          { "installmentNumber": 1, "date": "2024-02-15", "amount": 35.00, "installmentFee": 1.50, "installmentFeePercentage": 1.5 },
          { "installmentNumber": 2, "date": "2024-03-15", "amount": 35.00, "installmentFee": 1.50, "installmentFeePercentage": 1.5 },
          { "installmentNumber": 3, "date": "2024-04-15", "amount": 35.00, "installmentFee": 1.50, "installmentFeePercentage": 1.5 }
        ]
      }
    ],
    "timestamp": "1705123456789",
    "nonce": "550e8400-e29b-41d4-a716-446655440000"
  },
  "signature": "a1b2c3d4e5f6..."
}
```

#### 3. Error Response

Sent when the POS cannot process the request (hardware error, configuration issue, etc.).

```json
{
  "payload": {
    "type": "error",
    "txn_id": "TXN1705123456789",
    "message": "Error description",
    "timestamp": "1705123456789",
    "nonce": "550e8400-e29b-41d4-a716-446655440000"
  },
  "signature": "a1b2c3d4e5f6..."
}
```

---

## 🔄 Integration Workflow

### Standard Payment Flow

```
Kiosk (Server)                    POS Terminal (Client)
     │                                     │
     │◄──────────── TCP Connect ───────────│
     │                                     │
     ├──────── Transaction Request ───────►│
     │◄───────── ACK (processing) ─────────│
     │         [POS processes payment]      │
     │◄───── Transaction Result ───────────│
     ├──────── Display Result ────────────►│
```

### IPP Payment Flow

```
Kiosk (Server)                    POS Terminal (Client)
     │                                     │
     ├──── Transaction Request (IPP) ─────►│
     │◄──── ACK (processing) ──────────────│
     │◄──── Transaction Result (ipp_plans)─│
     ├──── Display Plans to User ─────────►│
     │      (User selects plan)             │
     ├──── IPP Plan Selection ────────────►│
     │◄──── ACK (processing) ──────────────│
     │◄──── Transaction Result (success) ──│
     ├──── Display Result ────────────────►│
```

### Cancellation Flow

```
Kiosk (Server)                    POS Terminal (Client)
     │                                     │
     ├──── Cancel Transaction ────────────►│
     │◄──── ACK (received) ────────────────│
     │      [POS aborts hardware txn]       │
```

### Connection Lifecycle & Reconnection

The POS terminal (client) is responsible for maintaining the connection:

1. **On startup:** Connect to the Kiosk server (`127.0.0.1` for same device, or Kiosk IP for remote).
2. **Keep-alive (recommended):** Detect stale connections by monitoring read timeouts or sending a lightweight ping every 30 seconds.
3. **On disconnect:** Implement exponential backoff retry — e.g., 1s → 2s → 4s → 8s, up to a max of 30s between retries.
4. **Mid-transaction disconnect:** Send an `error` result for the in-flight `txn_id` once reconnected, so the Kiosk can reset its state.
5. **Kiosk side:** Clean up socket state when a client disconnects; allow reconnection without requiring a server restart.

---

## 🌐 Network Configuration

### Requirements

- TCP connectivity between Kiosk and POS (same device, LAN, or internet)
- Open TCP port (default: **8080**)
- Shared HMAC secret on both sides
- Synchronized device clocks (within 60-second tolerance — use NTP)

### Deployment Scenarios

| Scenario | Kiosk IP | Notes |
|---|---|---|
| Same device | `127.0.0.1` | Android requires INTERNET permission |
| Same LAN | e.g. `192.168.1.100` | Reserve IP via DHCP or set static assignment |
| Internet | Public IP or hostname | Use TLS tunnel or VPN; open port in firewall |

### Android Network Security {#android-network-security}

For Android apps targeting API 28+, add a network security config to allow cleartext TCP to the Kiosk IP:

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="false">192.168.1.100</domain>
  </domain-config>
</network-security-config>
```

Reference it in `AndroidManifest.xml`:

```xml
<application android:networkSecurityConfig="@xml/network_security_config" ...>
```

> For same-device (`127.0.0.1`) connections, cleartext is acceptable. For internet deployments, use TLS.

### iOS Network Configuration

iOS apps using the `Network` framework for TCP connections may need:
- `NSLocalNetworkUsageDescription` in `Info.plist` for LAN discovery
- For enterprise/kiosk deployments (not App Store), no additional restrictions apply

### Production Configuration

| Parameter | Recommended Value |
|---|---|
| Port | 8080 (or any port > 1024) |
| Shared secret | Randomly generated, minimum 32 characters |
| Timestamp tolerance | 60 seconds |
| Nonce store | Redis with 60s TTL (production); in-memory (development) |
| Clock sync | NTP enabled on all devices |
| TLS | Required for internet-facing deployments |

---

*For platform-specific integration code → [QUICKSTART.md](QUICKSTART.md)*
*For testing procedures and troubleshooting → [TESTING.md](TESTING.md)*
