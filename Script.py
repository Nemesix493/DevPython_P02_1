#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from os.path import join
import csv


def get_data_from_product_page(url: str) -> dict[str, str]:
    """
    Scrap the url page, extract all the product data and write them
    in product_data dict
    :param url: page url
    :return: dict of extracted value
    """
    # Extraction
    response = requests.get(url)
    # Transformation
    soup = BeautifulSoup(response.content, 'html.parser')
    product_data = {'product_page_url': url}
    product = soup.find('div', class_='content')
    product_data['image_url'] = urljoin(url, product.find('img')['src'])
    if product.find('p', class_=''):
        product_data['product_description'] = product.find('p', class_='').text
    table_lines = product.find('table').find_all('tr')
    product_data['universal_product_code'] = table_lines[0].find('td').text
    product_data['price_excluding_tax'] = table_lines[2].find('td').text.replace('£', '')
    product_data['price_including_tax'] = table_lines[3].find('td').text.replace('£', '')
    product_data['review_rating'] = table_lines[6].find('td').text
    product_data['title'] = product.find('h1').text
    availability = product.find('p', class_='availability')
    if 'instock' in availability['class']:
        product_data['number_available'] = availability.text.replace(' ', '') \
            .replace('\n\n\nInstock(', '').replace('available)\n\n', '')
    else:
        product_data['number_available'] = '0'
    product_data['review_rating'] = product.find('p', class_='star-rating')['class'][1]
    product_data['category'] = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.replace('\n', '')
    return product_data


def save_as_csv(path: str, name: str, book_data: list) -> None:
    """
    Save the book data in csv file at path/name.csv
    :param path: directory path of csv file
    :param name: name of csv file
    :param book_data: list containing dict of book data
    :return: None
    """
    with open(join(path, name + '.csv'), 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, [
            'product_page_url',
            'image_url',
            'product_description',
            'universal_product_code',
            'price_excluding_tax',
            'price_including_tax',
            'review_rating',
            'title',
            'number_available',
            'category'], delimiter=',')
        writer.writeheader()
        writer.writerows(book_data)


def main() -> None:
    """
    Run the main code of this script
    :return: None
    """
    product_data = get_data_from_product_page("http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
    save_as_csv('', 'first_page', [product_data])


if __name__ == '__main__':
    main()
