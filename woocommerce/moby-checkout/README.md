# MobypayCheckoutGateway WordPress Plugin

[**Download the Latest WooCommerce Plugin - v1.5**](https://raw.githubusercontent.com/MobyPayTech/moby-plugins/main/woocommerce/moby-checkout/v1.5/moby-checkout.zip)

## Overview

The MobypayCheckoutGateway plugin integrates Moby Checkout as a payment gateway for WooCommerce. It provides a seamless payment experience for both merchants and customers.

## Features

- Supports product payments
- Configurable test and production modes
- Secure payment processing
- Callback and redirect handling for payment status updates

## Installation

1. Upload the plugin files to the `/wp-content/plugins/mobypay-checkout` directory.
2. Activate the plugin through the 'Plugins' menu in WordPress.
3. Configure the plugin settings in WooCommerce > Settings > Payments > Moby Checkout.

## Configuration

1. Enable the payment gateway.
2. Choose the environment (Sandbox or Production).
3. Enter your Merchant ID and API Key.
4. Set your Company Name.

## Key Components

### Payment Initialization

The `process_payment` method in `includes/mobypay-checkout-gateway.php` is responsible for initializing the payment process. It prepares the order data and sends it to Moby Checkout to create a payment link.

### Callback Handling

The `mobypay_callback` method in `includes/mobypay-checkout-gateway.php` handles the server-to-server callbacks from Moby Checkout. It updates the order status based on the payment result.

### Redirect Handling

The `mobypay_response` method in `includes/mobypay-checkout-gateway.php` manages the customer redirect after payment. It updates the order status and displays appropriate messages to the customer.

## Security

- The plugin validates the HMAC signature for both callbacks and redirects to ensure the integrity of the payment data.
- API credentials are securely stored and used for communication with Moby Checkout.

## ⚠️ Troubleshooting

- ❗ **Ensure WooCommerce plugin is installed.**
- ❗ **Ensure currency is set to MYR.**
- ✅ Ensure your Merchant ID and API Key are correct.
- ✅ Check the WooCommerce log for any error messages.
- ✅ Verify that your server can receive callbacks from Moby Checkout.

## Additional Support

For further assistance, you can reach our support teams:

- **Customer Care**:

  - Email: [customercare@moby.my](mailto:customercare@moby.my)
  - Phone: 011 1111 5155

- **Merchant Support**:

  - Email: [merchantsupport@moby.my](mailto:merchantsupport@moby.my)
  - Phone: 011 1111 7177

  [Return to Home](../README.md)
