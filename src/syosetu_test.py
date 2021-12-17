"""Exploring BeautifulSoup to scrape syosetu page"""
from bs4 import BeautifulSoup
from urllib.request import urlopen
import lxml 

url = r"https://ncode.syosetu.com/n7855ck/"
html = urlopen(url)
bs = BeautifulSoup(html, 'lxml')

