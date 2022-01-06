# coding=utf8

# Copyright (c) 2022 Delbert Yip
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import scrapy 
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule 
from scrapy.linkextractors import LinkExtractor

from datetime import datetime 
from typing import Callable, List, Dict, Union, Tuple, Any

import logging
from scrapy.utils.trackref import NoneType 
import validators

import regex as re 

# ---------------------------------------------------------------------------- #

SEARCH_RESULTS_XPATH = r"//div[@id='main_search'][1]/div[@class='searchkekka_box'][1]"

JAPANESE_SCRIPT_REGEX = "\p{Han}\p{Katakana}\p{Hiragana}"

REMOVE_PUNCT_REGEX = re.compile(
    f"[^{JAPANESE_SCRIPT_REGEX}\s\n\w\d]*"
)
    
# ---------------------------------------------------------------------------- #

def to_int(number: str) -> int:
    return int( re.sub("\D*", '', number) )

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
    hyouka_pnt: int = scrapy.Field()
    global_pnt: int = scrapy.Field()
    ncode: str = scrapy.Field()
    keywords: List[str] = scrapy.Field()

class FindNovelMetrics:
    patterns = {
        "word_cnt" : re.compile(r"([\d,]+)(?:文字)"),
        "post_cnt" : re.compile(r"(?:\(全)([\d]*)(?:部分\))"),
        "words" : f"%s[\s\D\W](.*)(?:%s)",
        "numbers" : r"%s[\s\D\W]{1,5}([\d,]*)",
        "dates" : re.compile(
            r"(?:最終更新日)[\s\D\W](\d{4}\/\d{2}\/\d{2}\s\d{2}:\d{2})"
        ),
        "rank" : re.compile(
            r"([\p{Han}]{1,2})間pt[\s\D\W]{1,5}([\d,]*)pt"
        )
    }

    metrics: Dict[str, Union[list, List[tuple]]] = {
        "rank" : [],
        "dates" : [],
        "words" : [(("ジャンル", "キーワード"), "genre"), 
                    (("キーワード", "最終更新日"), "keywords")],
        "numbers" : [("総合ポイント", "global_pnt"), 
                    ("週別ユニークユーザ", "weekly_unique_cnt"), 
                    ("レビュー数", "review_cnt"), 
                    ("ブックマーク", "bookmark_cnt"), 
                    ("評価人数", "hyouka_cnt"),
                    ("評価ポイント", "hyouka_pnt")],
    }
    
    ERR_MSG = "Could not extract data for metric < {m} >\n{e}"
    
    data: Dict[str, Union[str, int, List[str]]] = dict()
    
    def __init__(self, text: str) -> None:
        self.text = text
        # self.logger = logger 

    @staticmethod
    def _filterSearchByType(
        search: List[str], serializer=str, *args
    ) -> Union[int, str, NoneType]:
        """Discard regex matches that can't be serialized"""
        
        for s in search:
            try: 
                return serializer(s, *args)
            except ValueError as e:
                logging.error(e)
        
        logging.warning(f"Failed to serialize:\n{search}")
        return None 
    
    def _findContextSpecific(
        self, data: Dict[str, Any], group: str, names: List[Any]
    ) -> Dict[str, Any]:
        
        """Context-specific regex patterns in 'word' and 'numbers'"""
        
        serializer = str if (group == 'words') else to_int 
        
        for jp, eng in names:
            
            try:
                res = re.findall(self.patterns[group] % jp, self.text)
                res = self._filterSearchByType(res, serializer=serializer)
                data[eng] = res
                    
            except AttributeError as e:
        
                logging.error(self.ERR_MSG.format(
                    m=f"{group}/{eng}", e=e))
        
                data[eng] = None
        
        return data 
    
    def find(self) -> None:
        
        T = self.text 
        data = self.data 
        
        for name in ['word_cnt', 'post_cnt']:
            num = self.patterns[name].search(T).group(1)
            data[name] = to_int(num)

        for group, names in self.metrics.items():
            
            if group not in self.patterns: 
                logging.error(
                    KeyError(f"No regex pattern matching {group}.")
                )
                continue
            
            # pre-compiled regex patterns 
            try:
                if group == 'rank':
                    # List[ (period, score) ]
                    res = self.patterns['rank'].findall(T)
                    
                    if res:
                        for i, r in enumerate(res):
                            res[i] = (r[0], to_int(r[1]))
                    
                    data['rank'] = res 
                    continue 
                
                elif group == 'dates':
                    res = self.patterns['dates'].search(T).group(1)
                    data['most_recent_update'] = datetime.strptime(
                        res, r"%Y/%m/%d %H:%M"
                    )
                    continue 
                
            except AttributeError as e:
                logging.error(self.ERR_MSG.format(m=group, e=e))
                data[group] = None
            
            # 'words' and 'numbers' 
            data = self._findContextSpecific(data, group, names)
                            
        return 
    
    def replace_data(self, new_text: str) -> None:
        self.text = new_text 
        self.data = dict()
    
    def create_novel_item(self) -> Novel:
        return Novel(**self.data)
    
    def __repr__(self) -> str:
        output = [f"{name} \t {val}" for name, val in self.data.items()]
        return "\n".join(output)

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
    out = re.sub('[\n\s]*', '', ''.join(txt))
    return out 
    
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
    
    @staticmethod
    def _format_tbl_str(boxes: List[str]) -> str:
        """Format table strings containng novel metrics"""
        for i, box in enumerate(boxes):
            box = ' '.join(
                (''.join(box)).split()
            )
            boxes[i] = box 
        return boxes 
            
    def parse(self, response, **kwargs):
        
        for box in response.css("div.searchkekka_box"):
            summary = box.css("td div.ex::text").get()
            
            tbl = format_novel_metric_string(
                box.xpath("./table//text()").getall()
            )
            
    def parse_novel(self):
        pass 
