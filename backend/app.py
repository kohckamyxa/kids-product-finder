from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import urllib.parse
# --- Main Selenium Import ---
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# --- Undetected Chromedriver Import ---
import undetected_chromedriver as uc
from googletrans import Translator

# --- Setup ---
app = Flask(__name__)
CORS(app)
translator = Translator()

# --- Store Configuration ---
# All store-specific details, including search URLs and CSS selectors, are now here.
STORES = [
    {
        "name": "Babadut.dk",
        "language": "da",
        "affiliate_network": "Partner-ads",
        "affiliate_template": "https://www.partner-ads.com/dk/klikbanner.php?partnerid=55323&bannerid=88630&htmlurl={product_url}",
        "search_template": "https://babadut.dk/search?search={query}",
        "selectors": {
            "link": {"by": By.CLASS_NAME, "value": "productEntityClick"},
            "price": {"by": By.CLASS_NAME, "value": "product-price"}
        }
    },
    {
        "name": "Babymart.dk",
        "language": "da",
        "affiliate_network": "Partner-ads",
        "affiliate_template": "https://www.partner-ads.com/dk/klikbanner.php?partnerid=55323&bannerid=114447&htmlurl={product_url}",
        "search_template": "https://babymart.dk/search?q={query}",
        "selectors": {
            "link": {"by": By.CLASS_NAME, "value": "product-card-link"},
            "price": {"by": By.CLASS_NAME, "value": "price-item--regular"}
        }
    },
    {
        "name": "Babysleepy.dk",
        "language": "da",
        "affiliate_network": "Partner-ads",
        "affiliate_template": "https://www.partner-ads.com/dk/klikbanner.php?partnerid=55323&bannerid=113196&htmlurl={product_url}",
        "search_template": "https://babysleepy.dk/search?q={query}",
        "selectors": {
            # Shopify Standard Selectors
            "link": {"by": By.CLASS_NAME, "value": "product-item__image-wrapper"},
            "price": {"by": By.CLASS_NAME, "value": "price"}
        }
    },
    {
        "name": "Billigwallsticker.dk",
        "language": "da",
        "affiliate_network": "Partner-ads",
        "affiliate_template": "https://www.partner-ads.com/dk/klikbanner.php?partnerid=55323&bannerid=63203&htmlurl={product_url}",
        "search_template": "https://billigwallsticker.dk/?s={query}&post_type=product",
        "selectors": {
            # WooCommerce Standard Selectors
            "link": {"by": By.CLASS_NAME, "value": "woocommerce-LoopProduct-link"},
            "price": {"by": By.CSS_SELECTOR, "value": "p.price .woocommerce-Price-amount"}
        }
    },
    {
        "name": "Borncopenhagen.dk",
        "language": "da",
        "affiliate_network": "Partner-ads",
        "affiliate_template": "https://www.partner-ads.com/dk/klikbanner.php?partnerid=55323&bannerid=114809&htmlurl={product_url}",
        "search_template": "https://borncopenhagen.dk/search?q={query}",
        "selectors": {
            # Shopify Standard Selectors
            "link": {"by": By.CLASS_NAME, "value": "product-item__image-wrapper"},
            "price": {"by": By.CLASS_NAME, "value": "price"}
        }
    },
    {
        "name": "Buump.com",
        "language": "da",
        "affiliate_network": "Partner-ads",
        "affiliate_template": "https://www.partner-ads.com/dk/klikbanner.php?partnerid=55323&bannerid=71817&htmlurl={product_url}",
        "search_template": "https://buump.com/search?q={query}",
        "selectors": {
            # Shopify Standard Selectors
            "link": {"by": By.CLASS_NAME, "value": "product-item__image-wrapper"},
            "price": {"by": By.CLASS_NAME, "value": "price"}
        }
    }
]

# --- Generic Scraper Function ---
def scrape_product_with_selenium(store_config, product_name, product_ean):
    """
    A generic Selenium scraper that uses configuration for each store.
    It runs the browser invisibly in headless mode.
    """
    # Prefer EAN for search query if available
    query = product_ean if product_ean else urllib.parse.quote_plus(product_name)
    search_url = store_config["search_template"].format(query=query)
    
    driver = None
    try:
        print(f"-> Initializing UNDETECTED Selenium driver for {store_config['name']}...")
        
        # --- Headless Options ---
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = uc.Chrome(options=options, use_subprocess=True)

        print(f"-> Navigating to search URL: {search_url}")
        driver.get(search_url)

        wait = WebDriverWait(driver, 15)
        
        # --- Find product link using selectors from config ---
        print("-> Waiting for product link...")
        link_selector = store_config["selectors"]["link"]
        product_link_element = wait.until(
            EC.presence_of_element_located((link_selector["by"], link_selector["value"]))
        )
        product_url = product_link_element.get_attribute('href')
        print(f"-> Found product link: {product_url}")

        print("-> Navigating to product page...")
        driver.get(product_url)
        
        # --- Find price using selectors from config ---
        print("-> Waiting for price...")
        price_selector = store_config["selectors"]["price"]
        price_element = wait.until(
            EC.presence_of_element_located((price_selector["by"], price_selector["value"]))
        )
        
        price = price_element.text.strip()
        print(f"-> Found price: {price}")
        return {"price": price, "url": product_url}

    except Exception as e:
        print(f"!!! Error scraping {store_config['name']}: {e}")
        return None
    finally:
        if driver:
            print(f"-> Closing Selenium driver for {store_config['name']}.")
            driver.quit()


# --- Main API Endpoint ---
@app.route('/api/search', methods=['POST'])
def handle_search():
    data = request.get_json()
    product_name = data.get('productName')
    product_ean = data.get('productEan')
    source_lang = data.get('sourceLang', 'en')

    if not product_name:
        return jsonify({"error": "No productName provided"}), 400

    results = []

    for store in STORES:
        search_name = product_name
        store_lang = store.get("language", "en")

        if source_lang != store_lang:
            try:
                print(f"-> Translating '{product_name}' from {source_lang} to {store_lang}...")
                translation = translator.translate(product_name, src=source_lang, dest=store_lang)
                search_name = translation.text
                print(f"-> Translated name: '{search_name}'")
            except Exception as e:
                print(f"!!! Translation failed: {e}")
                # Fallback to original name if translation fails
                search_name = product_name
        
        # --- Call the generic scraper with the store's config ---
        print(f"\n--- Scraping {store['name']} ---")
        scraped_data = scrape_product_with_selenium(store, search_name, product_ean)
        
        if scraped_data and scraped_data.get("url"):
            product_url = scraped_data["url"]
            affiliate_link = store["affiliate_template"].format(product_url=product_url)
            
            results.append({
                "store_name": store["name"],
                "price": scraped_data["price"],
                "url": affiliate_link
            })

    return jsonify({"status": "success", "results": results})

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
