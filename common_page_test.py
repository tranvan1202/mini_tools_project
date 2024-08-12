import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from common_page import CommonPage  # Import the WebPage class from the module where it's defined

# Function to process a single URL
def process_url(url):
    page = CommonPage(url)
    return page.get_image_details()

# List of URLs to scrape
urls = [
    'https://www.samsung.com/th/smartphones/galaxy-a/galaxy-a55-5g-awesome-iceblue-256gb-sm-a556elbdthl/buy/',
    'https://www.samsung.com/th/lifestyle-tvs/the-frame/ls03d-43-inch-black-qa43ls03dakxxt/',
    # Add more URLs as needed
]

# Collect data from all URLs in parallel
all_image_details = []
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(process_url, url): url for url in urls}
    for future in as_completed(futures):
        try:
            image_details = future.result()
            all_image_details.extend(image_details)
        except Exception as e:
            print(f"Error processing URL {futures[future]}: {e}")

# Create a DataFrame
df = pd.DataFrame(all_image_details, columns=['URL', 'Element Locator', 'Alt Attribute Key', 'Alt text value'])

# Export the DataFrame to a CSV file with UTF-8 encoding
output_csv = 'image_details.csv'
df.to_csv(output_csv, index=False, encoding='utf-8')

# Print the DataFrame
print(df)
print(f'Results have been exported to {output_csv}')
