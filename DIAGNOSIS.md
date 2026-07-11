# simplystenovoice.com/payments/ — PayPal diagnosis (2026-07-11)

## Fault 1 — every "Buy Now" button is a dead, one-time checkout link

All 9 payment buttons are plain `<a href>` tags pointing at a **PayPal Hermes checkout-session URL**:

```
https://www.paypal.com/webapps/hermes?token=9FN00626JK6063306&useraction=commit&flowType=WPS...
```

A `token=...` (EC token) identifies **one single checkout session for one single shopper**.
It is single-use and expires in a few hours. It is NOT a reusable button link.

The embedded timestamps (`...StartTime=1756455511484`) decode to **29 Aug 2025** — the day of the
rebuild. Whoever rebuilt the page clicked each old Buy Now button, copied the resulting PayPal
URL out of the browser address bar, and pasted it in as the link.

So every visitor is being sent into a stranger's expired, already-consumed checkout session →
PayPal errors out. This is the reported bug.

| Elementor id | Card | Dead token |
|---|---|---|
| 4edad2a | $710 (3 months)      | 9FN00626JK6063306 |
| 43a5788 | $970 (6 months)      | 7WP86457VG897960N |
| 000b8f8 | $1,590 (12 months)   | 48093082B7284190N |
| cd7cd34 | $3,790 (1-Time Fee)  | 3VR8856896274820V |
| 6117f35 | 1 Month — $180       | 1JV0309592105413P |
| c8d70bd | 3 Month — $360       | 2NK0162888587830J |
| 9e81f06 | 6 Month — $650       | 1PP18546TJ878842X |
| 3375a4c | 1 Year — $1,240      | 3AB50699BK847144H |
| 71ca270 | Late Fee — $20       | 84953046RF003382P |

Note: the $20 late-fee link is also plain **http://** (not https).

## Fault 2 — the three checkboxes enforce nothing

The checkbox block (`.checkbox_wrapper`, inputs `agree1/agree2/agree3`) is raw HTML in an
Elementor HTML widget. Grepping the rendered page: the only references to it anywhere are
**two CSS rules** (lines 429/433). There is **zero JavaScript** bound to them.

They are decorative. A customer can pay right now without ticking any box — the "validation"
the client believes exists does not exist on the rebuilt page.

## Fault 3 — no PayPal SDK on the page at all

No `paypal.com/sdk/js`, no `checkout.js`. Nothing to integrate against.

## Fix

One Elementor HTML widget at the bottom of the page. It:
1. loads the PayPal JS SDK,
2. finds each `.price_box` card, reads the price from its own `<h3>` (so if Marc edits a price,
   the button follows automatically — no hardcoded amounts to drift),
3. replaces the dead link with a real PayPal Smart Button in the same spot,
4. gates every button on all three checkboxes using PayPal's documented
   `onInit`/`actions.disable()` + `onClick`/`actions.reject()` terms-acceptance pattern.

Nothing else on the page is touched.

## Could not reproduce from this server
PayPal blocks datacenter/headless traffic ("You have been blocked — we couldn't load the security
challenge"), so I could not capture the shopper-facing error message myself. The cause is
unambiguous from the markup regardless.
