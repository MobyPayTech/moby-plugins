# Changelog

All notable changes to Moby Plugins documentation and releases will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- CHANGELOG.md to track release history and documentation changes
- Rate limiting documentation to Recurring Payments API guide
- API versioning policy section to Recurring Payments guide
- Parameter tables to Direct Integration hosted payment endpoint
- Payment status values table to Direct Integration guide
- Signature fields specification to Direct Integration guide
- Callback HTTP 200 response requirement documented in Direct Integration guide
- WooCommerce version compatibility requirements table (WordPress 5.0+, WooCommerce 5.0+, PHP 7.4+)
- WooCommerce plugin upgrade and uninstallation instructions
- WooCommerce troubleshooting table with common issues and resolutions
- Shopify plugin upgrade instructions
- Prominent E-Wallet live transaction warning in Sandbox Testing guide
- Online Banking sandbox note clarifying only ACF Bank B2B is available
- Getting Your Credentials section with environment URL table in Direct Integration guide
- Table of Contents entry for Getting Your Credentials in Direct Integration guide

### Fixed
- Invalid JSON in Direct Integration hosted payment curl example (missing commas)
- Typo `secretKet` corrected to `secretKey` in signature generation code comment
- Shopify `READEME.md` renamed to `README.md`
- OpenCart version links in root README now point to versioned sub-directories
- Unified sandbox URL documentation (was inconsistent between Direct Integration and Recurring Payments guides)
- Token expiry clarified: Direct Integration tokens expire after 60 minutes; Recurring Payments API tokens expire after 30 minutes
- Shopify configuration credential naming aligned with onboarding terminology (API Key + Secret Key)

### Changed
- All README files updated to use consistent Additional Support section formatting
- Main README table of contents now uses relative links for all sub-guides
- Recurring Payments README restructured with improved section navigation

---

## Plugin Versions

### WooCommerce - Moby Checkout

| Version | Release Date | Notes |
|---------|-------------|-------|
| v1.5 | 2026-02-24 | Latest release |

### WooCommerce - Price Divider

| Version | Release Date | Notes |
|---------|-------------|-------|
| v1.3 | 2026-02-24 | Latest release |

### Magento - Moby Checkout

| Version | Release Date | Notes |
|---------|-------------|-------|
| Latest | 2026-03-12 | See magento/moby-checkout directory |

### OpenCart

| Version | Release Date | Notes |
|---------|-------------|-------|
| v4.0 | 2025-04-04 | Latest release |
| v3.0 | - | |
| v2.0 | - | |
| v1.0 | - | |

---

*For support, see [Additional Support](README.md#additional-support).*
