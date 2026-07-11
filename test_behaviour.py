from playwright.sync_api import sync_playwright

def warning_visible(pg):
    return pg.evaluate("""() => {
        const w = document.querySelector('.ss-paypal-warning');
        return !!w && getComputedStyle(w).display !== 'none';
    }""")

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width":1280,"height":720})
    pg = ctx.new_page()
    popups = []
    ctx.on("page", lambda pop: popups.append(pop))

    pg.goto("http://127.0.0.1:8912/", wait_until="networkidle", timeout=60000)
    pg.wait_for_selector(".ss-paypal-button iframe", timeout=30000)
    pg.wait_for_timeout(3000)

    btn = pg.frame_locator(".ss-paypal-button iframe").first.locator(
        "[data-funding-source='paypal']").first

    # --- TEST 1: boxes unticked -> click must NOT open PayPal ---
    btn.click(force=True)
    pg.wait_for_timeout(4000)
    print("TEST 1  boxes UNTICKED, clicked Pay")
    print("        PayPal windows opened :", len(popups), "(want 0)")
    print("        warning shown to user :", warning_visible(pg), "(want True)")
    pg.screenshot(path="shot_1_blocked.png")

    # --- TEST 2: only 2 of 3 -> still blocked ---
    pg.check('input[name="agree1"]'); pg.check('input[name="agree2"]')
    pg.wait_for_timeout(1500)
    btn.click(force=True); pg.wait_for_timeout(4000)
    print("TEST 2  only 2 of 3 ticked, clicked Pay")
    print("        PayPal windows opened :", len(popups), "(want 0)")

    # --- TEST 3: all 3 -> PayPal must open ---
    pg.check('input[name="agree3"]')
    pg.wait_for_timeout(1500)
    print("TEST 3  all 3 ticked")
    print("        warning auto-cleared  :", not warning_visible(pg), "(want True)")
    pg.screenshot(path="shot_2_unlocked.png")
    btn.click(force=True); pg.wait_for_timeout(7000)
    print("        PayPal windows opened :", len(popups), "(want >=1)")
    if popups:
        print("        popup URL            :", popups[0].url[:95])
    ctx.close(); b.close()
