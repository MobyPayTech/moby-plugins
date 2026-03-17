# Table of Contents

- [Hosted Payment](#hosted-payment)
- [Verifying the Signature of Calls](#verifying-the-signature-of-calls)
- [Handling Notifications](#handling-notifications)
- [Getting Your Credentials](#getting-your-credentials)

---

# Hosted Payment

A Hosted Payment Page is a secure method through which customers can make online payments. It's a webpage where transaction details are entered and processed. This page is hosted by Moby, thus reducing the risk of security breaches and providing a seamless payment experience for customers. This guide will walk you through how to integrate our Hosted Payment Page into your application.

## Quick Start Guide

Welcome to the Quick Start Guide for Moby Hosted Payment! In just a few simple steps, you'll be ready to integrate our payment solutions into your application and offer your customers a seamless payment experience. Let's get started.

![Moby Hosted Page Workflow](Hosted%20Payment%20Diagrams.webp)

## Moby Hosted Page Workflow

### Step 1: Retrieve Your Authorization Token

To ensure secure transactions, the first step in integrating with Moby Payments is to obtain an authorization token. This token is necessary for authenticating your API requests and is valid for **60 minutes**.

#### How to Retrieve Your Token

Make an API call to the following endpoint:

```
POST /api/auth/token
```

Include your Moby Payments clientID and secretKey. These were provided to you when you registered for an account. The token expires after **60 minutes**.

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| clientID | string | Yes | Your Merchant ID, provided during onboarding |
| secretKey | string | Yes | Your API Key/Secret, provided during onboarding |

#### Example Request

```bash
curl -X POST "[PAYMENT_URL]/api/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"clientID": "your_client_id", "secretKey": "your_client_secret"}'
```

#### Example Response

```json
{
  "status": "success",
  "token": "your_access_token",
  "expired_at": "2025-01-01 13:00:00"
}
```

---

### Step 2: Redirect User to the Payment Page

With the authorization token, create a payment session for your user by specifying the payment details and receiving a payment link in response.

#### Initiate Payment Session

```
POST /api/merchant/payment/checkout/hosted
```

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| clientId | string | Yes | Your Merchant ID |
| customerName | string | Yes | Full name of the customer |
| customerEmail | string | Yes | Customer email address |
| customerMobile | string | Yes | Customer mobile number (e.g. 0111222333) |
| referenceNo | integer | Yes | Your unique order/reference number |
| amount | number | Yes | Payment amount in MYR (e.g. 100.00) |
| returnUrl | string | Yes | URL to redirect the customer after payment |
| callbackUrl | string | Yes | URL to receive server-to-server payment status notifications |
| details | string | No | Additional information or order description |
| cart | array | No | Array of purchased item details |

#### Example Request

```bash
curl -X POST "[PAYMENT_URL]/api/merchant/payment/checkout/hosted" \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId": "YOUR_CLIENT_ID",
    "customerName": "customer name",
    "customerEmail": "customer@example.com",
    "customerMobile": "0111222333",
    "referenceNo": 100,
    "details": "additional information",
    "amount": 100,
    "returnUrl": "https://yourapp.com/payment/complete",
    "callbackUrl": "https://yourapp.com/payment/moby/status",
    "cart": []
  }'
```

---

### Step 3: Complete the Payment

After the customer completes the payment on the Moby Payments page, they are automatically redirected to your returnUrl with the following fields:

#### Example Response

```json
{
  "referenceNo": "Payment Reference",
  "transactionId": "Your Payment ID",
  "amount": "Payment Amount",
  "payMethod": "Payment Method Used By The User",
  "status": "Payment Status",
  "time": "Payment Time (YYYY-MM-DD HH:mm:ss)",
  "merchantOrderRef": "Merchant Order Reference",
  "description": "Payment Description or Status Description",
  "signature": "Request Signature"
}
```

> **Important:** Always verify the signature field before updating your system. See [Verifying the Signature of Calls](#verifying-the-signature-of-calls). Never treat a payment as successful without a valid signature match.

---

## Getting Your Credentials

### Payment URL

Use the appropriate base URL for your environment:

| Environment | Base URL |
|-------------|----------|
| Sandbox | `https://dev.pay.mobycheckout.com` |
| Production | `https://pay.mobycheckout.com` |

> Always test thoroughly in the **Sandbox** environment before switching to **Production**.

### Client ID & Secret Key

Upon completion of the onboarding process, you will be provided with a Client ID and Secret Key.

- **Client ID** is equivalent to your **Merchant ID**
- **Secret Key** is equivalent to your **API Key**

### API Reference

For a full reference to the API, please visit: [MobyPay API Reference](https://pay.mobycheckout.com/api-docs)

---

## Verifying the Signature of Calls

Security is paramount in payment processing. Verifying the signature of callbacks from Moby Payments ensures that the information received is genuinely from Moby Payments and has not been tampered with.

### How to Verify Signatures

1. **Receive the Callback:** When Moby Payments sends a callback, it includes a `signature` field in the request body.
2. **Extract the Signature:** Extract the `signature` value from the incoming request.
3. **Generate Your Signature:** Using the same payload fields (excluding `signature`) and your `secretKey`, generate an HMAC-SHA256 hash. Sort the remaining fields alphabetically by key, concatenate their string values in that order, then hash the result.
4. **Compare Signatures:** If your generated signature matches the one received, the request is authentic. Reject any request where they do not match.

> **Important:** Always verify the signature **before** acting on any callback or redirect.

### Signature Fields

The following response fields are used when generating the signature (sorted alphabetically by key, `signature` field excluded):

`amount`, `description`, `merchantOrderRef`, `payMethod`, `referenceNo`, `status`, `time`, `transactionId`

### Sample Code

```javascript
const crypto = require('crypto');

/**
 * Generates an HMAC SHA256 signature from given parameters and a secret key.
 * @param {Object} params - The response payload fields (excluding 'signature').
 * @param {string} secretKey - The secret key used for signing.
 * @return {string} The generated signature.
 */
function generateSignature(params, secretKey) {
  // Sort the parameters alphabetically by key
  const sortedKeys = Object.keys(params).sort();
  let sortedString = '';

  // Concatenate the sorted parameter values into a single string
  sortedKeys.forEach(key => {
    sortedString += params[key];
  });

  // Generate the HMAC SHA256 hash using the secret key
  const signature = crypto.createHmac('sha256', secretKey)
    .update(sortedString)
    .digest('hex');

  return signature;
}

// Example usage - exclude the 'signature' field from params
const params = {
  referenceNo: '234test1232111111qw343',
  transactionId: '******11196916084427898',
  amount: '60.00',
  payMethod: 'TEST',
  status: 'success',
  time: '2025-11-19 14:52:52',
  merchantOrderRef: '',
  description: 'Approved',
};
const secretKey = 'your_secret_key';
const signature = generateSignature(params, secretKey);
console.log('Generated Signature:', signature);
```

---

## Handling Notifications

When integrating with Moby Payments, you provide a `callbackUrl`. Moby Payments will send an HTTP POST request to this URL whenever a transaction occurs, delivering a JSON payload with the transaction details. This acts as a webhook for real-time updates.

### Steps to Handle Notifications

1. **Verify the Signature:** Before taking any action, verify the `signature` field. See [Verifying the Signature of Calls](#verifying-the-signature-of-calls).
2. **Process the Payload:** Update your system based on the `status` and other details.
3. **Respond with HTTP 200:** Return HTTP `200 OK` with the body below to acknowledge receipt. If Moby Payments does not receive a 200 response, it may retry the callback.

```json
{
  "status": "success"
}
```

### Example Callback Payload

```json
{
  "referenceNo": "234test1232111111qw343",
  "transactionId": "******11196916084427898",
  "amount": "60.00",
  "payMethod": "TEST",
  "status": "success",
  "time": "2025-11-19 14:52:52",
  "merchantOrderRef": null,
  "description": "Approved",
  "signature": "ac5e3e158839b691f69a7a933035f75b443ef3c4e40f7e8bf82ae1af68fa3ebb"
}
```

### Payment Status Values

| Status | Description |
|--------|-------------|
| `success` | Payment was approved and completed |
| `failed` | Payment was declined or failed |
| `pending` | Payment is pending processing |

---

## Additional Support

For further assistance, you can reach our support teams:

**Customer Care:**
- Email: customercare@moby.my
- Phone: 011 1111 5155

**Merchant Support:**
- Email: merchantsupport@moby.my
- Phone: 011 1111 7177

[Return to Home](../../README.md)
### How to Create a Payment Session:

1. **Initiate Payment Session**: Call the payment initiation endpoint with the necessary payment details and your authorization token.
   **POST /api/merchant/payment/checkout/hosted**
2. **Include Payment Details**: Provide the amount, customer information, and any additional details required for the transaction.
3. **Receive Payment Link**: The API response will include a URL to the Moby Payments page where your customer can complete the payment.

Example Request:

```bash
curl -X POST "[PAYMENT_URL]/api/merchant/payment/checkout/hosted" \
     -H "Authorization: Bearer your_access_token" \
     -H "Content-Type: application/json" \
     -d '{
         "clientId": "YOUR_CLIENT_ID"
         "customerName": "customer name",
         "customerEmail": "customer@example.com",
         "customerMobile": "0111222333",
         "referenceNo": 100,
         "details": "additional information"
         "amount": 100,
         "returnUrl": "https://yourapp.com/payment/complete",
         "callbackUrl": "https://yourapp.com/payment/moby/status",
         "cart": "Purchased items details" (Array - Optional),
        }'
```

### **Step 3: Complete the Payment**

After the customer completes the payment process on the Moby Payments page, they will be automatically redirected back to your application via the **return_url** you provided. This URL can handle any post-payment processing or status updates necessary for your application.

### **Payment Completion Flow:**

1.  **Customer Redirect**: Following a successful payment, the customer is redirected to your specified return URL.
2.  **Verify Payment**: Optionally, you can verify the payment status by calling the payment verification endpoint with the transaction ID received upon redirection.
3.  **Confirm Payment**: Update your system with the payment status, completing the integration process.

Example Response:

```bash
{
  "referenceNo": "Payment Reference",
  "transactionId": "Your Payment ID",
  "amount": "Payment Amount",
  "payMethod": "Payment Method Used By The User",
  "status": "Payment Status",
  "time": "Payment Time (YYYY-MM-DD HH:mm:ss)",
  "merchantOrderRef": "Merchant Order Reference",
  "description": "Payment Description or Status Description",
  "signature": "Request Signature"
}
```

Congratulations! You have now integrated Moby Payments into your application. With these three simple steps, you're ready to offer a seamless and secure payment experience to your customers. But there's more to robust integration than just getting started. To ensure your application is secure and resilient, it's essential to delve into two additional aspects:

[Verifying the Signature of Calls](#verifying-the-signature-of-calls)

[Handling Notifications](#handling-notifications)

## Getting Your Credentials

### Payment URL

Base on the environment that you are working on, you can use one of the following urls:

```bash
Sandbox Environment:
dev.pay.mobycheckout.com

Production Environment
pay.mobycheckout.com
```

### Client ID & Secret Key

Upon completion of the onboarding process, you will be provided with a Client ID and Secret Key. Please note that the Client ID is equivalent to your Merchant ID and the Secret Key is equivalent to your API Key.

## API Reference

For a more detailed understanding and complete reference to our API, please visit the link below.

[MobyPay API Reference](https://documenter.getpostman.com/view/32981011/2sA2xnzAvK)

# Verifying the Signature of Calls

Security is paramount in payment processing. Verifying the signature of callbacks from Moby Payments ensures that the information received is indeed from Moby Payments and has not been tampered with.

### How to Verify Signatures:

1.  **Receive the Callback**: When Moby Payments sends a callback to your server (e.g., payment status updates), it includes a signature header. This signature allows you to verify the authenticity of the request.
2.  **Extract the Signature**: The signature is sent in a body of the response named signature. Extract this from the incoming request.
3.  **Generate Your Signature**: Using the payload of the callback and your secretKet, generate a hash using the same algorithm that Moby Payments uses (e.g., HMAC-SHA256).
4.  **Compare Signatures**: Compare the signature you generated with the one sent by Moby Payments. If they match, the request is authentic.

Sample Code

```bash
const crypto = require('crypto');

/**
 * Generates an HMAC SHA256 signature from given parameters and a secret key.
 * @param {Object} params - The parameters to be signed, as key-value pairs.
 * @param {string} secretKey - The secret key used for signing.
 * @return {string} The generated signature.
 */
function generateSignature(params, secretKey) {
    // Sort the parameters by key
    const sortedKeys = Object.keys(params).sort();
    let sortedString = '';

    // Concatenate the sorted parameters into a single string
    sortedKeys.forEach(key => {
        sortedString += params[key];
    });

    // Generate the HMAC SHA256 hash of the concatenated string using the secret key
    const signature = crypto.createHmac('sha256', secretKey)
                            .update(sortedString)
                            .digest('hex');

    return signature;
}

// Example usage
const params = {
    order_id: '12345',
    amount: '100',
    currency: 'USD',
};
const secretKey = 'your_secret_key';

const signature = generateSignature(params, secretKey);
console.log('Generated Signature:', signature);

```

# Handling Notifications

Efficiently manage notifications from Moby Payments to handle transactions, especially unsuccessful ones. When integrating with Moby Payments, you have the option to provide a **callback_url**. This URL is used by Moby Payments to send direct callbacks to your system, acting similarly to a webhook. Whenever a transaction occurs, Moby Payments will make a request to this **callback_url** with a payload containing the transaction details. This enables your system to receive real-time notifications about transactions, allowing you to process and respond to each event accordingly.

Here’s what you need to do to handle those calls:

1.  Verify: before action on any calls to this endpoint, you first need to verify the signature, [see here](#verifying-the-signature-of-calls)
    ).
2.  Process & Response: Update your system based on the details given and respond to the call with the following message:

Status to be returned by your end.

```bash
{
  "status": 'success',
}
```

Example Request Body

```bash
{
  "referenceNo":"234test1232111111qw343",
  "transactionId":"******11196916084427898",
  "amount":"60.00",
  "payMethod":"TEST",
  "status":"success",
  "time":"2025-11-19 14:52:52",
  "merchantOrderRef":null,
  "description":"Approved",
  "signature":"ac5e3e158839b691f69a7a933035f75b443ef3c4e40f7e8bf82ae1af68fa3ebb"
}
```

## Additional Support

For further assistance, you can reach our support teams:

- **Customer Care**:

  - Email: [customercare@moby.my](mailto:customercare@moby.my)
  - Phone: 011 1111 5155

- **Merchant Support**:
  - Email: [merchantsupport@moby.my](mailto:merchantsupport@moby.my)
  - Phone: 011 1111 7177

[Return to Home](../README.md)
