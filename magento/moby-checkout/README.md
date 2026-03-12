# Moby Checkout Plugin for Magento 2

[**Download the Latest Magento Plugin - Moby Checkout**](https://raw.githubusercontent.com/MobyPayTech/moby-plugins/main/magento/moby-checkout/Moby_Checkout.zip)

Magento 2 payment extension for **Moby Checkout** hosted payment flow.

This guide is written for merchants/clients who receive this extension as a ZIP package.

---

## 1. Overview

The Moby Checkout module adds a payment method in Magento checkout and redirects customers to Moby hosted payment page.

### Key capabilities
- Hosted checkout redirect flow
- Sandbox (`test`) and Production (`live`) modes
- Configurable checkout logos (Visa, Mastercard, Maybank, FPX)
- Dedicated module log: `var/log/moby_checkout.log`

---

## 2. Package Structure

Download the plugin from the link above, then ensure this module path exists:

`app/code/Moby/Checkout`

Required core module files:
- `app/code/Moby/Checkout/registration.php`
- `app/code/Moby/Checkout/etc/module.xml`
- `app/code/Moby/Checkout/composer.json`

---

## 3. System Requirements

- Magento Open Source / Adobe Commerce
- PHP version compatible with your Magento version
- CLI access to run `bin/magento` commands
- Store currency for checkout/order must be **MYR**

---

## 4. Installation (From ZIP)

1. Copy/unzip module into Magento root:

```bash
unzip Moby_Checkout.zip -d <magento_root>/app/code
```

After extraction, this folder must exist:

`<magento_root>/app/code/Moby/Checkout`

2. Run Magento setup commands:

```bash
cd <magento_root>
bin/magento module:enable Moby_Checkout
bin/magento setup:upgrade
bin/magento setup:di:compile
bin/magento setup:static-content:deploy -f en_US
bin/magento cache:flush
```

3. (Recommended) Reindex:

```bash
bin/magento indexer:reindex
```

---

## 5. Admin Configuration

Go to:

`Admin > Stores > Configuration > Sales > Payment Methods > Moby Checkout`

### Screenshot placeholders
Add your screenshots in your final client version:

- `![Moby Checkout Admin Section](docs/images/admin-payment-method.png)`
- `![Checkout Payment Method UI](docs/images/checkout-payment-ui.png)`

### Field reference

- **Enabled**: Turns payment method on/off.
- **Title**: Payment method name shown at checkout.
- **Description**: Text shown below method title.
- **Mode**: `test` for sandbox, `live` for production.
- **Merchant ID**: Provided by Moby.
- **API Key**: Provided by Moby.
- **Company Name**: Sent with payment request (optional but recommended).
- **Show Visa Label**: Show/hide Visa logo at checkout.
- **Show Mastercard Label**: Show/hide Mastercard logo.
- **Show Maybank Label**: Show/hide Maybank logo.
- **Show FPX Label**: Show/hide FPX logo.
- **Sort Order**: Position among payment methods.

### Logo setting behavior
- Logo options control only checkout display, not transaction routing.
- If a logo is disabled in admin, that icon is hidden from checkout UI.
- Default module configuration enables all 4 logos.

---

## 6. Gateway Endpoints and Modes

### Base URLs
- **Sandbox/Test**: `https://dev.pay.mobycheckout.com`
- **Production/Live**: `https://pay.mobycheckout.com`

### Magento endpoints used by module
- Redirect action: `/moby/checkout_redirect/index`
- Return URL: `/moby/checkout_return/index`
- Callback URL: `/moby/checkout_callback/index`

Ensure your production domain is HTTPS and publicly reachable for callbacks.

---

## 7. Currency Rule (Important Edge Case)

This integration is intended for **MYR** transactions.

### Expected behavior
- If cart/order currency is MYR: Moby Checkout is available.
- If currency is not MYR: payment method may be unavailable or transaction should not proceed.

### Client recommendation
- Keep checkout/order currency in MYR for stores using this gateway.
- If multi-currency store is used, validate that Moby method appears only for MYR checkout.

---

## 8. Payment Flow

1. Customer selects **Moby Checkout** in Magento checkout.
2. Customer clicks **Place Order**.
3. Magento creates order (pending payment) and requests hosted pay link from Moby.
4. Customer is redirected to Moby hosted checkout page.
5. Moby sends server callback to Magento callback URL.
6. Customer is redirected back to Magento return URL.
7. Magento updates order status based on verified callback/return data.

---

## 9. Callback and Security Notes

- Signature validation is applied to protect callback integrity.
- Invalid signatures are rejected and logged.
- Duplicate callback handling is idempotent (safe against repeated notifications).

Log file:

`var/log/moby_checkout.log`

---

## 10. Testing Checklist (Client UAT)

1. **Method visibility**: Moby Checkout appears in checkout.
2. **MYR validation**: Verify behavior for MYR vs non-MYR carts.
3. **Sandbox success order**: Successful payment updates order correctly.
4. **Failed/cancelled order**: Order status/comments update correctly.
5. **Logo toggles**: Enable/disable each logo from admin and confirm UI change.
6. **Return/callback reachability**: No callback errors in logs.

---

## 11. Troubleshooting

### Payment method not visible
- Confirm module enabled:
  - `bin/magento module:status Moby_Checkout`
- Confirm **Enabled = Yes** in payment configuration.
- Confirm currency is MYR.
- Flush cache:
  - `bin/magento cache:flush`

### UI/CSS changes not visible
Run:

```bash
bin/magento cache:flush
bin/magento setup:static-content:deploy -f en_US
```

Then hard refresh browser (`Ctrl/Cmd + Shift + R`).

### Callback not updating order
- Check callback URL is publicly reachable.
- Verify Merchant ID/API Key/Mode values.
- Inspect logs in `var/log/moby_checkout.log`.

---

## 12. Uninstall (Optional)

```bash
bin/magento module:disable Moby_Checkout
bin/magento setup:upgrade
bin/magento cache:flush
```

Then remove folder:

`app/code/Moby/Checkout`

---

## 13. Support

For support, contact Moby teams:

- **Customer Care**
  - Email: `customercare@moby.my`
  - Phone: `011 1111 5155`

- **Merchant Support**
  - Email: `merchantsupport@moby.my`
  - Phone: `011 1111 7177`
