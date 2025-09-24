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
STORES = [
    {
        "name": "Babadut.dk",
        "language": "da",
        "affiliate_network": "Partner-ads",
        "affiliate_template": "https://www.partner-ads.com/dk/klikbanner.php?partnerid=55323&bannerid=88630&htmlurl={product_url}",
        "scraper_function": "scrape_babadut_product_with_selenium"
    }
]

# --- Scraper Functions ---
def scrape_babadut_product_with_selenium(product_name, product_ean):
    """
    This version runs the Selenium browser invisibly in headless mode.
    """
    query = product_ean if product_ean else urllib.parse.quote_plus(product_name)
    search_url = f"https://babadut.dk/search?search={query}"
    
    driver = None
    try:
        print("-> Initializing UNDETECTED Selenium driver in HEADLESS mode...")
        
        # --- ADDING HEADLESS OPTIONS ---
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu') # Often recommended for headless mode
        driver = uc.Chrome(options=options, use_subprocess=True)
        # --- END OF ADDED OPTIONS ---

        print(f"-> Navigating to search URL: {search_url}")
        driver.get(search_url)

        wait = WebDriverWait(driver, 15)
        
        print("-> Waiting for product link to appear...")
        product_link_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "productEntityClick"))
        )
        product_url = product_link_element.get_attribute('href')
        print(f"-> Found product link: {product_url}")

        print("-> Navigating to product page...")
        driver.get(product_url)
        
        print("-> Waiting for price to appear...")
        price_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-price"))
        )
        
        price = price_element.text.strip()
        print(f"-> Found price: {price}")
        return {"price": price, "url": product_url}

    except Exception as e:
        print(f"!!! Error scraping Babadut with Selenium: {e}")
        return None
    finally:
        if driver:
            print("-> Closing Selenium driver.")
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
                search_name = product_name

        scraper_func_name = store["scraper_function"]
        scraper_function = globals().get(scraper_func_name)
        
        if scraper_function:
            scraped_data = scraper_function(search_name, product_ean)
            
            if scraped_data and scraped_data.get("url"):
                product_url = scraped_data["url"]
                # No extra encoding is needed for this specific affiliate link structure
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