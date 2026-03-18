# MobyPay POS-KIOSK Quick Start Guide

Get from zero to a working POS integration in under 5 minutes — on any platform, any deployment topology.

---

## How it works

The **Kiosk app is the TCP server**. The **POS app is the TCP client**. The POS connects to the Kiosk, receives payment requests, processes them, and sends results back. The protocol is identical everywhere — only the IP address changes.

```
POS (your code)  ──── TCP connect ────→  Kiosk server
                 ←─── payment request ──
                 ──── ACK + result ────→
```

| Where are Kiosk + POS? | POS connects to |
|---|---|
| Same device | `127.0.0.1:8080` |
| Same LAN | `192.168.1.100:8080` (Kiosk's IP) |
| Over internet | `yourkiosk.domain.com:8080` |

---

## Step 1 — Start the Kiosk Server

```bash
# Requires Python 3.7+ — no extra packages needed
cd pos-kiosk-integration
python3 kiosk.py
```

```
Enter port (default 8080): [press Enter]
🚀 Server started on 192.168.1.100:8080
📱 Connect your POS terminal to: 192.168.1.100:8080
```

> **Same-device test:** connect to `127.0.0.1:8080` from your POS, regardless of the IP shown above.

---

## Step 2 — Integrate Your POS (pick your platform)

---

### 🤖 Android (Kotlin)

#### AndroidManifest.xml

```xml
<!-- Required for TCP — even for localhost connections -->
<uses-permission android:name="android.permission.INTERNET" />
```

For LAN connections on Android API 28+, add a network security config:

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="false">192.168.1.100</domain>
  </domain-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml <application> tag -->
<application android:networkSecurityConfig="@xml/network_security_config" ...>
```

#### MobyPosClient.kt

```kotlin
import java.net.Socket
import java.io.*
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import org.json.JSONObject
import java.util.UUID

class MobyPosClient(
    private val host: String,           // "127.0.0.1" (same device) | "192.168.1.x" (LAN) | hostname (internet)
    private val port: Int = 8080,
    private val secret: String,         // must match Kiosk secret — never hardcode in production
    private val kioskId: String = "KIOSK001"
) {
    private var socket: Socket? = null
    private var writer: PrintWriter? = null
    private var reader: BufferedReader? = null

    fun connect() {
        socket = Socket(host, port)
        writer = PrintWriter(BufferedWriter(OutputStreamWriter(socket!!.getOutputStream())), true)
        reader = BufferedReader(InputStreamReader(socket!!.getInputStream()))
    }

    fun disconnect() { socket?.close() }

    // ── Main entry point: called when Kiosk sends a payment request ──────────────
    // Run this in a background thread / coroutine — it blocks on readLine()
    fun listenAndRespond(
        onRequest: (txnId: String, amount: Double, paymentMode: String) -> TransactionResult,
        onCancel: (txnId: String) -> Unit = {}
    ) {
        while (true) {
            val raw = reader?.readLine() ?: break  // blocks until \n received
            val msg = JSONObject(raw)
            if (!verify(msg)) { /* drop invalid/tampered messages */ continue }

            val payload = msg.getJSONObject("payload")
            when (payload.getString("type")) {
                "transaction_request" -> {
                    val txnId = payload.getString("txn_id")
                    val amount = payload.getDouble("amount")
                    val mode = payload.getString("payment_mode")

                    sendAck(txnId)                        // Step 1: ACK immediately
                    val result = onRequest(txnId, amount, mode)  // Step 2: process payment
                    sendResult(txnId, result)             // Step 3: send result
                }
                "cancel_transaction" -> {
                    val txnId = payload.getString("txn_id")
                    sendAck(txnId)
                    onCancel(txnId)
                }
                "ipp_plan_selection" -> {
                    val txnId = payload.getString("txn_id")
                    val planId = payload.getString("plan_id")
                    sendAck(txnId)
                    // process the selected IPP plan here, then send result
                }
            }
        }
    }

    private fun sendAck(txnId: String) = send(mapOf(
        "type" to "ack", "txn_id" to txnId, "status" to "processing"
    ))

    fun sendResult(txnId: String, result: TransactionResult) = send(when (result) {
        is TransactionResult.Success -> mapOf(
            "type" to "transaction_result", "txn_id" to txnId,
            "status" to "success",
            "authorization_code" to result.authCode,
            "card_last4" to result.cardLast4
        )
        is TransactionResult.Failed -> mapOf(
            "type" to "transaction_result", "txn_id" to txnId,
            "status" to "failed"
        )
        is TransactionResult.IppPlans -> mapOf(
            "type" to "transaction_result", "txn_id" to txnId,
            "status" to "ipp_plans",
            "amount" to result.amount,
            "plans" to result.plans
        )
    })

    private fun send(data: Map<String, Any>) {
        val payload = JSONObject(data).apply {
            put("timestamp", System.currentTimeMillis().toString())
            put("nonce", UUID.randomUUID().toString())
        }
        val envelope = JSONObject()
        envelope.put("payload", payload)
        envelope.put("signature", sign(payload))
        writer?.println(envelope.toString())   // println appends \n (frame delimiter)
    }

    private fun sign(payload: JSONObject): String {
        val sorted = payload.keys().asSequence().sorted()
            .joinToString(",", "{", "}") { key ->
                val v = payload.get(key)
                "\"$key\":" + if (v is String) "\"$v\"" else v.toString()
            }
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(secret.toByteArray(Charsets.UTF_8), "HmacSHA256"))
        return mac.doFinal(sorted.toByteArray(Charsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
    }

    private fun verify(msg: JSONObject): Boolean {
        val payload = msg.optJSONObject("payload") ?: return false
        val received = msg.optString("signature")
        return sign(payload) == received
    }
}

// Result types — map these to your payment SDK's response
sealed class TransactionResult {
    data class Success(val authCode: String, val cardLast4: String) : TransactionResult()
    object Failed : TransactionResult()
    data class IppPlans(val amount: Double, val plans: List<Map<String, Any>>) : TransactionResult()
}
```

#### Usage

```kotlin
// In a ViewModel or Service — run on a background coroutine
viewModelScope.launch(Dispatchers.IO) {
    val client = MobyPosClient(
        host = "127.0.0.1",         // same device
        // host = "192.168.1.100",  // LAN
        secret = BuildConfig.MOBY_SECRET
    )
    client.connect()

    client.listenAndRespond(
        onRequest = { txnId, amount, paymentMode ->
            // Call your payment SDK here
            // Return the result:
            TransactionResult.Success(authCode = "AUTH123", cardLast4 = "4242")
        },
        onCancel = { txnId ->
            // Cancel any in-progress payment SDK call
        }
    )
}
```

---

### 🍎 iOS / Swift

#### Info.plist

```xml
<!-- Required for LAN access -->
<key>NSLocalNetworkUsageDescription</key>
<string>Required to communicate with the MobyPay Kiosk terminal on your local network.</string>
```

#### MobyPosClient.swift

```swift
import Network
import Foundation
import CryptoKit

class MobyPosClient {
    private var connection: NWConnection?
    private var receiveBuffer = Data()

    let host: String       // "127.0.0.1" (same device) | LAN IP | hostname
    let port: UInt16
    let secret: String
    let kioskId: String

    var onTransactionRequest: ((String, Double, String) -> Void)?  // (txnId, amount, paymentMode)
    var onCancelRequest: ((String) -> Void)?

    init(host: String = "127.0.0.1", port: UInt16 = 8080,
         secret: String, kioskId: String = "KIOSK001") {
        self.host = host; self.port = port
        self.secret = secret; self.kioskId = kioskId
    }

    func connect(onReady: @escaping () -> Void) {
        let ep = NWEndpoint.hostPort(host: NWEndpoint.Host(host),
                                     port: NWEndpoint.Port(rawValue: port)!)
        connection = NWConnection(to: ep, using: .tcp)
        connection?.stateUpdateHandler = { [weak self] state in
            if case .ready = state {
                onReady()
                self?.receive()     // start listening loop
            }
        }
        connection?.start(queue: .global(qos: .userInitiated))
    }

    // ── Receive loop — reads newline-delimited JSON frames ────────────────────────
    private func receive() {
        connection?.receive(minimumIncompleteLength: 1, maximumLength: 65536) { [weak self] data, _, isComplete, _ in
            guard let self = self, let data = data else { return }
            self.receiveBuffer.append(data)

            // Process all complete \n-delimited messages in the buffer
            while let newlineRange = self.receiveBuffer.firstRange(of: Data("\n".utf8)) {
                let msgData = self.receiveBuffer.subdata(in: self.receiveBuffer.startIndex..<newlineRange.lowerBound)
                self.receiveBuffer.removeSubrange(self.receiveBuffer.startIndex...newlineRange.upperBound - 1)
                if let json = try? JSONSerialization.jsonObject(with: msgData) as? [String: Any] {
                    self.handleMessage(json)
                }
            }
            if !isComplete { self.receive() }
        }
    }

    private func handleMessage(_ msg: [String: Any]) {
        guard let payload = msg["payload"] as? [String: Any],
              let signature = msg["signature"] as? String,
              sign(payload) == signature else { return }  // drop if invalid signature

        guard let type = payload["type"] as? String,
              let txnId = payload["txn_id"] as? String else { return }

        switch type {
        case "transaction_request":
            let amount = payload["amount"] as? Double ?? 0
            let mode = payload["payment_mode"] as? String ?? ""
            sendAck(txnId: txnId)
            DispatchQueue.main.async { self.onTransactionRequest?(txnId, amount, mode) }

        case "cancel_transaction":
            sendAck(txnId: txnId)
            DispatchQueue.main.async { self.onCancelRequest?(txnId) }

        default: break
        }
    }

    func sendSuccess(txnId: String, authCode: String, cardLast4: String) {
        send(["type": "transaction_result", "txn_id": txnId,
              "status": "success", "authorization_code": authCode, "card_last4": cardLast4])
    }

    func sendFailed(txnId: String) {
        send(["type": "transaction_result", "txn_id": txnId, "status": "failed"])
    }

    private func sendAck(txnId: String) {
        send(["type": "ack", "txn_id": txnId, "status": "processing"])
    }

    private func send(_ data: [String: Any]) {
        var payload = data
        payload["timestamp"] = String(Int(Date().timeIntervalSince1970 * 1000))
        payload["nonce"] = UUID().uuidString
        payload["kiosk_id"] = kioskId
        let signature = sign(payload)
        guard var msgData = try? JSONSerialization.data(withJSONObject: ["payload": payload, "signature": signature]) else { return }
        msgData.append(contentsOf: "\n".utf8)   // newline frame delimiter
        connection?.send(content: msgData, completion: .idempotent)
    }

    private func sign(_ payload: [String: Any]) -> String {
        let sorted = payload.keys.sorted().map { key -> String in
            let val = payload[key]!
            let v = val is String ? "\"\(val)\"" : "\(val)"
            return "\"\(key)\":$v"
        }.joined(separator: ",")
        let json = "{\(sorted)}"
        let key = SymmetricKey(data: Data(secret.utf8))
        return HMAC<SHA256>.authenticationCode(for: Data(json.utf8), using: key)
            .map { String(format: "%02x", $0) }.joined()
    }
}
```

#### Usage

```swift
let client = MobyPosClient(
    host: "127.0.0.1",     // same device
    // host: "192.168.1.100",   // LAN
    secret: Secrets.mobySecret
)

client.onTransactionRequest = { txnId, amount, paymentMode in
    // Call your payment SDK here, then:
    client.sendSuccess(txnId: txnId, authCode: "AUTH123", cardLast4: "4242")
    // or on failure: client.sendFailed(txnId: txnId)
}

client.onCancelRequest = { txnId in
    // Cancel any in-progress payment SDK call
}

client.connect {
    print("Connected to Kiosk — ready to receive payment requests")
}
```

---

### 🪟 Windows / C# (.NET)

#### MobyPosClient.cs

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class MobyPosClient : IDisposable
{
    private TcpClient? _client;
    private StreamReader? _reader;
    private StreamWriter? _writer;

    public string Host { get; }         // "127.0.0.1" (same device) | LAN IP | hostname
    public int Port { get; }
    private readonly string _secret;
    private readonly string _kioskId;

    // Callbacks — wire these up before calling ConnectAsync()
    public Func<string, double, string, Task<TxnResult>>? OnTransactionRequest { get; set; }
    public Func<string, Task>? OnCancelRequest { get; set; }

    public MobyPosClient(string host = "127.0.0.1", int port = 8080,
                         string secret = "REPLACE-IN-PRODUCTION",
                         string kioskId = "KIOSK001")
    {
        Host = host; Port = port; _secret = secret; _kioskId = kioskId;
    }

    public async Task ConnectAsync()
    {
        _client = new TcpClient();
        await _client.ConnectAsync(Host, Port);
        var stream = _client.GetStream();
        _reader = new StreamReader(stream);
        _writer = new StreamWriter(stream) { AutoFlush = true };
    }

    // ── Main listen loop — call after ConnectAsync() ──────────────────────────────
    public async Task ListenAsync()
    {
        while (true)
        {
            var raw = await _reader!.ReadLineAsync();   // blocks until \n received
            if (raw == null) break;

            using var doc = JsonDocument.Parse(raw);
            var root = doc.RootElement;
            var payload = root.GetProperty("payload");
            var receivedSig = root.GetProperty("signature").GetString() ?? "";

            if (!Verify(payload, receivedSig)) continue; // drop tampered messages

            var type = payload.GetProperty("type").GetString();
            var txnId = payload.GetProperty("txn_id").GetString() ?? "";

            switch (type)
            {
                case "transaction_request":
                    var amount = payload.GetProperty("amount").GetDouble();
                    var mode = payload.GetProperty("payment_mode").GetString() ?? "";
                    await SendAck(txnId);
                    if (OnTransactionRequest != null)
                    {
                        var result = await OnTransactionRequest(txnId, amount, mode);
                        await SendResult(txnId, result);
                    }
                    break;

                case "cancel_transaction":
                    await SendAck(txnId);
                    if (OnCancelRequest != null) await OnCancelRequest(txnId);
                    break;
            }
        }
    }

    public async Task SendResult(string txnId, TxnResult result)
    {
        var data = result switch
        {
            TxnResult.Success s => new Dictionary<string, object>
            {
                ["type"] = "transaction_result", ["txn_id"] = txnId,
                ["status"] = "success", ["authorization_code"] = s.AuthCode,
                ["card_last4"] = s.CardLast4
            },
            TxnResult.Failed => new Dictionary<string, object>
            {
                ["type"] = "transaction_result", ["txn_id"] = txnId, ["status"] = "failed"
            },
            _ => throw new ArgumentException("Unknown result type")
        };
        await Send(data);
    }

    private Task SendAck(string txnId) => Send(new Dictionary<string, object>
    {
        ["type"] = "ack", ["txn_id"] = txnId, ["status"] = "processing"
    });

    private async Task Send(Dictionary<string, object> data)
    {
        data["timestamp"] = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds().ToString();
        data["nonce"] = Guid.NewGuid().ToString();
        data["kiosk_id"] = _kioskId;

        var signature = Sign(data);
        var envelope = new { payload = data, signature };
        var json = JsonSerializer.Serialize(envelope);
        await _writer!.WriteLineAsync(json);    // WriteLine appends \n (frame delimiter)
    }

    private string Sign(Dictionary<string, object> payload)
    {
        var sorted = new SortedDictionary<string, object>(payload);
        var json = JsonSerializer.Serialize(sorted, new JsonSerializerOptions { WriteIndented = false });
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(_secret));
        return BitConverter.ToString(hmac.ComputeHash(Encoding.UTF8.GetBytes(json)))
            .Replace("-", "").ToLower();
    }

    private bool Verify(JsonElement payload, string receivedSignature)
    {
        // Rebuild the canonical payload dict for signing
        var dict = new SortedDictionary<string, object>();
        foreach (var prop in payload.EnumerateObject())
        {
            dict[prop.Name] = prop.Value.ValueKind switch
            {
                JsonValueKind.Number => (object)prop.Value.GetDouble(),
                JsonValueKind.True => true,
                JsonValueKind.False => false,
                _ => prop.Value.GetString() ?? ""
            };
        }
        var json = JsonSerializer.Serialize(dict, new JsonSerializerOptions { WriteIndented = false });
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(_secret));
        var expected = BitConverter.ToString(hmac.ComputeHash(Encoding.UTF8.GetBytes(json)))
            .Replace("-", "").ToLower();
        return expected == receivedSignature;
    }

    public void Dispose() => _client?.Dispose();
}

// Result types
public abstract record TxnResult
{
    public sealed record Success(string AuthCode, string CardLast4) : TxnResult;
    public sealed record Failed : TxnResult;
}
```

#### Usage

```csharp
using var client = new MobyPosClient(
    host: "127.0.0.1",       // same device
    // host: "192.168.1.100",   // LAN
    secret: Environment.GetEnvironmentVariable("MOBY_SECRET")!
);

client.OnTransactionRequest = async (txnId, amount, paymentMode) =>
{
    Console.WriteLine($"Payment request: {paymentMode} RM{amount:F2} [{txnId}]");

    // Call your payment hardware SDK here...
    // Return the result:
    return new TxnResult.Success(AuthCode: "AUTH123", CardLast4: "4242");
    // or: return new TxnResult.Failed();
};

client.OnCancelRequest = async txnId =>
{
    Console.WriteLine($"Cancel request for {txnId}");
    // Cancel any in-progress hardware transaction
};

await client.ConnectAsync();
Console.WriteLine($"Connected to Kiosk at {client.Host}:{client.Port}");
await client.ListenAsync();  // runs until disconnected
```

---

### 🐍 Python (testing & scripting)

For full Python POS simulator code, see **[TESTING.md → Example POS Test Client](TESTING.md#example-pos-test-client)**.

```python
# Minimal Python example — change KIOSK_HOST to match your deployment
KIOSK_HOST = "127.0.0.1"      # same device
# KIOSK_HOST = "192.168.1.100" # LAN

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((KIOSK_HOST, 8080))
reader = sock.makefile('r')

while True:
    raw = reader.readline()          # blocks until \n received
    request = json.loads(raw)
    txn_id = request['payload']['txn_id']

    # ACK → process → result
    sock.send(build_message("ack", txn_id, status="processing"))
    sock.send(build_message("transaction_result", txn_id,
                            status="success", authorization_code="AUTH123"))
```

---

## Step 3 — Test All Payment Modes

From the **Kiosk server interactive menu**, test each payment mode:

| Menu option | `payment_mode` sent | Your POS should respond with |
|---|---|---|
| 1. Card Payment | `card` | ACK → `transaction_result` status `success` |
| 2. BNPL | `bnpl` | ACK → `transaction_result` status `success` |
| 3. DuitNow QR | `duitnow_qr` | ACK → `transaction_result` status `success` |
| 4. IPP | `ipp` | ACK → `transaction_result` status `ipp_plans` → user selects → `success` |
| 5. Cancel | — | ACK the cancel |

---

## Step 4 — Transaction Result Fields

Your POS sends these fields back in the `transaction_result` payload:

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | ✅ | Always `"transaction_result"` |
| `txn_id` | string | ✅ | Must match the request's `txn_id` |
| `status` | string | ✅ | `success` / `approved` / `failed` / `ipp_plans` |
| `authorization_code` | string | Card/BNPL | Auth code from payment network |
| `card_last4` | string | Card | Last 4 digits of card |
| `plans` | array | IPP only | Array of installment plan objects |
| `timestamp` | string | ✅ | Milliseconds since epoch |
| `nonce` | string | ✅ | Unique UUID v4 per message |

---

## Step 5 — Go-Live Checklist

```
□ Replace POS-KIOSK-SECRET-KEY-2024 with a securely generated secret (min 32 chars)
□ Store the secret in environment variables or a secrets manager — never in source code
□ Enable NTP on both Kiosk and POS devices (clocks must be within 60 seconds)
□ For internet deployments: wrap TCP in TLS or use a VPN
□ For Android: INTERNET permission + network_security_config.xml for your Kiosk's IP
□ For iOS: NSLocalNetworkUsageDescription in Info.plist
□ Verify all 5 payment modes work end-to-end in staging
□ Test reconnection: kill the Kiosk server and verify POS reconnects automatically
□ Test cancellation: send a cancel mid-transaction and verify state resets correctly
```

---

## Troubleshooting Quick Reference

| Symptom | Likely cause | Fix |
|---|---|---|
| Can't connect | Wrong IP or port blocked | Use `nc -zv <host> 8080` to test; check firewall |
| Signature validation failed | Secret mismatch | Ensure both sides use the same secret; verify JSON key sort order |
| Timestamp expired | Clock drift | Enable NTP on both devices |
| No response from Kiosk | Not connected | Check Kiosk Status (menu option 6) shows 1+ connected terminals |
| Android: cleartext not permitted | API 28+ restriction | Add `network_security_config.xml` (see [INTEGRATION.md](INTEGRATION.md#android-network-security)) |

For detailed testing procedures → [TESTING.md](TESTING.md)
For full API reference → [INTEGRATION.md](INTEGRATION.md)
