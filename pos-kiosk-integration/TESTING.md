# MobyPay POS-KIOSK Testing Guide

This guide covers testing procedures using the `kiosk.py` reference implementation. It includes installation, usage, manual testing, and troubleshooting.

---

## 📋 Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Kiosk Server](#running-the-kiosk-server)
- [Interactive Menu](#interactive-menu)
- [Testing Scenarios](#testing-scenarios)
- [Connection Testing](#connection-testing)
- [Security Testing](#security-testing)
- [Troubleshooting](#troubleshooting)
- [Example POS Test Client](#example-pos-test-client)

---

## Requirements

- Python 3.7 or higher
- Network connectivity between Kiosk and POS terminals (or same device — see below)
- Open TCP port for communication (default: 8080)

> **Same-device testing:** If both the Kiosk server and your POS test client run on the same machine, use `127.0.0.1` as the connection address. No network setup is needed.

---

## Installation

### 1. Install Python

**macOS:**
```bash
brew install python3
# Or download from https://www.python.org/downloads/
```

**Windows:**
```bash
# Download installer from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install python3 python3-pip
```

**Linux (CentOS/RHEL):**
```bash
sudo dnf install python3 python3-pip
```

### 2. Verify Python Installation

```bash
python3 --version  # Should show Python 3.7.x or higher
```

### 3. Get the Files

```bash
git clone https://github.com/MobyPayTech/moby-plugins.git
cd moby-plugins/pos-kiosk-integration
```

### 4. Dependencies

No external packages required. The kiosk system uses only Python standard library modules: `socket`, `json`, `threading`, `hashlib`, `hmac`, `uuid`, `datetime`.

---

## Running the Kiosk Server

```bash
cd pos-kiosk-integration
python3 kiosk.py
```

When prompted:
```
Enter port (default 8080): [Press Enter for default]
```

On startup you will see the Kiosk's listening address:
```
🚀 Server started on 192.168.1.100:8080
📱 Connect your POS terminal to: 192.168.1.100:8080
```

> **Same-device testing:** When your POS test client runs on the same machine, connect to `127.0.0.1:8080` regardless of the IP shown above.

---

## Interactive Menu

```
📋 Available Commands:
1. 💳 Card Payment
2. 🛒 Buy Now Pay Later (BNPL)
3. 📱 DuitNow QR
4. 🏦 Installment Payment Plan (IPP)
5. 🚫 Cancel Transaction
6. ℹ️  Show Status
7. 🔴 Exit
```

---

## Testing Scenarios

### Scenario 1: Same-Device Test (Kiosk + POS on one machine)

This is the quickest way to verify the integration without any network setup.

1. Start the Kiosk server: `python3 kiosk.py`
2. In a **second terminal**, run the Python POS test client (see [Example POS Test Client](#example-pos-test-client)) with `host = "127.0.0.1"`
3. From the Kiosk menu, select option **1 (Card Payment)** and enter an amount
4. The test client should receive the request, send an ACK, then send a success result
5. The Kiosk should display the payment result

### Scenario 2: LAN Test (Kiosk + POS on different devices)

1. Note the IP address shown when the Kiosk server starts (e.g. `192.168.1.100:8080`)
2. On the POS device, run the test client with `host = "192.168.1.100"`
3. Verify the Kiosk shows **"🔗 Client connected from ..."** in its output
4. Test all payment methods

### Scenario 3: Internet Test (remote POS)

1. Ensure the Kiosk's port 8080 is accessible from the internet (port forward or public IP)
2. On the remote POS, run the test client with `host = "<kiosk-public-ip>"`
3. Verify connectivity and test all payment methods

> For internet deployments, wrap the connection in TLS or a VPN in production. Raw TCP over the internet is unencrypted.

### Scenario 4: Card Payment

1. Start Kiosk server
2. Connect POS test client (any topology)
3. Select option **1** → enter amount e.g. `25.50`
4. Expected Kiosk output:
```
📤 Sending card payment request for RM25.50
🆔 Transaction ID: TXN1705123456789
✅ Payment request sent to POS terminal
```

### Scenario 5: IPP Plan Selection

1. Connect POS test client that supports IPP plan responses
2. Select option **4 (IPP)** → enter amount e.g. `100.00`
3. POS responds with available plans:
```
💰 Amount: RM100.00
📋 Available Installment Plans:
--------------------------------------------------
1. Plan ID: IPP_3M
   Frequency: Monthly
   Total Installments: 3
   Installment Details:
     #1: RM35.00 on 2024-02-15  Fee: RM1.50 (1.5%)
     #2: RM35.00 on 2024-03-15  Fee: RM1.50 (1.5%)
     #3: RM35.00 on 2024-04-15  Fee: RM1.50 (1.5%)
Select plan (1-3) or 'q' to quit:
```

### Scenario 6: Transaction Cancellation

1. Initiate a payment (e.g. option 1, amount 50.00)
2. Before the POS responds, select option **5 (Cancel)**
3. Expected output:
```
🚫 Cancelling transaction: TXN1705123456789
✅ Cancel request sent to POS terminal
```

### Scenario 7: Amount Edge Cases

| Amount | Purpose |
|---|---|
| 0.01 | Minimum — smallest valid amount |
| 10.00 | Small transaction |
| 99.99 | Standard transaction |
| 999.99 | Large transaction |
| 5000.00 | Maximum — verify upper bound handling |

---

## Connection Testing

### Verify Port is Open

```bash
# Using telnet
telnet <kiosk-ip> 8080

# Using netcat
nc -zv <kiosk-ip> 8080

# Same-device check
nc -zv 127.0.0.1 8080
```

### Check Connectivity

```bash
ping <kiosk-ip>
```

### View Live Connections

From the Kiosk interactive menu, select **option 6 (Show Status)**:
```
📊 Status:
🔗 Connected POS terminals: 1
🆔 Current transaction: TXN1705123456789
👂 Listening for responses: True
🏪 Kiosk ID: KIOSK001
```

---

## Security Testing

The system automatically validates these security aspects on every message:

### 1. Message Signature Validation

All received messages are verified using HMAC-SHA256.

- POS terminals must use the shared secret `POS-KIOSK-SECRET-KEY-2024` (for testing; replace in production)
- Invalid signatures trigger security validation failures

**Expected output on valid signature:**
```
🔐 Signature verification PASSED:
   ✅ Signature matches expected value
   📨 Signature: a1b2c3d4e5f6...xxxxxxxx
```

**Expected output on invalid signature:**
```
🔐 Signature verification FAILED:
   📨 Received signature: xxxx...
   🔑 Expected signature: yyyy...
🔒 Security validation failed: Invalid signature
```

### 2. Nonce Validation

Each message uses a unique UUID v4 nonce. Duplicate nonces are rejected.

### 3. Timestamp Validation

Timestamps must be within a 60-second window.

```
🕐 Timestamp validation - Request: 1705123456789, Current: 1705123458000, Diff: 1211ms
✅ Timestamp valid: Within 60 second window
```

**Expired timestamp:**
```
❌ Timestamp failed: Request too old/new (diff: 65000ms > 60000ms)
🔒 Security validation failed: Request expired or invalid timestamp
```

---

## Troubleshooting

| Problem | Error | Solution |
|---|---|---|
| Port in use | `[Errno 48] Address already in use` | Run `lsof -i :8080` to find the process and kill it, or use a different port |
| Permission denied | `[Errno 13] Permission denied` | Use a port > 1024; avoid privileged ports |
| No POS connection | `❌ No POS terminals connected` | Verify IP/port, check firewall, run `ping <kiosk-ip>`, test port with telnet/nc |
| Signature failure | `🔒 Security validation failed: Invalid signature` | Ensure both sides use the same shared secret; verify JSON is UTF-8 and keys are sorted |
| Invalid JSON | `❌ JSON decode error` | Verify message ends with `\n`; validate JSON format; check for encoding issues |
| Clock drift | `Timestamp failed: Request too old/new` | Sync device clocks via NTP |

### Capture Debug Logs

```bash
python3 kiosk.py 2>&1 | tee kiosk.log

# Search for errors
grep "❌" kiosk.log

# Search for security events
grep "🔐" kiosk.log
```

---

## Example POS Test Client

This minimal Python client simulates a POS terminal. It works for **all deployment scenarios** — just change the `host` parameter:

```python
import socket
import json
import hmac
import hashlib
import uuid
from datetime import datetime

# Configuration
KIOSK_HOST = "127.0.0.1"   # Same device
# KIOSK_HOST = "192.168.1.100"  # LAN
# KIOSK_HOST = "pos.merchant.com"  # Internet
KIOSK_PORT = 8080
SECRET = "POS-KIOSK-SECRET-KEY-2024"  # Replace in production

def sign(payload: dict) -> str:
    """Create HMAC-SHA256 signature over sorted payload."""
    json_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return hmac.new(
        SECRET.encode('utf-8'),
        json_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def build_message(msg_type: str, txn_id: str, **extra) -> bytes:
    """Build a signed message with newline frame delimiter."""
    payload = {
        "type": msg_type,
        "txn_id": txn_id,
        "timestamp": str(int(datetime.now().timestamp() * 1000)),
        "nonce": str(uuid.uuid4()),
        **extra
    }
    message = {"payload": payload, "signature": sign(payload)}
    return json.dumps(message).encode('utf-8') + b'\n'  # \n is the frame delimiter

def simulate_pos():
    print(f"Connecting to Kiosk at {KIOSK_HOST}:{KIOSK_PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((KIOSK_HOST, KIOSK_PORT))
    reader = sock.makefile('r')
    print("✅ Connected!")

    while True:
        print("Waiting for payment request from Kiosk...")
        raw = reader.readline()  # reads until \n
        if not raw:
            print("Connection closed by Kiosk.")
            break

        request = json.loads(raw)
        payload = request.get('payload', {})
        txn_id = payload.get('txn_id', '')
        msg_type = payload.get('type', '')
        print(f"📨 Received: {msg_type} | TXN: {txn_id}")

        if msg_type == 'transaction_request':
            payment_mode = payload.get('payment_mode', '')
            amount = payload.get('amount', 0)
            print(f"   Amount: RM{amount:.2f}, Mode: {payment_mode}")

            # Step 1: Send ACK
            ack = build_message("ack", txn_id, status="processing")
            sock.send(ack)
            print("   → Sent ACK (processing)")

            if payment_mode == 'ipp':
                # Step 2a: Send IPP plans for selection
                result = build_message("transaction_result", txn_id,
                    status="ipp_plans",
                    amount=amount,
                    plans=[{
                        "planId": "IPP_3M",
                        "frequency": "Monthly",
                        "totalInstallments": 3,
                        "installmentDetails": [
                            {"installmentNumber": 1, "date": "2024-02-15", "amount": round(amount/3, 2), "installmentFee": 1.50, "installmentFeePercentage": 1.5},
                            {"installmentNumber": 2, "date": "2024-03-15", "amount": round(amount/3, 2), "installmentFee": 1.50, "installmentFeePercentage": 1.5},
                            {"installmentNumber": 3, "date": "2024-04-15", "amount": round(amount/3, 2), "installmentFee": 1.50, "installmentFeePercentage": 1.5},
                        ]
                    }]
                )
                sock.send(result)
                print("   → Sent IPP plans")
            else:
                # Step 2b: Simulate successful payment
                result = build_message("transaction_result", txn_id,
                    status="success",
                    authorization_code="AUTH123",
                    card_last4="4242"
                )
                sock.send(result)
                print("   → Sent transaction result: success")

        elif msg_type == 'ipp_plan_selection':
            plan_id = payload.get('plan_id', '')
            print(f"   Selected plan: {plan_id}")
            # ACK the plan selection
            ack = build_message("ack", txn_id, status="processing")
            sock.send(ack)
            # Send final success
            result = build_message("transaction_result", txn_id,
                status="success",
                authorization_code="AUTH456",
                plan_id=plan_id
            )
            sock.send(result)
            print("   → Sent final IPP success")

        elif msg_type == 'cancel_transaction':
            ack = build_message("ack", txn_id, status="received")
            sock.send(ack)
            print("   → Sent cancel ACK")

    sock.close()

if __name__ == "__main__":
    simulate_pos()
```

> **Tip:** To test all three deployment scenarios, only change `KIOSK_HOST`:
> - Same device: `"127.0.0.1"`
> - LAN: `"192.168.1.100"` (use the IP shown by kiosk.py on startup)
> - Internet: your Kiosk's public IP or hostname

---

*For API specifications and integration architecture, refer to [INTEGRATION.md](INTEGRATION.md)*
