import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def fetch_html(url):
    """Fetch the raw HTML content from the URL."""
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return response.text

def get_custom_xpath(tag):
    """Generate a custom XPath-like string based on tag and its attributes."""
    tag_name = tag.name
    id_attr = tag.get('id')
    class_attr = tag.get('class')

    attr_info = []
    if id_attr:
        attr_info.append(f"id='{id_attr}'")
    if class_attr:
        class_attr_str = " ".join(class_attr)
        attr_info.append(f"class='{class_attr_str}'")

    attr_str = " and ".join(attr_info)
    if attr_str:
        return f"{tag_name}[{attr_str}]"
    else:
        return tag_name

def extract_data_from_html(html):
    """Parse the HTML and extract data."""
    soup = BeautifulSoup(html, 'html.parser')
    data = []

    # Find all elements with text and either an id or class attribute
    elements = soup.find_all(lambda tag: tag.has_attr('id') or tag.has_attr('class') and tag.get_text(strip=True))

    for element in elements:
        text = element.get_text(strip=True)
        if text:
            element_html = str(element)
            element_and_class = get_custom_xpath(element)
            data.append({
                "Text": text,
                "Element HTML": element_html,
                "Element and Class": element_and_class,
                "Custom XPath": element_and_class
            })

    return data

def main():
    url = "https://www.samsung.com/au/price-promise/"  # Replace with your target URL
    html = fetch_html(url)
    extracted_data = extract_data_from_html(html)
    df = pd.DataFrame(extracted_data)

    # Define the directory
    directory = "D:/Output"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the Excel file in the specified directory
    excel_filename = f"{directory}/AllTextsAndHTML_BeautifulSoup.xlsx"
    df.to_excel(excel_filename, index=False)
    print(f"Data has been successfully extracted and saved to Excel at {excel_filename}.")

if __name__ == "__main__":
    main()
