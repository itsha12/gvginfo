import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1400, "height": 1000})
        await pg.route("https://api.github.com/**", lambda r: r.fulfill(status=404, body="{}"))
        await pg.route("https://wiki.guildwars.com/**", lambda r: r.abort())
        msgs=[]; pg.on("console", lambda m: msgs.append(m.text)); pg.on("pageerror", lambda e: msgs.append(str(e)))
        await pg.goto("http://localhost:8765/#/report/51683de9-4096-5833-ad4a-56a69c4759e4")
        await pg.wait_for_timeout(2500)
        await pg.evaluate("document.querySelector(\"#rp-key details\")?.setAttribute(\"open\",\"\")")
        await pg.wait_for_timeout(300)
        await pg.screenshot(path=sys.argv[1], full_page=True)
        print("\n".join(msgs[:10]))
        await b.close()
asyncio.run(main())
