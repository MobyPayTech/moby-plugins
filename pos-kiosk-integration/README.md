# MobyPay POS-KIOSK Integration

This project provides a secure TCP communication system for MobyPay Kiosk integration with Point of Sale (POS) terminals. The system enables kiosks to send payment requests to POS terminals and handle various payment methods including card payments, Buy Now Pay Later (BNPL), DuitNow QR, and Installment Payment Plans (IPP).

## 📋 Table of Contents
- [Features](#features)
- [Security](#security)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Payment Methods](#payment-methods)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **Secure TCP Communication**: HMAC-SHA256 message signing with nonce validation
- **Multiple Payment Methods**: Card, BNPL, DuitNow QR, and IPP support
- **Real-time Transaction Processing**: Instant communication between kiosk and POS
- **IPP Plan Selection**: Interactive installment plan selection for banking payments
- **Connection Management**: Automatic handling of multiple POS terminal connections
- **Transaction Lifecycle Management**: Complete payment flow from request to completion
- **Replay Attack Protection**: Nonce-based security to prevent message replay
- **Timestamp Validation**: Time-based request validation (60-second window)

## 🔒 Security

The system implements multiple security layers:

- **Message Signing**: All messages are signed using HMAC-SHA256
- **Nonce Validation**: Unique identifiers prevent replay attacks  
- **Timestamp Validation**: Requests must be within 60-second window
- **Secure Key Management**: Shared secret for message authentication
- **Connection Validation**: Secure client-server handshake

## 📋 Requirements

- Python 3.7 or higher
- Network connectivity between kiosk and POS terminals
- Open TCP port for communication (default: 8080)

## 🚀 Installation

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

### 4. No Additional Dependencies Required

The kiosk system uses only Python standard library modules:
- `socket` - TCP communication
- `json` - Message formatting
- `threading` - Concurrent connection handling
- `hashlib` & `hmac` - Security and message signing
- `uuid` - Nonce generation
- `datetime` - Timestamp validation

## 🎯 Usage

### Starting the Kiosk Server

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

### Interactive Menu Options

Once the server is running, you'll see the following menu:

```
📋 Available Commands:
1. 💳 Card Payment
2. 🛒 Buy Now Pay Later (BNPL)
3. 📱 DuitNow QR
4. 🏦 Installment Payment (IPP)
5. 🚫 Cancel Transaction
6. ℹ️  Show Status
7. 🔴 Exit
```

### Making a Payment

1. **Select payment method** (1-4)
2. **Enter amount** when prompted: `Enter amount (RM): 50.00`
3. **Wait for POS connection** and transaction processing
4. **For IPP payments**: Select installment plan when prompted

### Example Payment Flow

```bash
Select option (1-7): 1
Enter amount (RM): 25.50
📤 Sending card payment request for RM25.50
🆔 Transaction ID: TXN1705123456789
✅ Payment request sent to POS terminal
✅ Payment acknowledged by POS: processing
💳 Payment Result: success
🎉 Payment Successful!
🔑 Auth Code: ABC123
💳 Card: **** **** **** 1234
```

## 💳 Payment Methods

### 1. Card Payment
- Direct card transactions through POS terminal
- Supports credit and debit cards
- Real-time authorization

### 2. Buy Now Pay Later (BNPL)
- Installment-based payment options
- Flexible payment terms
- Instant approval process

### 3. DuitNow QR
- Malaysia's national QR payment system
- Bank and e-wallet integration
- Quick and secure transactions

### 4. Installment Payment Plans (IPP)
- Available for MobyPay BNPL account holders
- Flexible installment payment options
- Interactive plan selection
- Detailed installment breakdown with fees

#### IPP Plan Selection Example:
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
```

## 📡 API Documentation

### Message Format

All messages use the following secure format:

```json
{
  "payload": {
    "type": "transaction_request",
    "txn_id": "TXN1705123456789",
    "amount": 50.00,
    "payment_mode": "card",
    "kiosk_id": "KIOSK001",
    "timestamp": "1705123456789",
    "nonce": "uuid-v4-string"
  },
  "signature": "hmac-sha256-signature"
}
```

### Request Types

1. **Transaction Request**
   ```json
   {
     "type": "transaction_request",
     "txn_id": "unique-transaction-id",
     "amount": 100.00,
     "payment_mode": "card|bnpl|duitnow_qr|ipp",
     "kiosk_id": "KIOSK001"
   }
   ```

2. **Cancel Transaction**
   ```json
   {
     "type": "cancel_transaction",
     "txn_id": "transaction-id-to-cancel",
     "kiosk_id": "KIOSK001"
   }
   ```

3. **IPP Plan Selection**
   ```json
   {
     "type": "ipp_plan_selection",
     "txn_id": "transaction-id",
     "plan_id": "selected-plan-id",
     "kiosk_id": "KIOSK001"
   }
   ```

### Response Types

1. **Acknowledgment**
   ```json
   {
     "type": "ack",
     "txn_id": "transaction-id",
     "status": "processing|received"
   }
   ```

2. **Transaction Result**
   ```json
   {
     "type": "transaction_result",
     "txn_id": "transaction-id",
     "status": "success|failed|ipp_plans",
     "authorization_code": "AUTH123",
     "card_last4": "1234",
     "plans": [...] // Only for IPP
   }
   ```

## 🧪 Testing

### Manual Testing

1. **Start the kiosk server:**
   ```bash
   python3 kiosk.py
   ```

2. **Test different payment methods:**
   - Try each payment option (1-4)
   - Test with various amounts
   - Test transaction cancellation
   - Verify status information

### Connection Testing

1. **Check server status:**
   - Use option 6 to view connection status
   - Verify POS terminal connections
   - Monitor transaction states

2. **Network connectivity:**
   ```bash
   # Test if port is accessible
   telnet <kiosk-ip> 8080
   
   # Or using netcat
   nc -zv <kiosk-ip> 8080
   ```

### Security Testing

The system automatically validates:
- Message signatures (HMAC-SHA256)
- Nonce uniqueness (replay attack prevention)
- Timestamp validity (60-second window)
- Message format integrity

### Load Testing

For production environments, consider testing:
- Multiple concurrent POS connections
- High-frequency payment requests
- Network interruption handling
- Memory usage under load

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```
   Error: [Errno 48] Address already in use
   ```
   **Solution:** Use a different port or stop the process using the port:
   ```bash
   # Find process using the port
   lsof -i :8080
   
   # Kill the process (replace PID)
   kill -9 <PID>
   ```

2. **Permission Denied**
   ```
   Error: [Errno 13] Permission denied
   ```
   **Solution:** Use a port number > 1024 or run with appropriate permissions

3. **No POS Connection**
   ```
   ❌ No POS terminals connected
   ```
   **Solution:** 
   - Verify POS terminal network settings
   - Ensure correct IP address and port
   - Check local network connectivity

4. **Signature Validation Failed**
   ```
   🔒 Security validation failed: Invalid signature
   ```
   **Solution:**
   - Verify shared secret key matches on both sides
   - Check message format integrity
   - Ensure proper JSON encoding

### Network Configuration

**Local Network Setup:**
- System operates within local network environment
- Ensure kiosk and POS terminals are on the same network
- Use local IP addresses (e.g., 192.168.1.x)
- Default port 8080 should be accessible within local network

**Network Requirements:**
- Configure static IP for the kiosk if needed
- Ensure network connectivity between devices

### Logging and Debugging

The application provides detailed console output:
- 🔗 Connection events
- 📨 Message exchanges  
- 🔐 Security validations
- 💳 Payment processing status
- ❌ Error conditions

For additional debugging, modify the logging level in the code or redirect output:
```bash
python3 kiosk.py 2>&1 | tee kiosk.log
```

## 📞 Support

For technical support or questions about the POS-KIOSK integration:

1. **Check the documentation:** `POS - KIOSK Integration.pdf`
2. **Review the source code:** `kiosk.py`
3. **Test network connectivity** between kiosk and POS terminals
4. **Verify security configurations** and shared secrets

## 📄 Files in This Directory

- `README.md` - This documentation file
- `kiosk.py` - Main Python application for kiosk TCP server
- `POS - KIOSK Integration.pdf` - Detailed technical documentation

---

**Note:** This is a secure payment integration system. Always ensure proper security measures are in place in production environments, including network encryption, access controls, and audit logging.