# SimplySteno — PayPal Buy Now repair

Fixes the broken payment buttons on https://simplystenovoice.com/payments/ and makes the three
"I agree" checkboxes actually enforce themselves.

## What was wrong

**1. Every Buy Now button was a dead, one-time link.**
All 9 buttons pointed at a PayPal *checkout-session* URL:

```
https://www.paypal.com/webapps/hermes?token=9FN00626JK6063306&useraction=commit&flowType=WPS...
```

That `token=...` identifies **one single checkout, for one single shopper**. It is single-use and
expires within hours — it is not a reusable button link. The timestamps embedded in those URLs
decode to **29 Aug 2025**, the day of the rebuild: whoever rebuilt the page clicked each of the old
buttons, copied the PayPal URL out of the browser address bar, and pasted it back in as the link.

So every customer was being dropped into a stranger's long-dead checkout session. Hence the errors.

**2. The three checkboxes enforced nothing.** They were raw HTML with **zero JavaScript** attached —
the only thing referencing them anywhere on the page was two CSS rules. Customers could pay without
ticking a single box.

**3. There was no PayPal SDK on the page at all.**

## The fix

`simplysteno-paypal-widget.html` — one self-contained block. It:

- loads the PayPal JS SDK,
- finds each `.price_box` card, **reads the price out of the card's own heading**
  (`$1,590 (12 months)` → `1590.00`), so if you edit a price in Elementor the button follows
  automatically — no amounts hardcoded anywhere to drift out of sync,
- strips the dead link and renders a real PayPal Smart Button in its place,
- **gates every button on all three checkboxes**, using PayPal's documented `onInit` /
  `actions.disable()` + `onClick` / `actions.reject()` terms-acceptance pattern.

Nothing else on the page is touched. The cards, layout, copy and checkbox wording stay exactly as
they are.

## Install

1. WordPress → Pages → **Payments** → Edit with Elementor.
2. Drag an **HTML** widget to the very bottom of the page (below the last price card).
3. Paste in the entire contents of `simplysteno-paypal-widget.html`.
4. Set `PAYPAL_CLIENT_ID` (line ~25) — see below.
5. Update.

### Client ID

Get these from https://developer.paypal.com → Apps & Credentials, using the Business account:

- **Sandbox** tab → Client ID → test the whole flow with fake money.
- **Live** tab → Client ID → real payments.

The file ships with `PAYPAL_CLIENT_ID = "test"`, PayPal's public demo ID. Buttons render and the
checkout window opens, but **no money moves** — safe for previewing, useless for real payments.
Swap it for the Live ID when you're happy.

## Verified

Driven in a real browser (Playwright, Chromium):

| Test | Result |
|---|---|
| 0 boxes ticked → click Buy Now | **blocked**, no PayPal window, warning shown |
| 2 of 3 ticked → click Buy Now | **blocked**, no PayPal window |
| 3 of 3 ticked → click Buy Now | **PayPal checkout opens** (`sandbox.paypal.com/checkoutnow`) |
| untick a box afterwards | button **re-locks** immediately |
| dead `hermes` links remaining on page | **0** |
| JS errors | none |

Screenshots: `shot_1_blocked.png`, `shot_2_unlocked.png`, `shot_3_us_locale.png`.

## Notes

- `LOCALE` is pinned to `en_US`. Without it PayPal guesses from the shopper's IP — while testing
  from a European server the buttons came up in German ("Später Bezahlen") with SEPA Direct Debit
  offered. Pinning the locale prevents that.
- Funding is trimmed to the gold **Buy Now** button plus **Pay Later** (PayPal Credit), which the
  page already advertises. Shoppers without a PayPal account can still pay by card as a guest
  *inside* the PayPal window. If you'd rather show a separate "Debit or Credit Card" button on each
  card, remove `card` from `DISABLE_FUNDING`.
- The `$20 Late Payment Fee` card gets a button too, same as the rest.

## Files

| File | Purpose |
|---|---|
| `simplysteno-paypal-widget.html` | **The deliverable.** Paste into an Elementor HTML widget. |
| `DIAGNOSIS.md` | Full breakdown of the fault, incl. the 9 dead tokens. |
| `demo/index.html` | Local replica of the payments page running the widget. |
| `test_behaviour.py` | The browser test that proves the checkbox gate holds. |
