# MobyPay POS-KIOSK Testing Guide

This guide covers testing procedures using the `kiosk.py` reference implementation. It includes installation, usage, manual testing, and troubleshooting.

## 📋 Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Kiosk Server](#running-the-kiosk-server)
- [Interactive Menu](#interactive-menu)
- [Manual Testing](#manual-testing)
- [Testing Scenarios](#testing-scenarios)
- [Connection Testing](#connection-testing)
- [Security Testing](#security-testing)
- [Troubleshooting](#troubleshooting)

## Requirements

- Python 3.7 or higher
- Network connectivity between kiosk and POS terminals
- Open TCP port for communication (default: 8080)

## Installation

### 1. Install Python

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python3

# Or download from python.org
# Visit: https://www.python.org/downloads/
```

**Windows:**
```bash
# Download installer from python.org
# Visit: https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install python3 python3-pip
# or for newer versions:
sudo dnf install python3 python3-pip
```

### 2. Verify Python Installation

```bash
python3 --version
# Should show Python 3.7.x or higher
```

### 3. Clone/Download the Project

```bash
# If using git
git clone <repository-url>
cd pos-kiosk-integration

# Or download and extract the files to this directory
```

### 4. Dependencies

The kiosk system uses only Python standard library modules:
- `socket` - TCP communication
- `json` - Message formatting
- `threading` - Concurrent connection handling
- `hashlib` & `hmac` - Security and message signing
- `uuid` - Nonce generation
- `datetime` - Timestamp validation

No external packages need to be installed.

## Running the Kiosk Server

### Starting the Server

1. **Navigate to the project directory:**
   ```bash
   cd pos-kiosk-integration
   ```

2. **Run the kiosk application:**
   ```bash
   python3 kiosk.py
   ```

3. **Configure the server:**
   ```
   Enter port (default 8080): [Press Enter for default or enter custom port]
   ```

4. **Server startup confirmation:**
   ```
   🚀 Server started on 192.168.1.100:8080
   📱 Connect your POS terminal to: 192.168.1.100:8080
   ```

The server is now ready to accept POS terminal connections.

## Interactive Menu

Once the server is running, you'll see the following menu:

```
📋 Available Commands:
1. 💳 Card Payment
2. 🛒 Buy Now Pay Later (BNPL)
3. 📱 DuitNow QR
4. 🏦 Internet Banking (IPP)
5. 🚫 Cancel Transaction
6. ℹ️  Show Status
7. 🔴 Exit
```

### Menu Options Explained

- **1. Card Payment**: Initiate a card payment transaction
- **2. BNPL**: Initiate a Buy Now Pay Later transaction
- **3. DuitNow QR**: Initiate a DuitNow QR payment
- **4. IPP**: Initiate an Installment Payment Plan transaction
- **5. Cancel**: Cancel the current active transaction
- **6. Status**: Display current server and connection status
- **7. Exit**: Shut down the server and exit

## Manual Testing

### Basic Card Payment Test

1. **Start the server:**
   ```bash
   python3 kiosk.py
   ```

2. **When prompted for port, press Enter** (to use default 8080)

3. **Select option 1** (Card Payment)

4. **Enter an amount when prompted:**
   ```
   Enter amount (RM): 25.50
   ```

5. **Expected output:**
   ```
   📤 Sending card payment request for RM25.50
   🆔 Transaction ID: TXN1705123456789
   ✅ Payment request sent to POS terminal
   ```

6. **Wait for POS response** (in a real scenario, this would come from a connected POS terminal)

### Payment Method Test Sequence

Test all payment methods in sequence:

```
1. Card Payment (amount: 10.00)
   - Select option 1
   - Enter: 10.00
   - Verify: Transaction ID generated

2. BNPL (amount: 20.00)
   - Select option 2
   - Enter: 20.00
   - Verify: Correct payment mode sent

3. DuitNow QR (amount: 15.50)
   - Select option 3
   - Enter: 15.50
   - Verify: DuitNow QR request sent

4. IPP (amount: 100.00)
   - Select option 4
   - Enter: 100.00
   - Wait for plan selection if POS responds with plans
```

### Transaction Cancellation Test

1. **Initiate a payment:**
   ```
   Select option (1-7): 1
   Enter amount (RM): 50.00
   ```

2. **Before POS responds, select option 5:**
   ```
   Select option (1-7): 5
   ```

3. **Expected output:**
   ```
   🚫 Cancelling transaction: TXN1705123456789
   ✅ Cancel request sent to POS terminal
   ```

### Status Display Test

1. **Select option 6** from the main menu

2. **Expected output:**
   ```
   📊 Status:
   🔗 Connected POS terminals: 1
   🆔 Current transaction: TXN1705123456789
   👂 Listening for responses: True
   🏪 Kiosk ID: KIOSK001
   ```

## Testing Scenarios

### Scenario 1: Single POS Connection

**Setup:**
1. Start kiosk server (port 8080)
2. Connect one POS terminal to the server

**Test Steps:**
1. Send card payment (RM 25.00)
2. POS should acknowledge with "processing" status
3. POS should respond with transaction result
4. Verify status display shows 1 connected terminal

**Expected Results:**
- Message flow completes without errors
- Transaction ID is generated correctly
- Status is updated in real-time

### Scenario 2: Multiple POS Connections

**Setup:**
1. Start kiosk server (port 8080)
2. Connect multiple POS terminals to the server

**Test Steps:**
1. Send payment request
2. Verify broadcast to all connected terminals
3. Handle responses from multiple terminals

**Expected Results:**
- Status displays correct number of connected terminals
- Requests are broadcast to all terminals
- Each terminal can respond independently

### Scenario 3: IPP Plan Selection

**Setup:**
1. Start kiosk server
2. Connect POS terminal capable of IPP

**Test Steps:**
1. Select option 4 (IPP Payment)
2. Enter amount (e.g., 100.00)
3. Wait for POS to respond with available plans
4. Display and select from available plans
5. Verify plan selection is sent back

**Expected Results:**
```
💰 Amount: RM100.00
📋 Available Installment Plans:
--------------------------------------------------
1. Plan ID: IPP_3M
   Frequency: Monthly
   Total Installments: 3
   Installment Details:
     #1: RM35.00 on 2024-02-15
       Fee: RM1.50 (1.5%)
     #2: RM35.00 on 2024-03-15
       Fee: RM1.50 (1.5%)
     #3: RM35.00 on 2024-04-15
       Fee: RM1.50 (1.5%)

Select plan (1-3) or 'q' to quit: 1
✅ Selected Plan: IPP_3M
📤 Sending plan selection: IPP_3M
✅ Plan selection sent to terminal
```

### Scenario 4: Transaction with Various Amounts

Test transactions with different amount ranges:

| Amount | Purpose | Notes |
|--------|---------|-------|
| 0.01 | Minimum | Test handling of smallest amount |
| 10.00 | Small | Typical small transaction |
| 99.99 | Standard | Most common transaction size |
| 999.99 | Large | Test larger amounts |
| 5000.00 | Maximum | Test handling of max amounts |

## Connection Testing

### Check Server Status

**Using telnet (available on most systems):**
```bash
telnet <kiosk-ip> 8080

# Expected response:
# Connected to <kiosk-ip>
# Escape character is '^]'.
```

**Using netcat (if available):**
```bash
nc -zv <kiosk-ip> 8080

# Expected response:
# Connection to <kiosk-ip> port 8080 [tcp/*] succeeded!
```

### Verify Network Connectivity

```bash
# Ping the kiosk server
ping <kiosk-ip>

# Expected response:
# PING <kiosk-ip> (<ip-address>): 56 data bytes
# 64 bytes from <ip-address>: icmp_seq=0 ttl=64 time=2.123 ms
```

### Monitor Live Connections

While the kiosk server is running, you can:
1. Select option 6 (Show Status) to see connected terminals
2. Check console output for connection events:
   ```
   🔗 Client connected from 192.168.1.50:54321
   📨 Received from 192.168.1.50: {...}
   🔌 Client 192.168.1.50 disconnected
   ```

## Security Testing

The system automatically validates the following security aspects:

### 1. Message Signature Validation

- All received messages are verified using HMAC-SHA256
- The signature is calculated over the sorted payload JSON
- Invalid signatures trigger security validation failures

**Test:** POS Terminal should use the shared secret `POS-KIOSK-SECRET-KEY-2024` when signing messages.

### 2. Nonce Validation

- Each message includes a unique UUID v4 nonce
- Nonces are tracked to prevent replay attacks
- Duplicate nonces are rejected

**Test Output:**
```
🔐 Signature verification PASSED:
   ✅ Signature matches expected value
   📨 Signature: a1b2c3d4e5f6...xxxxxxxx
```

### 3. Timestamp Validation

- Timestamps must be within a 60-second window
- Timestamps are in milliseconds since epoch
- Requests outside the window are rejected

**Test Output:**
```
🕐 Timestamp validation - Request: 1705123456789, Current: 1705123458000, Diff: 1211ms
✅ Timestamp valid: Within 60 second window
```

### Security Failure Examples

**Invalid Signature:**
```
🔐 Signature verification FAILED:
   📨 Received signature: xxxx...
   🔑 Expected signature: yyyy...
   ❌ Signatures match: False
🔒 Security validation failed: Invalid signature
```

**Expired Timestamp:**
```
❌ Timestamp failed: Request too old/new (diff: 65000ms > 60000ms)
🔒 Security validation failed: Request expired or invalid timestamp
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:**
```
❌ Failed to start server: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using the port
lsof -i :8080

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or use a different port when starting kiosk.py
# When prompted, enter a different port number (e.g., 8081)
```

#### 2. Permission Denied

**Error:**
```
❌ Failed to start server: [Errno 13] Permission denied
```

**Solution:**
- Use a port number > 1024 (privileged ports like 80, 443, 8000-8100 may require admin)
- On Linux/macOS, prefix with `sudo` if needed (not recommended for security reasons)
- Choose a port in the range 8080-9999

#### 3. No POS Connection

**Symptom:**
```
❌ No POS terminals connected
```

**Solution:**
1. Verify POS terminal network settings
2. Ensure correct IP address and port from kiosk startup message
3. Check local network connectivity:
   ```bash
   ping <kiosk-ip>
   ```
4. Verify firewall settings allow traffic on the port
5. Test port accessibility:
   ```bash
   telnet <kiosk-ip> 8080
   ```

#### 4. Signature Validation Failed

**Error:**
```
🔒 Security validation failed: Invalid signature
```

**Solution:**
- Verify shared secret key matches on both sides: `POS-KIOSK-SECRET-KEY-2024`
- Check message format integrity (JSON must be valid)
- Ensure proper JSON encoding (UTF-8)
- Verify payload is sorted by keys before signing

#### 5. Invalid JSON Format

**Error:**
```
❌ JSON decode error: [error message]
```

**Solution:**
- Ensure messages are valid JSON
- Check for proper quote escaping
- Verify newline at end of message (`\n`)
- Use JSON validators to check message format

### Debugging with Logs

**Capture detailed output to a file:**
```bash
python3 kiosk.py 2>&1 | tee kiosk.log
```

**This creates a `kiosk.log` file with:**
- 🔗 Connection events
- 📨 Message exchanges
- 🔐 Security validations
- 💳 Payment processing status
- ❌ Error conditions

**Analyze the log file:**
```bash
# View the log
cat kiosk.log

# Search for errors
grep "❌" kiosk.log

# Search for security events
grep "🔐" kiosk.log
```

### Performance Testing

For production environments, consider testing:

1. **Multiple concurrent POS connections:**
   - Start 5-10 simulated POS terminals
   - Send payment requests from each
   - Monitor memory usage and response time

2. **High-frequency payment requests:**
   - Send 100+ payment requests rapidly
   - Verify all are processed correctly
   - Check for dropped or duplicate messages

3. **Network interruption handling:**
   - Simulate POS disconnections
   - Verify graceful cleanup
   - Check connection recovery

4. **Memory usage under load:**
   - Run for extended period with continuous traffic
   - Monitor nonce storage size
   - Verify periodic cleanup is working

### Example Python Test Client

For testing purposes, here's a minimal POS client example:

```python
import socket
import json
import hmac
import hashlib
import uuid
from datetime import datetime

def create_test_response(txn_id):
    """Create a test acknowledgment response"""
    secret = "POS-KIOSK-SECRET-KEY-2024"

    payload = {
        "type": "ack",
        "txn_id": txn_id,
        "status": "processing",
        "timestamp": str(int(datetime.now().timestamp() * 1000)),
        "nonce": str(uuid.uuid4())
    }

    # Create signature
    json_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    signature = hmac.new(
        secret.encode('utf-8'),
        json_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return {
        "payload": payload,
        "signature": signature
    }

# Connect to kiosk
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.100', 8080))

# Receive payment request
data = sock.recv(4096)
request = json.loads(data.decode('utf-8'))
txn_id = request['payload']['txn_id']

# Send acknowledgment
response = create_test_response(txn_id)
sock.send(json.dumps(response).encode('utf-8') + b'\n')

sock.close()
```

---

**Note:** For API specifications and integration architecture details, refer to `INTEGRATION.md`
