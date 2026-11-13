// Screenshots the card HTML files listed in a jobs JSON file, using the Edge/Chrome already on the machine.
// Usage: node render.js <jobs.json>
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
const puppeteer = require("puppeteer-core");

const CANDIDATES = [
  process.env.BROWSER_PATH,
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
].filter(Boolean);

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  const exe = CANDIDATES.find((p) => fs.existsSync(p));
  if (!exe) { console.error("No Edge/Chrome found. Set BROWSER_PATH to its executable."); process.exit(1); }
  const browser = await puppeteer.launch({ executablePath: exe, headless: true });
  const page = await browser.newPage();
  let done = 0, failed = 0;
  for (const j of jobs) {
    try {
      await page.setViewport({ width: j.w, height: j.h, deviceScaleFactor: 1 });
      await page.goto(pathToFileURL(j.html).href, { waitUntil: "networkidle0", timeout: 30000 });
      await page.evaluate(() => document.fonts.ready);
      fs.mkdirSync(path.dirname(j.out), { recursive: true });
      await page.screenshot({ path: j.out, type: "jpeg", quality: 86 });
      done++;
      if (done % 25 === 0) console.log("  rendered " + done + "/" + jobs.length);
    } catch (e) {
      failed++;
      console.error("  failed: " + j.html + " — " + e.message);
    }
  }
  await browser.close();
  console.log("render: " + done + " images written" + (failed ? ", " + failed + " failed" : ""));
  if (failed) process.exit(1);
})();
