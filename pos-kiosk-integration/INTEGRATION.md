# MobyPay POS-KIOSK Integration Guide

This guide covers the integration architecture, communication protocols, and API specifications for integrating with the MobyPay Kiosk system.

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
- [Platform Integration Examples](#platform-integration-examples)

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
       │
  [POS Client]
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

### 1. Card Payment
Direct card transactions through the POS terminal. Supports credit and debit cards with real-time authorization.
**Payment Mode:** `card`

### 2. Buy Now Pay Later (BNPL)
Installment-based payment options with flexible terms and instant approval.
**Payment Mode:** `bnpl`

### 3. DuitNow QR
Malaysia's national QR payment system supporting bank and e-wallet integration.
**Payment Mode:** `duitnow_qr`

### 4. Installment Payment Plans (IPP)
Available for MobyPay BNPL account holders. Interactive plan selection via kiosk.
**Payment Mode:** `ipp`

---

## 📡 API Documentation

### Message Framing

All messages use **newline-delimited JSON**. Each message is a single JSON object followed by a newline character (`\n`). This newline is the message frame delimiter and **must always be appended** when sending.

```
<JSON object>\n
```

### Message Envelope

All messages follow this secure envelope:

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

> The `signature` is computed over the `payload` object only — keys sorted alphabetically, compact JSON separators, UTF-8 encoded.

---

### Request Types (Kiosk → POS)

#### 1. Transaction Request

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

#### 2. Cancel Transaction

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

#### 1. Acknowledgment

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

| Status | Meaning |
|---|---|
| `received` | Request has been received |
| `processing` | Request is being processed |

#### 2. Transaction Result

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

| Status | Meaning |
|---|---|
| `success` | Transaction completed successfully |
| `approved` | Transaction approved (alternative to success) |
| `failed` | Transaction failed |
| `ipp_plans` | IPP plans available — Kiosk must display and let user select |

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
     │                                     │
     │◄───────── Acknowledgment (ACK) ─────│
     │                                     │
     │         [POS processes payment]      │
     │                                     │
     │◄───── Transaction Result ───────────│
     │                                     │
     ├──────── Display Result ────────────►│
```

### IPP Payment Flow

```
Kiosk (Server)                    POS Terminal (Client)
     │                                     │
     ├──── Transaction Request (IPP) ─────►│
     │◄──── Acknowledgment (ACK) ──────────│
     │◄──── Transaction Result (ipp_plans)─│
     ├──── Display Plans to User ─────────►│
     │      (User selects plan)             │
     ├──── IPP Plan Selection ────────────►│
     │◄──── Acknowledgment (ACK) ──────────│
     │◄──── Transaction Result (success) ──│
     ├──── Display Result ────────────────►│
```

### Error Handling Flow

```
Kiosk (Server)                    POS Terminal (Client)
     │                                     │
     ├──── Transaction Request ───────────►│
     │◄──── Error Response ────────────────│
     ├──── Display Error ─────────────────►│
```

### Connection Lifecycle & Reconnection

The POS terminal (client) is responsible for maintaining the connection:

1. **On startup:** Connect to the Kiosk server (127.0.0.1 for same device, or Kiosk IP for remote).
2. **Keep-alive (recommended):** Send a lightweight ping message every 30 seconds to detect stale connections early.
3. **On disconnect:** Implement exponential backoff retry — e.g., 1s → 2s → 4s → 8s, up to a max of 30s between retries.
4. **Mid-transaction disconnect:** If the connection drops during a transaction, the POS should attempt reconnect and send an `error` result for the in-flight `txn_id` once reconnected, so the Kiosk can reset its state.
5. **Kiosk side:** Clean up socket state when a client disconnects; allow reconnection cleanly without requiring a server restart.

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

### Android Network Security

For Android apps targeting API 28+, if connecting over cleartext TCP (non-TLS), add a network security config:

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="false">192.168.1.100</domain>
  </domain-config>
</network-security-config>
```

Reference it in your `AndroidManifest.xml`:
```xml
<application
  android:networkSecurityConfig="@xml/network_security_config"
  ...>
```

> For same-device (127.0.0.1) connections, cleartext is acceptable. For internet deployments, use TLS.

### iOS Network Configuration

iOS apps using the `Network` framework for TCP connections may need:
- `NSLocalNetworkUsageDescription` in `Info.plist` for LAN discovery
- Bonjour services declaration for same-network browsing (if using mDNS for discovery)
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

## 💻 Platform Integration Examples

The core TCP protocol is identical on all platforms. Only the socket API differs.

### Android (Kotlin)

```kotlin
import java.net.Socket
import java.io.*
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import org.json.JSONObject
import java.util.UUID

class KioskTcpClient(
    private val kioskHost: String,  // "127.0.0.1" (same device) or IP/hostname (remote)
    private val kioskPort: Int = 8080,
    private val secret: String = "YOUR-PRODUCTION-SECRET-KEY",
    private val kioskId: String = "KIOSK001"
) {
    private var socket: Socket? = null
    private var writer: PrintWriter? = null
    private var reader: BufferedReader? = null

    fun connect() {
        socket = Socket(kioskHost, kioskPort)
        writer = PrintWriter(socket!!.getOutputStream(), true)
        reader = BufferedReader(InputStreamReader(socket!!.getInputStream()))
    }

    fun sendPayment(txnId: String, amount: Double, paymentMode: String): String {
        val payload = JSONObject().apply {
            put("type", "transaction_request")
            put("txn_id", txnId)
            put("amount", amount)
            put("payment_mode", paymentMode)
            put("kiosk_id", kioskId)
            put("timestamp", System.currentTimeMillis().toString())
            put("nonce", UUID.randomUUID().toString())
        }
        val message = buildSignedMessage(payload)
        writer?.println(message)           // println appends \n (the required frame delimiter)
        return reader?.readLine() ?: ""    // readLine reads until \n
    }

    private fun sign(payload: JSONObject): String {
        // Build canonical JSON: keys sorted, compact separators
        val sorted = payload.keys().asSequence().sorted()
            .joinToString(",", "{", "}") { key ->
                val v = payload.get(key)
                val valStr = when (v) {
                    is String -> "\"$v\""
                    is Boolean -> v.toString()
                    else -> v.toString()
                }
                "\"$key\":$valStr"
            }
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(secret.toByteArray(Charsets.UTF_8), "HmacSHA256"))
        return mac.doFinal(sorted.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }
    }

    private fun buildSignedMessage(payload: JSONObject): String {
        val envelope = JSONObject()
        envelope.put("payload", payload)
        envelope.put("signature", sign(payload))
        return envelope.toString()
    }

    fun disconnect() { socket?.close() }
}

// Usage — same code works for same-device and remote
fun example() {
    // Same device
    val client = KioskTcpClient(kioskHost = "127.0.0.1")
    // Different device on LAN
    // val client = KioskTcpClient(kioskHost = "192.168.1.100")
    // Over internet
    // val client = KioskTcpClient(kioskHost = "pos.merchant.com")

    client.connect()
    val txnId = "TXN${System.currentTimeMillis()}"
    val response = client.sendPayment(txnId, 50.0, "card")
    println("POS response: $response")
    client.disconnect()
}
```

### iOS / Swift

```swift
import Network
import Foundation
import CryptoKit

class KioskTcpClient {
    private var connection: NWConnection?
    private let kioskHost: String    // "127.0.0.1" (same device) or IP/hostname (remote)
    private let kioskPort: UInt16
    private let secret: String
    private let kioskId: String

    init(host: String = "127.0.0.1", port: UInt16 = 8080,
         secret: String = "YOUR-PRODUCTION-SECRET-KEY",
         kioskId: String = "KIOSK001") {
        self.kioskHost = host
        self.kioskPort = port
        self.secret = secret
        self.kioskId = kioskId
    }

    func connect(onReady: @escaping () -> Void) {
        let endpoint = NWEndpoint.hostPort(
            host: NWEndpoint.Host(kioskHost),
            port: NWEndpoint.Port(rawValue: kioskPort)!
        )
        connection = NWConnection(to: endpoint, using: .tcp)
        connection?.stateUpdateHandler = { [weak self] state in
            if case .ready = state { onReady() }
        }
        connection?.start(queue: .global())
    }

    func sendPayment(txnId: String, amount: Double, paymentMode: String) {
        var payload: [String: Any] = [
            "type": "transaction_request",
            "txn_id": txnId,
            "amount": amount,
            "payment_mode": paymentMode,
            "kiosk_id": kioskId,
            "timestamp": String(Int(Date().timeIntervalSince1970 * 1000)),
            "nonce": UUID().uuidString
        ]
        let signature = sign(payload: payload)
        let envelope: [String: Any] = ["payload": payload, "signature": signature]
        if var data = try? JSONSerialization.data(withJSONObject: envelope) {
            data.append(contentsOf: "\n".utf8)   // append newline frame delimiter
            connection?.send(content: data, completion: .idempotent)
        }
    }

    private func sign(payload: [String: Any]) -> String {
        let sorted = payload.keys.sorted().map { key -> String in
            let val = payload[key]!
            let valStr: String
            switch val {
            case let s as String: valStr = "\"\(s)\""
            case let b as Bool: valStr = b ? "true" : "false"
            default: valStr = "\(val)"
            }
            return "\"\(key)\":\(valStr)"
        }.joined(separator: ",")
        let json = "{\(sorted)}"
        let key = SymmetricKey(data: Data(secret.utf8))
        let sig = HMAC<SHA256>.authenticationCode(for: Data(json.utf8), using: key)
        return sig.map { String(format: "%02x", $0) }.joined()
    }
}

// Usage — same code, just change the host
// Same device:     KioskTcpClient(host: "127.0.0.1")
// LAN:             KioskTcpClient(host: "192.168.1.100")
// Internet:        KioskTcpClient(host: "pos.merchant.com")
```

### Windows / C# (.NET)

```csharp
using System;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Security.Cryptography;
using System.Collections.Generic;
using System.IO;

public class KioskTcpClient : IDisposable
{
    private TcpClient? _client;
    private StreamReader? _reader;
    private StreamWriter? _writer;

    private readonly string _kioskHost;  // "127.0.0.1" (same device) or IP/hostname (remote)
    private readonly int _kioskPort;
    private readonly string _secret;
    private readonly string _kioskId;

    public KioskTcpClient(string host = "127.0.0.1", int port = 8080,
                          string secret = "YOUR-PRODUCTION-SECRET-KEY",
                          string kioskId = "KIOSK001")
    {
        _kioskHost = host;
        _kioskPort = port;
        _secret = secret;
        _kioskId = kioskId;
    }

    public void Connect()
    {
        _client = new TcpClient(_kioskHost, _kioskPort);
        var stream = _client.GetStream();
        _reader = new StreamReader(stream);
        _writer = new StreamWriter(stream) { AutoFlush = true };
    }

    public string SendPayment(string txnId, double amount, string paymentMode)
    {
        var payload = new Dictionary<string, object>
        {
            ["type"] = "transaction_request",
            ["txn_id"] = txnId,
            ["amount"] = amount,
            ["payment_mode"] = paymentMode,
            ["kiosk_id"] = _kioskId,
            ["timestamp"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds().ToString(),
            ["nonce"] = Guid.NewGuid().ToString()
        };
        var signature = Sign(payload);
        var envelope = new { payload, signature };
        var json = JsonSerializer.Serialize(envelope);
        _writer!.WriteLine(json);          // WriteLine appends \n (the required frame delimiter)
        return _reader!.ReadLine() ?? "";  // ReadLine reads until \n
    }

    private string Sign(Dictionary<string, object> payload)
    {
        var sorted = new SortedDictionary<string, object>(payload);
        var json = JsonSerializer.Serialize(sorted, new JsonSerializerOptions { WriteIndented = false });
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(_secret));
        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(json));
        return BitConverter.ToString(hash).Replace("-", "").ToLower();
    }

    public void Dispose() { _client?.Dispose(); }
}

// Usage — same code, just change the host:
// Same device:   new KioskTcpClient(host: "127.0.0.1")
// LAN:           new KioskTcpClient(host: "192.168.1.100")
// Internet:      new KioskTcpClient(host: "pos.merchant.com")

class Program
{
    static void Main()
    {
        using var client = new KioskTcpClient(host: "127.0.0.1");
        client.Connect();
        var txnId = $"TXN{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}";
        var response = client.SendPayment(txnId, 50.0, "card");
        Console.WriteLine($"POS response: {response}");
    }
}
```

### Python (Reference / Testing)

See `kiosk.py` in this repository for the full reference server implementation, and `TESTING.md` for a minimal Python POS client example.

---

*For installation, testing procedures, and troubleshooting, refer to [TESTING.md](TESTING.md)*
