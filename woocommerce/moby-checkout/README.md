# MobypayCheckoutGateway WordPress Plugin

[Download the Latest WooCommerce Plugin - v1.5](https://github.com/MobyPayTech/moby-plugins/tree/main/woocommerce/moby-checkout)

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Upgrading](#upgrading)
- [Key Components](#key-components)
- [Troubleshooting](#troubleshooting)

---

## Overview

The MobypayCheckoutGateway plugin integrates Moby Checkout as a payment gateway for WooCommerce. It provides a seamless payment experience for both merchants and customers.

### Features

- Supports product payments
- Configurable sandbox and production modes
- Secure payment processing with HMAC signature validation
- Callback and redirect handling for payment status updates

---

## Requirements

| Requirement | Minimum Version |
|-------------|----------------|
| WordPress | 5.0 or higher |
| WooCommerce | 5.0 or higher |
| PHP | 7.4 or higher |
| Currency | MYR (Malaysian Ringgit) only |

> **Note:** This plugin currently only supports **MYR (Malaysian Ringgit)** as the transaction currency. Ensure your WooCommerce store currency is set to MYR before activating the plugin.

---

## Installation

1. Download the latest plugin zip file from the link above.
2. In your WordPress admin panel, go to **Plugins > Add New > Upload Plugin**.
3. Upload the downloaded zip file and click **Install Now**.
4. Click **Activate Plugin** after installation completes.
5. Configure the plugin settings in **WooCommerce > Settings > Payments > Moby Checkout**.

---

## Configuration

1. **Enable** the payment gateway by toggling it on.
2. **Choose the environment:** Select **Sandbox** for testing or **Production** for live payments.
3. **Enter your Merchant ID** and **API Key** (provided during onboarding).
4. **Set your Company Name** as it should appear to customers.
5. Click **Save changes**.

> ⚠️ Always test your integration thoroughly in **Sandbox** mode before switching to **Production**.

---

## Upgrading

When a new version of the plugin is released:

1. **Back up your current settings** — note down your Merchant ID, API Key, and environment setting before upgrading.
2. Deactivate and delete the current version of the plugin from **Plugins > Installed Plugins**.
3. Download and install the new version following the [Installation](#installation) steps above.
4. Re-enter your credentials in **WooCommerce > Settings > Payments > Moby Checkout**.

> **Note:** Upgrading the plugin does not automatically preserve your settings. Always re-enter your credentials after upgrading.

---

## Key Components

### Payment Initialization

The `process_payment` method in `includes/mobypay-checkout-gateway.php` is responsible for initializing the payment process. It prepares the order data and sends it to Moby Checkout to create a payment link.

### Callback Handling

The `mobypay_callback` method in `includes/mobypay-checkout-gateway.php` handles server-to-server callbacks from Moby Checkout. It validates the HMAC signature and updates the order status based on the payment result.

### Redirect Handling

The `mobypay_response` method in `includes/mobypay-checkout-gateway.php` manages the customer redirect after payment. It updates the order status and displays appropriate messages to the customer.

### Security

- The plugin validates the HMAC signature for both callbacks and redirects to ensure the integrity of payment data.
- API credentials are securely stored in the WordPress options table and used for communication with Moby Checkout.

---

## Troubleshooting

| Issue | Action |
|-------|--------|
| Payment gateway not visible at checkout | Ensure WooCommerce is installed and the plugin is activated |
| Payments failing immediately | Verify your Merchant ID and API Key are correct |
| Currency error | Ensure WooCommerce currency is set to **MYR** |
| Callbacks not being received | Verify your server is publicly accessible and can receive POST requests from Moby Checkout |
| Order status not updating | Check the WooCommerce logs at **WooCommerce > Status > Logs** for error messages |

> ✅ Check the WooCommerce log for detailed error messages: **WooCommerce > Status > Logs**

---

## Additional Support

For further assistance, you can reach our support teams:

**Customer Care:**
- Email: customercare@moby.my
- Phone: 011 1111 5155

**Merchant Support:**
- Email: merchantsupport@moby.my
- Phone: 011 1111 7177

[Return to Home](../../../README.md)
