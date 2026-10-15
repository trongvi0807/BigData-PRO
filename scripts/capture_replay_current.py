"""Capture current real replay and live charts without changing any dataset."""
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT=Path('/workspace/outputs/screenshots')
with sync_playwright() as p:
    browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1050})
    page.goto('http://127.0.0.1:8090/?source=all#replay',wait_until='networkidle')
    page.wait_for_function('ReplayView.view.history?.frames.length>0');page.wait_for_timeout(900)
    page.screenshot(path=str(OUT/'14-four-platform-replay-20261015.png'),full_page=True)
    page.locator('#replay-switch').click()
    page.wait_for_function('ReplayView.view.mode==="live" && ReplayView.view.live.length>0');page.wait_for_timeout(900)
    page.screenshot(path=str(OUT/'15-live-source-growth-20261015.png'),full_page=True)
    browser.close()
print('Current HDFS replay and real-source observation chart screenshots captured')
