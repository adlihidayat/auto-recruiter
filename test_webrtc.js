const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: "new",
    args: [
      '--use-fake-ui-for-media-stream',
      '--use-fake-device-for-media-stream',
      '--no-sandbox',
    ]
  });
  const page = await browser.newPage();

  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.toString()));

  const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiVGVzdCBDYW5kaWRhdGUiLCJ2aWRlbyI6eyJyb29tSm9pbiI6dHJ1ZSwicm9vbSI6ImNhbmRpZGF0ZV8xMjMiLCJjYW5QdWJsaXNoIjp0cnVlLCJjYW5TdWJzY3JpYmUiOnRydWUsImNhblB1Ymxpc2hEYXRhIjp0cnVlfSwic3ViIjoiY2FuZGlkYXRlXzEyMyIsImlzcyI6ImRldmtleSIsIm5iZiI6MTc4NzY1MjgwMCwiZXhwIjoxNzg3Njc0NDAwfQ.oGqhIyQ_DTjqFKOywULIJ6qlXCWlOzUcpD4PIySD8TU";
  const url = `http://localhost:3000/interview?token=${token}`;

  console.log("Navigating to", url);
  await page.goto(url, { waitUntil: 'networkidle2' });

  console.log("Clicking join button...");
  try {
    // The button has "Enter Interview Room" text
    await page.waitForFunction(() => {
      const btn = Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('Enter Interview'));
      if (btn) {
        btn.click();
        return true;
      }
      return false;
    });
    console.log("Clicked join!");
  } catch (err) {
    console.log("Could not click join:", err.message);
  }

  // Wait 10 seconds to see logs
  console.log("Waiting 15 seconds to collect WebRTC logs...");
  await new Promise(r => setTimeout(r, 15000));

  await browser.close();
})();
