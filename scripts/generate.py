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
            <a href="items/{item['id']}.html">
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
            <h3>{item['name']}</h3>
            <p>{item['summary']}</p>
            <a href="items/{item['id']}.html" class="detail-btn">詳細を見る</a>
        </div>
        """

    index_template = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IT関連アイテム紹介サイト</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="icon" href="favicon.ico">
</head>
<body>
    <header>
        <h1>ITアイテム セレクション</h1>
    </header>
    
    <section class="carousel-container">
        <div class="carousel-track">
            {carousel_html}
            {carousel_html} <!-- Duplicate for infinite effect -->
        </div>
    </section>

    <main>
        <section class="items-grid">
            {items_list_html}
        </section>
    </main>

    <footer>
        <p>&copy; 2026 ITアイテム紹介サイト</p>
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
            engineer_desc_html = f'<section class="engineer-context"><h3>Engineer\'s Point</h3><p>{item["engineer_desc"]}</p></section>'

        # Amazon Image Link
        amazon_image_link = ""
        asin = item.get('asin')
        if asin:
            # Check for multiple ASINs (if applicable) or handle string
            if isinstance(asin, list):
                asin = asin[0]
            amazon_image_link = f'<div class="amazon-image-link"><a href="{amazon_url}" target="_blank"><img src="https://images-na.ssl-images-amazon.com/images/P/{asin}.01.LZZZZZZZ.jpg" alt="Amazonで見る"><p>Amazonで詳しく見る</p></a></div>'

        item_template = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{item['name']} - ITアイテム紹介</title>
    <link rel="stylesheet" href="../css/style.css">
    <link rel="icon" href="../favicon.ico">
</head>
<body>
    <header>
        <h1><a href="../index.html">ITアイテム セレクション</a></h1>
    </header>
    
    <main class="item-detail">
        <img src="{item['image']}" alt="{item['name']}" class="detail-image">
        <h2>{item['name']}</h2>
        <p class="category">カテゴリ: {item['category']}</p>
        <p class="summary">{item['summary']}</p>
        
        <a href="{amazon_url}" class="amazon-btn" target="_blank">Amazonでチェックする</a>

        {engineer_desc_html}

        {amazon_image_link}

        <section class="sources">
            <h3>紹介されていた記事</h3>
            <ul>
                {sources_html}
            </ul>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 ITアイテム紹介サイト</p>
    </footer>
</body>
</html>
        """
        with open(f'dist/items/{item["id"]}.html', 'w', encoding='utf-8') as f:
            f.write(item_template)

    # CSS
    css_content = """
body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f9;
    color: #333;
}

header {
    background-color: #232f3e;
    color: white;
    padding: 1rem;
    text-align: center;
}

header h1 a {
    color: white;
    text-decoration: none;
}

.carousel-container {
    width: 100%;
    overflow: hidden;
    background: white;
    padding: 20px 0;
    border-bottom: 1px solid #ddd;
}

.carousel-track {
    display: flex;
    width: calc(250px * 10);
    animation: scroll 20s linear infinite;
}

@keyframes scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(calc(-250px * 5)); }
}

.carousel-item {
    width: 230px;
    margin: 0 10px;
    flex-shrink: 0;
    text-align: center;
}

.carousel-item img {
    width: 200px;
    height: 150px;
    object-fit: cover;
    border-radius: 8px;
}

.items-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.item-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    padding: 15px;
    text-align: center;
}

.item-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 4px;
}

.detail-btn, .amazon-btn {
    display: inline-block;
    background-color: #ff9900;
    color: #232f3e;
    padding: 10px 20px;
    text-decoration: none;
    border-radius: 4px;
    font-weight: bold;
    margin-top: 10px;
}

.amazon-btn {
    background-color: #f0c14b;
    border: 1px solid #a88734;
}

.amazon-image-link {
    margin-top: 20px;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    display: inline-block;
    background: #fff;
    text-align: center;
}

.amazon-image-link a {
    text-decoration: none;
    color: #333;
}

.amazon-image-link img {
    max-width: 150px;
    height: auto;
    display: block;
    margin: 0 auto 10px;
}

.item-detail {
    max-width: 800px;
    margin: 20px auto;
    background: white;
    padding: 30px;
    border-radius: 8px;
}

.engineer-context {
    background: #eef2f7;
    border-left: 4px solid #232f3e;
    padding: 15px;
    margin: 20px 0;
    border-radius: 0 4px 4px 0;
}

.engineer-context h3 {
    margin-top: 0;
    color: #232f3e;
    font-size: 1.1rem;
}

.detail-image {
    width: 100%;
    max-height: 400px;
    object-fit: cover;
    border-radius: 8px;
}

.sources {
    margin-top: 30px;
    border-top: 1px solid #eee;
    padding-top: 20px;
}

footer {
    text-align: center;
    padding: 20px;
    color: #888;
}
    """
    with open('dist/css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)

if __name__ == "__main__":
    main()
