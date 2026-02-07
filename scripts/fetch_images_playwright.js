const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

function sleep(ms){return new Promise(r=>setTimeout(r,ms));}

(async ()=>{
  const base=path.resolve(__dirname,'..');
  const cacheDir=path.join(process.env.HOME,'.cache/ms-playwright','chromium_headless_shell-1208','chrome-linux');
  const executable=process.env.CHROME_PATH || path.join(cacheDir,'headless_shell');
  const itemsPath=path.join(base,'data','items.json');
  const assetsDir=path.join(base,'dist','assets');
  if(!fs.existsSync(assetsDir)) fs.mkdirSync(assetsDir,{recursive:true});
  const items=JSON.parse(fs.readFileSync(itemsPath,'utf8'));

  const browser = await chromium.launch({headless:true, executablePath: executable, args:['--no-sandbox','--disable-dev-shm-usage','--single-process']}).catch(e=>{console.error('LAUNCH_ERR',e);process.exit(1)});
  const context = await browser.newContext({viewport:{width:1280,height:900}, userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'});
  const page = await context.newPage();
  page.setDefaultTimeout(90000);

  async function tryGetMainImageFromPage(page, referer){
    // handle cookie popups / dismiss buttons
    try{ await page.locator('button:has-text("同意"), button:has-text("Accept"), button:has-text("閉じる"), button:has-text("×"), button[aria-label*="close"]').first().click({timeout:2000}).catch(()=>{}); }catch(e){}
    await sleep(800);
    // try og:image
    const og = await page.$eval('meta[property="og:image"]',m=>m.content).catch(()=>null);
    if(og) return og;
    // try common selectors, prefer large images
    const candidates = await page.$$eval('img', imgs => imgs.map(i=>({src:i.src||i.getAttribute('data-src')||'', w:i.naturalWidth, h:i.naturalHeight, alt:i.alt||''})).filter(i=>i.src));
    if(candidates.length===0) return null;
    // pick largest by area
    candidates.sort((a,b)=> (b.w*b.h)-(a.w*a.h));
    return candidates[0].src || null;
  }

  let runDownloaded=0;
  for(const it of items){
    try{
      if(it.image && it.image.startsWith('./dist/assets/')){ console.log('SKIP',it.id); continue; }
      const q=encodeURIComponent(it.name);
      const searchUrls = [
        `https://search.rakuten.co.jp/search/mall/${q}/`,
        `https://www.google.com/search?tbm=shop&q=${q}`,
        `https://shopping.yahoo.co.jp/search?p=${q}`
      ];
      let found=false;
      let pageUrl=null;
      for(const searchUrl of searchUrls){
        console.log('SEARCH',it.id,searchUrl);
        try{
          await page.goto(searchUrl,{waitUntil:'networkidle'}).catch(()=>{});
          // dismiss cookie/popups
          await page.locator('button:has-text("同意"), button:has-text("Accept"), button:has-text("閉じる"), button:has-text("×")').first().click({timeout:2000}).catch(()=>{});
          await sleep(1000);
          // scroll to load lazy images and links
          for(let s=0;s<5;s++){ await page.evaluate(()=>window.scrollBy(0,window.innerHeight)); await sleep(500); }
          // try to find product link
          const href = await page.$eval('a[href*="item.rakuten.co.jp"], a[data-rakuten-item-url], a[data-gtm-product-id], a[href*="shopping.yahoo"]', a=>a.href).catch(()=>null);
          const link = href || await page.evaluate(()=>{
            const anchors = Array.from(document.querySelectorAll('a'));
            const a = anchors.find(x=>/item|shop|product|detail/.test(x.href));
            return a?.href || null;
          })||null;
          if(!link){ console.log('NO_LINK_ON',searchUrl); continue; }
          pageUrl = link;
          found=true;
          break;
        }catch(e){ console.log('SEARCH_ERR',it.id,e.message); }
      }
      if(!found || !pageUrl){ console.log('NO_LINK',it.id); continue; }
      console.log('LINK',it.id,pageUrl);
      // open product page with retries
      let imgUrl=null;
      for(let attempt=0;attempt<3 && !imgUrl;attempt++){
        try{
          await page.goto(pageUrl,{waitUntil:'domcontentloaded'}).catch(()=>{});
          await sleep(1000+attempt*1000);
          // scroll product page to trigger lazy images
          for(let s=0;s<6;s++){ await page.evaluate(()=>window.scrollBy(0,window.innerHeight/2)); await sleep(400); }
          imgUrl = await tryGetMainImageFromPage(page,pageUrl);
          if(imgUrl) break;
          // try clicking thumbnails to reveal main image
          const thumbs = await page.$$('img');
          for(const t of thumbs.slice(0,8)){
            try{ await t.click({timeout:500}).catch(()=>{}); await sleep(500); imgUrl = await tryGetMainImageFromPage(page,pageUrl); if(imgUrl) break; }catch(e){}
          }
        }catch(e){ console.log('PAGE_ERR',it.id,e.message); }
      }
      if(!imgUrl){ console.log('NO_IMG',it.id); continue; }
      const url = new URL(imgUrl, pageUrl).toString();
      const ext = (path.extname(new URL(url).pathname).split('?')[0] || '.jpg') || '.jpg';
      const out = path.join(assetsDir, it.id + ext);
      try{
        const res = await page.request.get(url,{timeout:60000});
        const buffer = await res.body();
        fs.writeFileSync(out,buffer);
        it.image = './dist/assets/'+path.basename(out);
        runDownloaded++;
        console.log('SAVED',it.id,url);
      }catch(e){ console.log('DL_ERR',it.id,e.message); }
    }catch(e){ console.log('ERR',it.id,e.message); }
  }
  fs.writeFileSync(itemsPath,JSON.stringify(items,null,2),'utf8');
  await browser.close();
  console.log('DONE', 'downloaded_in_run=', runDownloaded);
})();
