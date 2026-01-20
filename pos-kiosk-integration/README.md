# MobyPay POS-KIOSK Integration

Secure TCP communication system for MobyPay Kiosk integration with POS terminals. Supports card payments, Buy Now Pay Later (BNPL), DuitNow QR, and Installment Payment Plans (IPP).

## 📚 Documentation

- **[INTEGRATION.md](./INTEGRATION.md)** - API specs, system architecture, security model, and workflows
- **[TESTING.md](./TESTING.md)** - Installation, usage, testing procedures, and troubleshooting
- `kiosk.py` - Reference implementation (TCP server with interactive menu)
- `POS - KIOSK Integration.pdf` - Detailed technical reference

## ✨ Features

- Secure TCP with HMAC-SHA256 signing and nonce validation
- Multiple payment methods (card, BNPL, DuitNow QR, IPP)
- Real-time transaction processing
- Replay attack protection with 60-second timestamp validation
- Multiple concurrent POS connections
- IPP plan selection with installment details

---

**Note:** This is a secure payment integration system. Always ensure proper security measures are in place in production environments, including network encryption, access controls, and audit logging.