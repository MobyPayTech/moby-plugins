# MobyPay POS-KIOSK Integration Guide

This guide covers the integration architecture, communication protocols, and API specifications for integrating with the MobyPay Kiosk system.

## 📋 Table of Contents

- [Overview](#overview)
- [Security Architecture](#security-architecture)
- [System Architecture](#system-architecture)
- [Payment Methods](#payment-methods)
- [API Documentation](#api-documentation)
- [Message Format](#message-format)
- [Integration Workflow](#integration-workflow)
- [Network Configuration](#network-configuration)

## Overview

The MobyPay POS-KIOSK integration enables secure TCP-based communication between kiosk terminals and Point of Sale (POS) systems. The system supports multiple payment methods including card payments, Buy Now Pay Later (BNPL), DuitNow QR, and Installment Payment Plans (IPP).

### Key Features

- **Secure TCP Communication**: HMAC-SHA256 message signing with nonce validation
- **Multiple Payment Methods**: Card, BNPL, DuitNow QR, and IPP support
- **Real-time Transaction Processing**: Instant communication between kiosk and POS
- **Replay Attack Protection**: Nonce-based security to prevent message replay
- **Timestamp Validation**: Time-based request validation (60-second window)

## 🔒 Security Architecture

### Message Signing

All messages are signed using HMAC-SHA256. The signature is calculated over the payload JSON after:
1. Sorting keys alphabetically
2. Using compact separators (`,` for array/object elements, `:` for key-value pairs)
3. Encoding with UTF-8

**Shared Secret:** `POS-KIOSK-SECRET-KEY-2024`

### Nonce Validation

- Unique nonce (UUID v4) is included in every message
- Each nonce can only be used once (prevents replay attacks)
- Nonces are tracked server-side; old nonces are cleared periodically

### Timestamp Validation

- Timestamps are in milliseconds since epoch
- Requests must be within 60-second window from current time
- Protects against time-shifted replay attacks

### Validation Sequence

1. Verify message structure (payload and signature present)
2. Verify HMAC-SHA256 signature matches
3. Validate nonce uniqueness
4. Validate timestamp within acceptable range

## System Architecture

```
┌─────────────────┐                    ┌─────────────────┐
│   Kiosk         │ ←→ TCP (8080)  ←→  │  POS Terminal   │
│   Server        │   (Secure)         │                 │
│                 │                    │                 │
│ - Listener      │                    │ - Parser        │
│ - Sender        │                    │ - Responder     │
│ - Handler       │                    │ - Processor     │
└─────────────────┘                    └─────────────────┘
```

### Component Responsibilities

**Kiosk Server:**
- Listen for incoming POS terminal connections
- Send payment requests to connected terminals
- Receive and process transaction responses
- Manage multiple concurrent connections
- Handle IPP plan selection

**POS Terminal Client:**
- Connect to kiosk server
- Receive payment requests
- Process transactions
- Send responses with results
- Provide IPP plans when applicable

## 💳 Payment Methods

### 1. Card Payment
- Direct card transactions through POS terminal
- Supports credit and debit cards
- Real-time authorization
- Payment Mode: `card`

### 2. Buy Now Pay Later (BNPL)
- Installment-based payment options
- Flexible payment terms
- Instant approval process
- Payment Mode: `bnpl`

### 3. DuitNow QR
- Malaysia's national QR payment system
- Bank and e-wallet integration
- Quick and secure transactions
- Payment Mode: `duitnow_qr`

### 4. Installment Payment Plans (IPP)
- Available for MobyPay BNPL account holders
- Flexible installment payment options
- Interactive plan selection via kiosk
- Payment Mode: `ipp`

## 📡 API Documentation

### Message Format

All messages follow this secure envelope format:

```json
{
  "payload": {
    "type": "message_type",
    "txn_id": "unique-transaction-id",
    "timestamp": "milliseconds-since-epoch",
    "nonce": "uuid-v4-string",
    "kiosk_id": "KIOSK001",
    ... other fields depending on message type
  },
  "signature": "hmac-sha256-hex-digest"
}
```

### Request Types

#### 1. Transaction Request

Sent by kiosk to initiate a payment transaction.

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

**Fields:**
- `txn_id` (string): Unique transaction identifier (format: TXN + timestamp in milliseconds)
- `amount` (number): Transaction amount in RM
- `payment_mode` (string): One of `card`, `bnpl`, `duitnow_qr`, `ipp`
- `kiosk_id` (string): Identifier of the kiosk terminal

#### 2. Cancel Transaction

Sent by kiosk to cancel an ongoing transaction.

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

Sent by kiosk to select a specific installment plan.

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

**Fields:**
- `plan_id` (string): ID of the selected installment plan from the available plans

### Response Types

#### 1. Acknowledgment

Sent by POS to acknowledge receipt of a request.

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

**Status Values:**
- `received`: Request has been received
- `processing`: Request is being processed

#### 2. Transaction Result

Sent by POS with the final transaction result.

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

**Status Values:**
- `success`: Transaction completed successfully
- `failed`: Transaction failed
- `approved`: Transaction approved (alternative to success)
- `ipp_plans`: IPP plans available for selection

**For IPP Responses:**

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
          {
            "installmentNumber": 1,
            "date": "2024-02-15",
            "amount": 35.00,
            "installmentFee": 1.50,
            "installmentFeePercentage": 1.5
          },
          {
            "installmentNumber": 2,
            "date": "2024-03-15",
            "amount": 35.00,
            "installmentFee": 1.50,
            "installmentFeePercentage": 1.5
          },
          {
            "installmentNumber": 3,
            "date": "2024-04-15",
            "amount": 35.00,
            "installmentFee": 1.50,
            "installmentFeePercentage": 1.5
          }
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

Sent by POS when an error occurs.

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

## Integration Workflow

### Standard Payment Flow

```
Kiosk                           POS Terminal
  │                               │
  ├─── Transaction Request ──────→│
  │                               │
  │←─── Acknowledgment (ACK) ─────┤
  │                               │
  │       [Processing]            │
  │                               │
  │←─Transaction Result (Success)─│
  │                               │
  └─── Display Result ───────────→│
```

### IPP Payment Flow

```
Kiosk                           POS Terminal
  │                               │
  ├─── Transaction Request (IPP)─→│
  │                               │
  │←─── Acknowledgment (ACK) ─────┤
  │                               │
  │       [Processing]            │
  │                               │
  │←─ Transaction Result (Plans)──│
  │                               │
  ├─ Display IPP Plans ──────────→│
  │ (User selects plan)           │
  │                               │
  ├─── Plan Selection ───────────→│
  │                               │
  │←─── Acknowledgment (ACK) ─────┤
  │                               │
  │       [Processing]            │
  │                               │
  │←─Transaction Result (Success)─│
  │                               │
  └─── Display Result ───────────→│
```

### Error Handling Flow

```
Kiosk                           POS Terminal
  │                               │
  ├─── Transaction Request ──────→│
  │                               │
  │←─── Error Response ───────────│
  │                               │
  └─── Display Error ────────────→│
```

### Transaction Cancellation Flow

```
Kiosk                           POS Terminal
  │                               │
  ├─ Cancel Transaction Request ──│
  │                               │
  │←─── Acknowledgment (ACK) ─────┤
  │                               │
  └─── Transaction Cancelled ────→│
```

## Network Configuration

### Requirements

- Network connectivity between kiosk and POS terminals
- Open TCP port for communication (default: 8080)
- Shared secret key for message authentication
- Synchronized clocks (within 60-second tolerance)

### Local Network Setup

- System operates within local network environment
- Kiosk and POS terminals must be on the same network
- Use local IP addresses (e.g., 192.168.1.x)
- Default port 8080 should be accessible within local network

### Connection Validation

- Secure client-server handshake on connection establishment
- Message signature validation on all communications
- Automatic cleanup of inactive connections
- Support for multiple concurrent POS terminal connections

### Recommended Configuration

- **Kiosk IP**: Static local IP address (e.g., 192.168.1.100)
- **Port**: 8080 (customizable during startup)
- **Timeout**: 60-second window for message timestamp validation
- **Nonce Storage**: In-memory with periodic cleanup after 1000 entries

---

**Note:** For implementation examples and testing procedures, refer to `TESTING.md`
