#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from os.path import join
import csv
import os
import pathlib


def get_data_from_product_page(url: str) -> dict[str, str]:
    """
    Scrape the url page, extract all the product data and write them
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


def save_as_csv(path: str, name: str, books_data: list) -> None:
    """
    Save the book data in csv file at path/name.csv
    :param path: directory path of csv file
    :param name: name of csv file
    :param books_data: list containing dict of book data
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
        writer.writerows(books_data)


def get_all_product_url(url: str) -> list[str]:
    """
    Scrape the url page and extract all the link for book's page
    :param url: url of a category page
    :return: a list containing the url of all the book in this category page
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    products = soup.find_all("article", class_="product_pod")
    urls = []
    for product in products:
        urls.append(urljoin(url, product.find("a")['href']))
    return urls


def get_all_book_url_in_category(url: str) -> tuple[str, list[str]]:
    """
    Take the url of category's main page, and return a list of paginated pages url and the category's name, in tuple
    :param url:
    :return: tuple of category_name and url list
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    name = soup.find('div', class_='page-header').find('h1').text.lower()
    books_number = int(
        soup.find('form', class_="form-horizontal").find('strong').text
    )
    pages_number = books_number//20
    if books_number % 20 > 0:
        pages_number += 1
    links = get_all_product_url(url)
    for i in range(pages_number-1):
        links += get_all_product_url(
            urljoin(url, "page-" + str(i + 2) + ".html")
        )
    return name, links


def get_all_category_main_page(url: str = "http://books.toscrape.com/index.html") -> list[str]:
    """
    Scrape the main page of Books to Scrape and extract all the categories main pages
    :param url:
    :return: url list of the categories main pages
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find('ul', class_="nav-list").find('ul').find_all('a')
    categories_link = [urljoin(url, link['href']) for link in links]
    return categories_link


def recursive_directory_path_builder(path: str) -> None:
    """
    Check recursively if each parent exist else it make them
    :param path: the path of directory
    :return: None
    """
    if os.path.isfile(path):
        raise ValueError('invalid path, path is not a directory !')
    elif not os.path.isdir(path):
        recursive_directory_path_builder(pathlib.Path(path).parent)
        os.mkdir(path)




def main() -> None:
    """
    Get all book's data of all books in Books to Scrape, http://books.toscrape.com/index.html, and save them in some csv
    named by the category name
    :return: None
    """
    for category_main_page_url in get_all_category_main_page():
        category_name, books_url = get_all_book_url_in_category(category_main_page_url)
        books_data = [get_data_from_product_page(url) for url in books_url]
        save_as_csv('', category_name, books_data)


if __name__ == '__main__':
    main()
