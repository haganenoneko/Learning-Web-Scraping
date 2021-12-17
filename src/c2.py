"""c2 Advanced HTML parsing"""

from urllib.request import urlopen 
from bs4 import BeautifulSoup
import lxml

def html_as_soup(link: str, parser: str='html.parser') -> BeautifulSoup:
    
    try:
        html = urlopen(link)
        bs = BeautifulSoup(html, parser)
    except ValueError:
        bs = BeautifulSoup(link, parser)
    
    return bs 

"""
Find things between
<span> class='...' </span>
objects. 
"""
def page35():    
    bs = html_as_soup(r"http://www.pythonscraping.com/pages/page1.html")
    
    # look for a tag with a certain CSS class 
    nameList = bs.find_all('title')
    
    for name in nameList: 
        print(name.get_text())
        
def page41():
    bs = html_as_soup(r"http://www.pythonscraping.com/pages/page3.html")
    
    for child in bs.find('table', {'id' : 'giftList'}).tr.next_siblings:
        print(child)
    
page41()