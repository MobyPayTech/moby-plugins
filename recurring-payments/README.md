# MobyPay Recurring API Documentation 📚

## Table of Contents

- [Introduction](#introduction)
- [Base URLs](#base-urls)
- [Rate Limiting](#rate-limiting)
- [API Versioning](#api-versioning)
- [API Routes](#api-routes)
  - [POST /api/auth/token](#post-apiauthtoken)
  - [GET /api/v2/tokens](#get-apiv2tokens)
  - [POST /api/v2/tokens](#post-apiv2tokens)
  - [DELETE /api/v2/tokens/{token}](#delete-apiv2tokenstoken)
  - [POST /api/v2/tokens/{token}/charges](#post-apiv2tokenstokencharges)
  - [GET /api/v2/charges/{order_reference}](#get-apiv2chargesorder_reference)
  - [POST /api/v2/charges/{order_reference}/refund](#post-apiv2chargesorder_referencerefund)
- [Error Handling](#error-handling)
- [Implementation Notes](#implementation-notes)

---

## 🚀 Introduction

This documentation provides comprehensive information about MobyPay's recurring payment processing API. It covers card tokenization, token management, transaction processing, and refunds.

> **Note:** All monetary amounts are in **MYR (Malaysian Ringgit)** unless otherwise specified.

---

## 🌐 Base URLs

All API endpoints must be prefixed with the appropriate base URL depending on your environment:

| Environment | Base URL |
|-------------|----------|
| Sandbox | `https://dev-pay-refactor.mobycheckout.com/` |
| Production | `https://pay.mobycheckout.com/` |

> ⚠️ Always test your integration thoroughly in the **Sandbox** environment before switching to **Production**.

---

## ⏱️ Rate Limiting

To ensure service stability, the API enforces rate limits. Exceeding these limits will result in an HTTP **429 Too Many Requests** response.

| Limit Type | Limit |
|------------|-------|
| Authentication requests | 10 requests per minute per client |
| General API requests | 60 requests per minute per token |

When you receive a 429 response, wait before retrying. The response will include a `Retry-After` header indicating when you may resume requests.

```json
{
  "success": false,
  "error": "TOO_MANY_REQUESTS",
  "message": "Rate limit exceeded. Please retry after 30 seconds."
}
```

---

## 🔖 API Versioning

The current API version is **v2** (indicated by the `/v2/` path prefix).

> **Note:** If you are using a previous integration without the `/v2/` prefix, please contact Merchant Support to discuss migration to the current API version.

---

## 🔐 API Routes

### POST /api/auth/token

Authenticates a merchant and generates a bearer token for accessing protected API endpoints.

**🔗 URL**
```
POST /api/auth/token
```

**📋 Headers**
```
Content-Type: application/json
Accept: application/json
```

**📝 Request Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| clientId | string | Yes | Merchant's client ID provided during onboarding |
| secretKey | string | Yes | Secret key provided during onboarding |
| scope | string | No | Access scope (default: 'pay') |

**📦 Sample Request**
```bash
curl -X POST https://dev-pay-refactor.mobycheckout.com/api/auth/token \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "clientId": "MOBY00000123",
    "secretKey": "a2DQqfwUoxf6ZeTDbuki7MNoAp0j2z"
  }'
```

**✅ Success Response (200 OK)**
```json
{
  "status": "success",
  "success": true,
  "msg": "Authentication success",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expired_at": "2025-04-25 15:14:24",
  "scope": "pay"
}
```

**❌ Error Response**
```json
{
  "success": false,
  "error": "BAD_REQUEST",
  "msg": "Incorrect credentials!"
}
```

**🧠 Notes**
- Token validity: **30 minutes (1800 seconds)**
- Include the token in the Authorization header as a Bearer token for all protected endpoints: `Authorization: Bearer <token>`
- Expired tokens will return `401 Unauthorized` responses.

---

### GET /api/v2/tokens

Retrieves a paginated list of saved card tokens for a merchant's customers, optionally filtered by customer information.

**🔗 URL**
```
GET /api/v2/tokens
```

**📋 Headers**
```
Authorization: Bearer {api_token}
Content-Type: application/json
Accept: application/json
```

**📝 Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| client_id | string | Yes | Merchant's client ID |
| name | string | No | Filter tokens by customer name (partial match) |
| email | string | No | Filter tokens by customer email (partial match) |
| mobile | string | No | Filter tokens by customer mobile number (partial match) |
| page | int | No | Page number for pagination |
| per_page | int | No | Number of results per page |

**📦 Example Request**
```bash
curl -X GET "https://dev-pay-refactor.mobycheckout.com/api/v2/tokens?client_id=MOBY00000123&email=john@example.com" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json"
```

**✅ Success Response (200 OK)**
```json
{
  "success": true,
  "current_page": 1,
  "per_page": 15,
  "total": 2,
  "last_page": 1,
  "data": [
    {
      "provider": null,
      "type": null,
      "token": "b1df18d393e0610af46e5b1d7d5be79ccb596c2fe1546facd2723ec6956ad0e9",
      "firstSix": "512345",
      "lastFour": "0008",
      "expiryYearMonth": "0139",
      "customer": {
        "name": "John Doe",
        "email": "john@example.com",
        "mobile": "60123456789"
      }
    }
  ]
}
```

**❌ Error Response**
```json
{
  "success": false,
  "error": "Invalid client id"
}
```

**🧠 Notes**
- A valid Bearer token is required. Requests without proper authentication will return `401 Unauthorized`.
- Requests from unauthorized merchants will return `403 Forbidden`.

---

### POST /api/v2/tokens

Initiates the process to create a new card token for a customer. Returns a URL where the customer can securely enter their card details.

**🔗 URL**
```
POST /api/v2/tokens
```

**📋 Headers**
```
Authorization: Bearer {api_token}
Content-Type: application/json
Accept: application/json
```

**📝 Request Body**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| client_id | string | Yes | Merchant's client ID |
| customer_email | string | Yes | Customer's email address |
| customer_name | string | Yes | Customer's full name |
| customer_mobile | string | Yes | Customer's mobile number |

**📦 Sample Request**
```bash
curl -X POST https://dev-pay-refactor.mobycheckout.com/api/v2/tokens \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "client_id": "MOBY00000123",
    "customer_email": "john@example.com",
    "customer_name": "John Doe",
    "customer_mobile": "60123456789"
  }'
```

**✅ Success Response (201 Created)**
```json
{
  "success": true,
  "redirect_url": "https://dev-pay-refactor.mobycheckout.com/mpgs/save-card?merchantId=MOBY00000123&customerName=John%20Doe&customerEmail=john@example.com&customerMobile=60123456789"
}
```

Redirect the customer to the returned `redirect_url` to complete card entry and tokenization.

**❌ Error Response**
```json
{
  "success": false,
  "error": "Invalid customer information"
}
```

**🧠 Notes**
- A valid Bearer token is required. Requests without proper authentication will return `401 Unauthorized`.
- Requests from unauthorized merchants will return `403 Forbidden`.

---

### DELETE /api/v2/tokens/{token}

Deletes a saved card token.

**🔗 URL**
```
DELETE /api/v2/tokens/{token}
```

**📋 Headers**
```
Authorization: Bearer {api_token}
Content-Type: application/json
Accept: application/json
```

**📝 Request Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| token | string | Yes | Token identifier to delete (path parameter) |
| client_id | string | Yes | Client ID (query parameter) |

**📦 Sample Request**
```bash
curl -X DELETE "https://dev-pay-refactor.mobycheckout.com/api/v2/tokens/{token}?client_id=MOBY00000123" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"
```

**✅ Success Response (200 OK)**
```json
{
  "success": true,
  "message": "Token deleted successfully"
}
```

**❌ Error Response**
```json
{
  "success": false,
  "error": "Token not found"
}
```

**🧠 Notes**
- A valid Bearer token is required. Requests without proper authentication will return `401 Unauthorized`.
- Requests from unauthorized merchants will return `403 Forbidden`.

---

### POST /api/v2/tokens/{token}/charges

Processes a payment using a previously tokenized card. Supports both 3DS (3-D Secure) and non-3DS flows.

**🔗 URL**
```
POST /api/v2/tokens/{token}/charges
```

**📋 Headers**
```
Authorization: Bearer {api_token}
Content-Type: application/json
Accept: application/json
```

**📝 Request Body**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| client_id | string | Yes | Client ID |
| amount | number | Yes | Amount to charge in MYR (minimum: 0) |
| order_reference | string | Yes | Unique order reference for this transaction |
| merchant_reference | string | No | Optional merchant-specific reference |
| return_url | string | No | URL to redirect after transaction completion |
| callback_url | string | No | URL to receive transaction webhook notifications |
| skip_receipt | boolean | No | Whether to skip sending receipt emails |
| details | string | No | Transaction details or description |
| custom_data | string | No | Custom metadata for the transaction (JSON string) |
| 3ds | boolean | Yes | Whether to require 3D Secure authentication (true or false) |

**📦 Sample Request**
```bash
curl -X POST "https://dev-pay-refactor.mobycheckout.com/api/v2/tokens/{token}/charges" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "client_id": "MOBY00000123",
    "amount": 100.50,
    "order_reference": "ORDER-REF-123456",
    "merchant_reference": "MERCHANT-REF-7890",
    "return_url": "https://merchant.com/payment-complete",
    "callback_url": "https://merchant.com/webhook",
    "skip_receipt": false,
    "details": "Payment for Order #123456",
    "custom_data": "{\"order_id\":\"123456\",\"product_id\":\"PRD123\"}",
    "3ds": true
  }'
```

**✅ Success Response (200 OK)**

If `3ds` is `true`:
```json
{
  "success": true,
  "redirect_url": "https://secure-3ds-provider.com/authenticate?ref=xyz"
}
```
Redirect your customer to the `redirect_url` to complete 3DS authentication.

If `3ds` is `false`:
```json
{
  "success": true,
  "message": "Successfully charged",
  "data": {
    "referenceNo": "ref-2q134e32",
    "merchantId": "MOBY123",
    "status": "pending",
    "amount": 100,
    "payAt": "2025-02-01",
    "createdAt": "2025-02-01",
    "customer": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "60123456789"
    },
    "transactions": [
      {
        "transactionId": "1q23",
        "status": "pending",
        "amount": 100,
        "payMethod": "MPGS",
        "payAt": "2025-02-01",
        "createdAt": "2025-02-01"
      }
    ]
  }
}
```

**❌ Error Response**
```json
{
  "success": false,
  "error": "DECLINED - Do not honor",
  "message": "05 - Do not honor",
  "data": null
}
```

**🧠 Notes**
- When `3ds` is `true`, redirect the customer to the returned `redirect_url` to complete authentication.
- When `3ds` is `false`, the response includes the charge data directly.
- A valid Bearer token is required. Requests without proper authentication will return `401 Unauthorized`.
- Requests from unauthorized merchants will return `403 Forbidden`.

---

### GET /api/v2/charges/{order_reference}

Checks the status of a previously initiated token charge transaction.

**🔗 URL**
```
GET /api/v2/charges/{order_reference}
```

**📋 Headers**
```
Authorization: Bearer {api_token}
Content-Type: application/json
Accept: application/json
```

**📝 Request Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| order_reference | string | Yes | Order reference used in the original charge (path parameter) |
| client_id | string | Yes | Client ID (query parameter) |

**📦 Sample Request**
```bash
curl -X GET "https://dev-pay-refactor.mobycheckout.com/api/v2/charges/ORDER-REF-123456?client_id=MOBY00000123" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json"
```

**✅ Success Response (200 OK)**
```json
{
  "success": true,
  "message": "Charge Success",
  "data": {
    "result": "SUCCESS",
    "response": {
      "gatewayCode": "APPROVED",
      "acquirerCode": "00",
      "acquirerMessage": "Approved",
      "transaction": {
        "id": "TXN-035134a9-4580-43fc-b106-981cfb4968c4",
        "amount": 100.50,
        "currency": "MYR",
        "timeOfRecord": "2025-04-25T12:34:56.000Z"
      }
    }
  }
}
```

**❌ Error Response**
```json
{
  "success": false,
  "error": "DECLINED - Do not honor",
  "message": "05 - Do not honor",
  "data": {
    "result": "ERROR",
    "response": {
      "gatewayCode": "DECLINED",
      "gatewayRecommendation": "Do not honor",
      "acquirerCode": "05",
      "acquirerMessage": "Do not honor"
    }
  }
}
```

**🧠 Notes**
- A valid Bearer token is required. Requests without proper authentication will return `401 Unauthorized`.
- Requests from unauthorized merchants will return `403 Forbidden`.

---

### POST /api/v2/charges/{order_reference}/refund

Queues a refund request for a previously successful token charge transaction. The refund is processed asynchronously.

**🔗 URL**
```
POST /api/v2/charges/{order_reference}/refund
```

**📋 Headers**
```
Authorization: Bearer {api_token}
Content-Type: application/json
Accept: application/json
```

**📝 Request Body**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| amount | number | Yes | Amount to refund (must be less than or equal to the original transaction amount) |
| client_id | string | Yes | Client ID |

**📦 Sample Request**
```bash
curl -X POST "https://dev-pay-refactor.mobycheckout.com/api/v2/charges/ORDER-REF-123456/refund" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "amount": 100.50,
    "client_id": "MOBY00000123"
  }'
```

**✅ Success Response (201 Created)**
```json
{
  "success": true,
  "message": "Refund request submitted."
}
```

**❌ Error Responses**

Transaction not found:
```json
{
  "success": false,
  "error": "Transaction not found",
  "data": "Transaction not found"
}
```

Unauthorized (403 Forbidden):
```json
{
  "success": false,
  "error": "Forbidden"
}
```

Validation error:
```json
{
  "success": false,
  "error": "Validation error",
  "message": "The amount field is required.",
  "data": {
    "amount": ["The amount field is required."]
  }
}
```

**🧠 Notes**
- A valid Bearer token is required. Requests without proper authentication will return `401 Unauthorized`.
- The refund is queued for asynchronous processing and may not complete immediately.
- The refund amount cannot exceed the original transaction amount.
- Requests from unauthorized merchants will return `403 Forbidden`.

---

## Error Handling

All endpoints may return the following standard error responses:

| HTTP Code | Error | Description |
|-----------|-------|-------------|
| 400 | Bad Request | Missing or invalid parameters |
| 401 | Unauthorized | Invalid or expired API token |
| 403 | Forbidden | Access denied due to ownership or permissions |
| 404 | Not Found | Transaction or resource not found |
| 422 | Unprocessable Entity | Request validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |

Common error response format:
```json
{
  "success": false,
  "error": "Error message description"
}
```

---

## Implementation Notes

- All monetary amounts must be provided as decimal numbers.
- Default currency: **MYR (Malaysian Ringgit)**
- Authentication is required for all API routes using a Bearer token.
- The web route for saving cards returns an HTML form rather than JSON data.
- Successful transactions trigger email notifications to both customer and merchant unless `skip_receipt` is set to `true`.
- For refunds, the refund amount cannot exceed the original transaction amount.
- Auth tokens expire after **30 minutes**. Implement token refresh logic to handle `401` responses gracefully.

---

## Additional Support

For further assistance, you can reach our support teams:

**Customer Care:**
- Email: customercare@moby.my
- Phone: 011 1111 5155

**Merchant Support:**
- Email: merchantsupport@moby.my
- Phone: 011 1111 7177

[Return to Home](../README.md)
