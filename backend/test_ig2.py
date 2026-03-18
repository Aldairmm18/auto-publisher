from playwright.sync_api import sync_playwright
import os

PROFILE_DIR = os.path.abspath('cookies/chrome_profile_instagram')

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False,
        args=['--disable-blink-features=AutomationControlled'],
        ignore_default_args=['--enable-automation'],
        viewport={'width': 414, 'height': 896},
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'
    )
    page = context.new_page()
    page.goto('https://www.instagram.com', wait_until='domcontentloaded')
    page.wait_for_timeout(5000)

    svg = page.locator('svg[aria-label="Nueva publicación"]').first
    parent = svg.locator('xpath=..').first
    parent.click()
    print('1. Click en Nueva publicacion OK')
    page.wait_for_timeout(2000)

    pub_btn = page.get_by_text('Publicación', exact=True).first
    pub_btn.click()
    print('2. Click en Publicacion OK')
    page.wait_for_timeout(3000)

    page.screenshot(path='cookies/debug_ig_step2.png')
    print('Screenshot guardado')

    context.close()
