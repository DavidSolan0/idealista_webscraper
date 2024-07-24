import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class IdealistaScraper:
    """
    Clase para realizar scraping de anuncios en el sitio web de Idealista.

    Parameters
    ----------
    url : str
        La URL del anuncio en Idealista.

    Attributes
    ----------
    url : str
        La URL del anuncio.
    headers : dict
        Encabezados HTTP para la solicitud.
    announcement_info : dict
        Diccionario para almacenar la información del anuncio.
    soup : BeautifulSoup
        Objeto BeautifulSoup para parsear el HTML del anuncio.

    Methods
    -------
    fetch_page()
        Realiza la solicitud HTTP y parsea el HTML de la página del anuncio.
    get_title()
        Obtiene el título del anuncio.
    get_reference()
        Obtiene la referencia del anuncio.
    get_price()
        Obtiene el precio del anuncio.
    get_info_features()
        Obtiene las características de información del anuncio.
    get_caracteristicas_basicas()
        Obtiene las características básicas del anuncio.
    get_certificado_energetico()
        Obtiene el certificado energético del anuncio.
    get_price_features()
        Obtiene las características de precio del anuncio.
    get_ubicacion()
        Obtiene la ubicación del anuncio.
    scrape()
        Realiza todo el proceso de scraping y devuelve la información del anuncio.
    """

    def __init__(self, url):
        self.url = url
        self.headers = {
            "User-Agent": UserAgent().random,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.google.com/",
        }
        self.announcement_info = {}
        self.soup = None

    def fetch_page(self):
        """
        Realiza la solicitud HTTP y parsea el HTML de la página del anuncio.

        Raises
        ------
        ValueError
            Si la solicitud HTTP falla.
        """
        response = requests.get(self.url, headers=self.headers, timeout=120)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.content, "html.parser")
        else:
            raise ValueError(
                f"Failed to fetch page with status code: {response.status_code}"
            )

    def get_title(self):
        """
        Obtiene el título del anuncio y lo guarda en announcement_info.
        """
        self.announcement_info["title"] = self.soup.title.string.strip()

    def get_reference(self):
        """
        Obtiene la referencia del anuncio y la guarda en announcement_info.
        """
        reference_tags = self.soup.find_all("p", class_="txt-ref")
        for ref_tag in reference_tags:
            ref_number = ref_tag.text.strip()
            self.announcement_info["referencia_anuncio"] = ref_number

    def get_price(self):
        """
        Obtiene el precio del anuncio y lo guarda en announcement_info.
        """
        info_data_divs = self.soup.find_all("div", class_="info-data")
        for info_div in info_data_divs:
            price_span = info_div.find("span", class_="info-data-price")
            if price_span:
                price = price_span.find("span", class_="txt-bold").text.strip()
                self.announcement_info["price"] = price

    def get_info_features(self):
        """
        Obtiene las características de información del anuncio y las guarda en
        announcement_info.
        """
        info_features_divs = self.soup.find_all("div", class_="info-features")
        for features_div in info_features_divs:
            features = [span.text.strip() for span in features_div.find_all("span")]
            self.announcement_info["info_features"] = features

    def get_caracteristicas_basicas(self):
        """
        Obtiene las características básicas del anuncio y las guarda en announcement_info.
        """
        details_div = self.soup.find("div", class_="details-property-feature-one")
        if details_div:
            headings = details_div.find_all("h2", class_="details-property-h2")
            for heading in headings:
                if "Características básicas" in heading.text:
                    next_div = heading.find_next_sibling(
                        "div", class_="details-property_features"
                    )
                    if next_div:
                        ul_tags = next_div.find_all("ul")
                        for ul in ul_tags:
                            items = [li.text.strip() for li in ul.find_all("li")]
                            self.announcement_info["caracteristicas_basicas"] = items

    def get_certificado_energetico(self):
        """
        Obtiene el certificado energético del anuncio y lo guarda en announcement_info.
        """
        certificate_div = self.soup.find("div", class_="details-property-feature-two")
        if certificate_div:
            headings = certificate_div.find_all("h2", class_="details-property-h2")
            for heading in headings:
                if "Certificado energético" in heading.text:
                    next_div = heading.find_next_sibling(
                        "div", class_="details-property_features"
                    )
                    if next_div:
                        ul_tags = next_div.find_all("ul")
                        items = []
                        for li in ul_tags[0].find_all("li"):
                            title_span = li.find_all("span")[0]
                            value_span = li.find_all("span")[1]

                            title = title_span.text.strip()
                            value = value_span.text.strip()
                            icon_class = value_span.get("class", [""])[0]

                            items.append({title: [value, icon_class]})

                        self.announcement_info["certificado_energetico"] = items

    def get_price_features(self):
        """
        Obtiene las características de precio del anuncio y las guarda en announcement_info.
        """
        price_article = self.soup.find("article", class_="price-feature")
        if price_article:
            price_info = price_article.find_all("p", class_="flex-feature")
            for p in price_info:
                label_span = p.find("span", class_="flex-feature-details")
                value_strong = p.find("strong", class_="flex-feature-details")
                if value_strong:
                    value = value_strong.get_text(strip=True)
                else:
                    value = (
                        p.get_text(strip=True)
                        .replace(label_span.get_text(strip=True), "")
                        .strip()
                    )
                if label_span:
                    label = label_span.get_text(strip=True)
                    if "Precio del inmueble" in label or "Precio por m²" in label:
                        self.announcement_info[label] = value

    def get_ubicacion(self):
        """
        Obtiene la ubicación del anuncio y la guarda en announcement_info.
        """
        location_div = self.soup.find("div", id="headerMap")
        if location_div:
            location_items = location_div.find_all("li", class_="header-map-list")
            location_info = [item.get_text(strip=True) for item in location_items]
            self.announcement_info["ubicacion"] = location_info

    def scrape(self):
        """
        Realiza todo el proceso de scraping y devuelve la información del anuncio.

        Returns
        -------
        dict
            Diccionario con la información del anuncio.
        """
        self.fetch_page()
        self.get_title()
        self.get_reference()
        self.get_price()
        self.get_info_features()
        self.get_caracteristicas_basicas()
        self.get_certificado_energetico()
        self.get_price_features()
        self.get_ubicacion()
        return self.announcement_info
