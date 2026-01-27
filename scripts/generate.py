import json
import os

ASSOCIATE_ID = "ukiuni-22"

def generate_amazon_link(asin, name):
    if asin:
        return f"https://www.amazon.co.jp/dp/{asin}/?tag={ASSOCIATE_ID}"
    return f"https://www.amazon.co.jp/s?k={name}&tag={ASSOCIATE_ID}"

def main():
    # Load base items
    with open('data/items.json', 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    # Load and merge cached items if they exist
    cache_dir = 'data/cache'
    if os.path.exists(cache_dir):
        for filename in os.listdir(cache_dir):
            if filename.endswith('.json'):
                with open(os.path.join(cache_dir, filename), 'r', encoding='utf-8') as f:
                    cached_items = json.load(f)
                    # Merge by ID to avoid duplicates
                    item_ids = {item['id'] for item in items}
                    for c_item in cached_items:
                        if c_item['id'] not in item_ids:
                            items.append(c_item)
                            item_ids.add(c_item['id'])

    # index.html
    carousel_html = ""
    for item in items:
        carousel_html += f"""
        <div class="carousel-item">
            <a href="items/{item['id']}.html" style="text-decoration:none; color:inherit;">
                <img src="{item['image']}" alt="{item['name']}">
                <p>{item['name']}</p>
            </a>
        </div>
        """

    items_list_html = ""
    for item in items:
        items_list_html += f"""
        <div class="item-card">
            <img src="{item['image']}" alt="{item['name']}">
            <div class="item-content">
                <h3>{item['name']}</h3>
                <p>{item['summary']}</p>
                <a href="items/{item['id']}.html" class="detail-btn">詳細を見る</a>
            </div>
        </div>
        """

    index_template = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ITアイテム セレクション | エンジニアのための究極のガジェットガイド</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="icon" href="favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <h1><a href="index.html">IT Item Selection</a></h1>
    </header>

    <section class="hero">
        <h2>エンジニアの生産性を、<br>極限まで高める道具たち。</h2>
        <p>現役開発者のレビューから厳選された、ソフトウェア開発現場で真に価値を発揮するガジェットガイド。</p>
    </section>
    
    <section class="carousel-container">
        <div class="carousel-track">
            {carousel_html}
            {carousel_html} <!-- Duplicate for infinite effect -->
        </div>
    </section>

    <main>
        <h2 class="section-title">Latest Items</h2>
        <section class="items-grid">
            {items_list_html}
        </section>
    </main>

    <footer>
        <p>&copy; 2026 IT Item Selection. Curated for Developers.</p>
    </footer>
</body>
</html>
    """
    
    with open('dist/index.html', 'w', encoding='utf-8') as f:
        f.write(index_template)

    # Item pages
    for item in items:
        amazon_url = generate_amazon_link(item.get('asin'), item['name'])
        sources_html = "".join([f'<li><a href="{s["url"]}" target="_blank">{s["title"]}</a></li>' for s in item['sources']])
        
        # Engineer Description
        engineer_desc_html = ""
        if item.get('engineer_desc'):
            engineer_desc_html = f'''
            <section class="engineer-context">
                <h3>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
                    Engineer's Point
                </h3>
                <p>{item["engineer_desc"]}</p>
            </section>
            '''

        # Amazon Image Link
        amazon_image_link = ""
        asin = item.get('asin')
        if asin:
            if isinstance(asin, list):
                asin = asin[0]
            amazon_image_link = f'''
            <div class="amazon-image-link">
                <img src="https://images-na.ssl-images-amazon.com/images/P/{asin}.01.LZZZZZZZ.jpg" alt="Amazonで見る">
                <div>
                    <p style="margin:0 0 10px 0; font-weight:600;">この商品をAmazonで詳しく見る</p>
                    <a href="{amazon_url}" class="amazon-btn" target="_blank">Amazonでチェック</a>
                </div>
            </div>
            '''

        item_template = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{item['name']} | IT Item Selection</title>
    <link rel="stylesheet" href="../css/style.css">
    <link rel="icon" href="../favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <h1><a href="../index.html">IT Item Selection</a></h1>
    </header>
    
    <main class="item-detail">
        <img src="{item['image']}" alt="{item['name']}" class="detail-image">
        <h2>{item['name']}</h2>
        <div style="display:flex; gap:10px; margin-bottom:20px;">
            <span style="background:#e2e8f0; padding:4px 12px; border-radius:20px; font-size:0.85rem; font-weight:600;">{item['category']}</span>
        </div>
        <p class="summary" style="font-size:1.1rem; color:#334155; margin-bottom:30px;">{item['summary']}</p>
        
        {engineer_desc_html}

        {amazon_image_link}

        <section class="sources">
            <h3 style="font-size:1.25rem; margin-bottom:20px;">紹介・レビュー記事</h3>
            <ul style="padding-left:20px; color:#475569;">
                {sources_html}
            </ul>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 IT Item Selection. Curated for Developers.</p>
    </footer>
</body>
</html>
        """
        with open(f'dist/items/{item["id"]}.html', 'w', encoding='utf-8') as f:
            f.write(item_template)

    # CSS
    css_content = """
:root {
    --primary: #2563eb;
    --primary-dark: #1e40af;
    --accent: #f59e0b;
    --bg-main: #f8fafc;
    --bg-card: #ffffff;
    --text-main: #1e293b;
    --text-muted: #64748b;
    --header-bg: rgba(15, 23, 42, 0.9);
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 0;
    background-color: var(--bg-main);
    color: var(--text-main);
    line-height: 1.6;
}

header {
    background-color: var(--header-bg);
    backdrop-filter: blur(10px);
    color: white;
    padding: 1.5rem;
    text-align: center;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

header h1 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    text-transform: uppercase;
}

header h1 a {
    color: white;
    text-decoration: none;
}

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: white;
    padding: 6rem 2rem;
    text-align: center;
}

.hero h2 {
    font-size: 2.5rem;
    margin-bottom: 1.5rem;
    font-weight: 800;
    line-height: 1.2;
}

.hero p {
    font-size: 1.1rem;
    color: #cbd5e1;
    max-width: 600px;
    margin: 0 auto;
}

.carousel-container {
    width: 100%;
    overflow: hidden;
    background: white;
    padding: 60px 0;
    border-bottom: 1px solid #e2e8f0;
}

.carousel-track {
    display: flex;
    width: fit-content;
    animation: scroll 60s linear infinite;
}

@keyframes scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

.carousel-item {
    width: 320px;
    margin: 0 20px;
    flex-shrink: 0;
}

.carousel-item img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 16px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.carousel-item:hover img {
    transform: scale(1.05);
}

.carousel-item p {
    margin-top: 15px;
    font-weight: 600;
    font-size: 0.95rem;
    text-align: center;
}

.section-title {
    text-align: center;
    font-size: 2.25rem;
    margin: 4rem 0 3rem;
    font-weight: 800;
    color: #0f172a;
}

.items-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 40px;
    padding: 0 20px;
    max-width: 1200px;
    margin: 0 auto 6rem;
}

.item-card {
    background: var(--bg-card);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    border: 1px solid #f1f5f9;
}

.item-card:hover {
    transform: translateY(-12px);
    box-shadow: 0 25px 30px -5px rgba(0, 0, 0, 0.15);
}

.item-card img {
    width: 100%;
    height: 240px;
    object-fit: cover;
}

.item-content {
    padding: 28px;
}

.item-card h3 {
    margin: 0 0 14px;
    font-size: 1.4rem;
    font-weight: 700;
}

.item-card p {
    color: var(--text-muted);
    font-size: 0.95rem;
    margin-bottom: 24px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    height: 3rem;
}

.detail-btn {
    display: block;
    background-color: var(--primary);
    color: white;
    padding: 14px;
    text-align: center;
    text-decoration: none;
    border-radius: 12px;
    font-weight: 700;
    transition: all 0.2s;
}

.detail-btn:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
}

.item-detail {
    max-width: 900px;
    margin: 60px auto;
    background: white;
    padding: 50px;
    border-radius: 32px;
    box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.12);
}

.detail-image {
    width: 100%;
    max-height: 550px;
    object-fit: cover;
    border-radius: 24px;
    margin-bottom: 40px;
}

.amazon-btn {
    display: inline-block;
    background: linear-gradient(135deg, #fcd34d 0%, #fbbf24 100%);
    border: 1px solid #d97706;
    color: #78350f;
    padding: 16px 32px;
    text-decoration: none;
    border-radius: 12px;
    font-weight: 800;
    font-size: 1.1rem;
    transition: all 0.2s;
}

.amazon-btn:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(217, 119, 6, 0.2);
}

.engineer-context {
    background: #f1f5f9;
    border-left: 6px solid var(--primary);
    padding: 30px;
    margin: 40px 0;
    border-radius: 0 16px 16px 0;
}

.engineer-context h3 {
    margin-top: 0;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 1.3rem;
    font-weight: 800;
}

.amazon-image-link {
    background: #fff;
    border: 2px solid #f1f5f9;
    border-radius: 16px;
    padding: 25px;
    margin: 40px 0;
    display: flex;
    align-items: center;
    gap: 30px;
}

.amazon-image-link img {
    max-width: 160px;
    height: auto;
    border-radius: 8px;
}

.sources {
    margin-top: 50px;
    border-top: 2px solid #f1f5f9;
    padding-top: 40px;
}

.sources ul li {
    margin-bottom: 12px;
}

.sources a {
    color: var(--primary);
    text-decoration: none;
    font-weight: 600;
}

.sources a:hover {
    text-decoration: underline;
}

footer {
    text-align: center;
    padding: 5rem 2rem;
    background: #0f172a;
    color: #94a3b8;
    font-size: 0.95rem;
}
    """
    with open('dist/css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)

if __name__ == "__main__":
    main()
