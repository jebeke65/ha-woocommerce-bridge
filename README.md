# HA WooCommerce Bridge (Home Assistant)

Custom integration that polls a secure WordPress/WooCommerce endpoint (provided by the companion WP plugin) and exposes:
- `sensor.woocommerce_open_orders` (count)
- `sensor.woocommerce_latest_open_order` (order number, with attributes)

## Install via HACS
1. In HACS → Integrations → ⋮ → Custom repositories
2. Add this repo URL, category **Integration**
3. Install **HA WooCommerce Bridge**
4. Restart Home Assistant
5. Settings → Devices & Services → Add Integration → **HA WooCommerce Bridge**
6. Provide:
   - Endpoint: `https://<site>/wp-json/ha-wc/v1/open-orders`
   - Token: the value from the WordPress plugin settings (sent as header `X-HA-Token`)

## Companion WordPress plugin
Install **HA WooCommerce Bridge** plugin in WordPress and copy token + endpoint.

## Troubleshooting
- If you get `Forbidden`, token is missing/incorrect.
- If you get connection errors, verify the endpoint is reachable from your HA instance.
