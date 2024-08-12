import requests
from bs4 import BeautifulSoup


class CommonPage:
    def __init__(self, url):
        self.url = url
        self.soup = None

    def fetch_content(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching the URL {self.url}: {e}")

    def get_image_details(self):
        if self.soup is None:
            self.fetch_content()

        img_tags = self.soup.find_all('img')
        image_details = []
        for img in img_tags:
            element_html = str(img)
            for attr_key, attr_value in img.attrs.items():
                if 'alt' in attr_key.lower():
                    image_details.append([self.url, element_html, attr_key, attr_value])

        return image_details
