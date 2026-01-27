const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async ()=>{
  const base=path.resolve(__dirname,'..');
  const cacheDir=path.join(process.env.HOME,'.cache/ms-playwright','chromium_headless_shell-1208','chrome-linux');
  // Playwright downloaded headless_shell binary
  const executable=process.env.CHROME_PATH || path.join(cacheDir,'headless_shell');
  const itemsPath=path.join(base,'data','items.json');
  const assetsDir=path.join(base,'dist','assets');
  if(!fs.existsSync(assetsDir)) fs.mkdirSync(assetsDir,{recursive:true});
  const items=JSON.parse(fs.readFileSync(itemsPath,'utf8'));
  const browser = await chromium.launch({headless:true, executablePath: executable, args:['--no-sandbox','--disable-dev-shm-usage','--single-process']}).catch(e=>{console.error('LAUNCH_ERR',e);process.exit(1)});
  const page = await browser.newPage({timeout:60000});
  // Use a common desktop UA and reasonable viewport to get consistent pages
  await page.context().setExtraHTTPHeaders({ 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' });
  await page.setViewportSize({width:1280,height:800});
  for(const it of items){
    try{
      if(it.image && it.image.startsWith('./dist/assets/')){ console.log('SKIP',it.id); continue; }
      const q=encodeURIComponent(it.name);
      const searchUrl=`https://search.rakuten.co.jp/search/mall/${q}/`;
      console.log('SEARCH',it.id);
      await page.goto(searchUrl,{waitUntil:'networkidle'});
      // try several selectors to find the first product link
      const href = await page.$eval('a[href*="item.rakuten.co.jp"], a[data-rakuten-item-url], a.searchResultItem', a=>a.href).catch(()=>null);
      const link = href || await page.evaluate(()=>{
        const a = Array.from(document.querySelectorAll('a')).find(x=>/item|shop/.test(x.href));
        return a?.href || null;
      })||null;
      if(!link){ console.log('NO_LINK',it.id); continue; }
      console.log('LINK',link);
      await page.goto(link,{waitUntil:'domcontentloaded'});
      // wait a bit for images to load, then attempt several ways to locate the main image
      await page.waitForTimeout(500);
      const og = await page.$eval('meta[property="og:image"]',m=>m.content).catch(()=>null);
      let img = og;
      if(!img){ img = await page.$eval('img.main-image, img.p-image, img[itemprop="image"], img', i=>i.src).catch(()=>null); }
      if(!img){ console.log('NO_IMG',it.id); continue; }
      const url = new URL(img, link).toString();
      const ext = path.extname(new URL(url).pathname).split('?')[0] || '.jpg';
      const out = path.join(assetsDir, it.id + ext);
      const res = await page.request.get(url);
      const buffer = await res.body();
      fs.writeFileSync(out,buffer);
      it.image = './dist/assets/'+path.basename(out);
      console.log('SAVED',it.id,url);
    }catch(e){ console.log('ERR',it.id,e.message); }
  }
  fs.writeFileSync(itemsPath,JSON.stringify(items,null,2),'utf8');
  await browser.close();
  console.log('DONE');
})();
