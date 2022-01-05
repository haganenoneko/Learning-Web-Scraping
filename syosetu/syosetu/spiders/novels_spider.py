# Copyright (c) 2022 Delbert Yip
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import scrapy 
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule 
from scrapy.linkextractors import LinkExtractor

from datetime import datetime 
from typing import List, Dict, Union

import validators

import regex as re 

# ---------------------------------------------------------------------------- #

SEARCH_RESULTS_XPATH = r"//div[@id='main_search'][1]/div[@class='searchkekka_box'][1]"

REMOVE_NEWLINE = re.compile(r"[\n]*"),

class FindNovelMetrics:
    patterns = {
        "wordcnt" : re.compile(r"([\d,]+)(?:文字)"),
        "postcnt" : re.compile(r"(?:\(全)([\d]*)(?:部分\))"),
        "words" : r"%s[\s\D\W]{1,5}(.*)\n"
        "numbers" : r"(?:%s)[\s\D\W]{1,5}([\d,]*)",
        "dates" : re.compile(
            "(?:最終更新日)[\s\D\W]{1,5}(\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2})"
        ),
        "rank" : re.compile(r"([\p{Han}]{1,2})間pt[\s\D\W]{1,5}([\d,]*)pt")
    }

    metrics = {
        "rank" : [''],
        "dates" : [''],
        "words" : ["ジャンル", "キーワード"],
        "numbers" : ["総合ポイント", "週別ユニークユーザ", 
                    "レビュー数", "ブックマーク", "評価人数", 
                    "評価ポイント"],
    }
    
    def __init__(self, text: str) -> None:
        self.text = text

    def find(self):
        
        T = self.text 
        data: Dict[str, Union[str, int, List[str]]] = dict()
        
        data['word_cnt'] = self.patterns['wordcnt'].search(T)
        data['post_cnt'] = self.patterns['postcnt'].search(T)

        for group, names in self.metrics.items():
            if group == 'rank':
                res = self.patterns['rank'].findall(T).groups()
                
                # (period, score)
                data['rank'] = [
                    (a, b) for a, b in zip(res[::2], res[1::2])
                ]
                continue     
            
            elif group == 'dates':
                res = self.patterns['dates'].search(T).groups()[0]
                data['most_recent_update'] = datetime.strptime(
                    res, r"%Y/%m/%d %H:%M"
                )
                continue 
            
            for m in group:
                
# ---------------------------------------------------------------------------- #


class Novel(scrapy.Item):
    """Novel information"""
    title: str = scrapy.Field()
    author: str = scrapy.Field()
    genre: str = scrapy.Field()
    summary: str = scrapy.Field()
    word_cnt: int = scrapy.Field()
    post_cnt: int = scrapy.Field()
    weekly_unique_cnt: int = scrapy.Field()
    most_recent_update: datetime.date = scrapy.Field()
    bookmark_cnt: int = scrapy.Field()
    review_cnt: int = scrapy.Field()
    hyouka_cnt: int = scrapy.Field()
    hyouka_point: int = scrapy.Field()
    global_point: int = scrapy.Field()
    ncode: str = scrapy.Field()
    keywords: List[str] = scrapy.Field()


def get_search_order(order: str) -> str:
    """
    Return `yomou.syosetu` search page ordered by `order`
    
    ## Options for `order`
    `new` = by most recent update 
    `old` = by oldest update
    `weekly` = by number of weekly unique users 
    `favnovelcnt` = by number of bookmarks 
    `reviewcnt` = by number of reviews 
    `hyoka` = by total score 
    `hyokacnt` = by number of user ratings 
    `lengthdesc` = by total word count
    
    ### Points over specific periods
    `dailypoint` = per day
    `weeklypoint` = per week
    `monthlypoint` = per month
    `quarterpoint` = per quarter
    `yearlypoint` = per year 
    """
    return f"https://yomou.syosetu.com/search.php?&order_former=search&order={order}&notnizi=1&p=%d"


def format_novel_metric_string(txt: List[str]) -> str:
    out = ",".join([s.strip() for s in txt if not s.isspace()])
    return REMOVE_NEWLINE.sub('', )
    
class NovelSpider(CrawlSpider):
    name = 'novels'    
    allowed_domains = ['yomou.syosetu.com/', 
                    'ncode.syosetu.com/']
    
    rules = (
        # novel 
        Rule(LinkExtractor(allow=(r"\/(n[\d]{4}[a-z]{2})\/$",),), callback='parse'),
    )
    
    def __init__(self, max_novel_cnt: int=20, max_page_cnt: int=10,
                order: Union[str, List[str]]="favnovelcnt", 
                *args, **kwargs
        ):
        
        super().__init__(*args, **kwargs)
        
        self.max_novel_cnt = max_novel_cnt
        self.get_start_URLs(order, max_page_cnt)
    
    def get_start_URLs(self, order: str, max_page_cnt: int):
        
        first_page = get_search_order(order=order)
        
        if not validators.url(first_page):
            raise ValueError(f"{first_page} is an invalid URL.")
        
        self.start_urls = [
            first_page % d for d in range(1, max_page_cnt+1)
        ]
        
        if not validators.url(self.start_urls[0]):
            raise ValueError(f"Search page URLs are invalid. Tested\n{self.start_urls[0]}")
    
    def start_requests(self):
        return super().start_requests()
    
    def parse(self, response, **kwargs):
        
        for box in response.css("div.searchkekka_box"):
            summary = box.css("td div.ex::text").get()
            
            tbl = format_novel_metric_string(
                box.xpath("./table//text()").getall()
            )
            
            word_cnt = METRIC_PATTERNS['wordcnt'].search(tbl)
            post_cnt = METRIC_PATTERNS['postcnt'].search(tbl)
            
            for category in NOVEL_METRICS:
                
            
    def parse_novel(self):
        pass 
    