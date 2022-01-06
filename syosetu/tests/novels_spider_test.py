import sys 
import os 
import unittest 

import pandas as pd 

from typing import List
from ast import literal_eval

sys.path.insert(0, os.path.abspath("./syosetu/"))
import syosetu.spiders.novels_spider as nspider


# ---------------------------------------------------------------------------- #
FILE_OPTS = dict(mode='r', encoding='utf8')

def generate_true_data() -> bool:
    finder = nspider.FindNovelMetrics('')
    metrics = [] 
    for i in range(1, 11):
        
        with open(f"./syosetu/tests/data/_testtxt{i}.txt", **FILE_OPTS) as file:
            data = file.read().rstrip()
        
        finder.replace_data(data)
        finder.find()
        metrics.append(finder.data)
        
    df = pd.DataFrame.from_records(metrics)
    df.index += 1 
    
    f = "./syosetu/tests/data/trueMetrics.csv"
    df.to_csv(f)
    return os.path.isfile(f)

# ---------------------------------------------------------------------------- #

class MetricFinderTest(unittest.TestCase):
    TESTPATH = "./syosetu/tests/data/"
    
    TRUEVALS = pd.read_csv(
        TESTPATH + "/trueMetrics.csv", 
        header=0, index_col=0,
        parse_dates=['most_recent_update']
    )
    
    finder = nspider.FindNovelMetrics('')
            
    def _readFile(self, num: int) -> str:
        """Read the `num`-th .txt file containing raw metrics data"""
        
        path = self.TESTPATH + f"/_testtxt{num}.txt"
        
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Test file does not exist:\n{path}"
            )
        
        with open(path, **FILE_OPTS) as file:
            return file.read().rstrip()
        
    def assertListOfTuplesEqual(self, expected: List[tuple], actual: List[tuple]):
        
        self.assertEqual(type(expected), type(actual))
        self.assertEqual(len(expected), len(actual))  
        self.assertCountEqual(expected, actual)
        
        
    def test_metric_extraction(self):
        
        for i in range(1, 11):
            
            with self.subTest(suffix=i):
                data = self._readFile(i)
                self.finder.replace_data(data)
                self.finder.find()
                
                ref = self.TRUEVALS.iloc[i-1,:]
                
                for col, val in self.finder.data.items():
                    if isinstance(val, list):
                        actual = literal_eval(ref.loc[col])
                        self.assertListOfTuplesEqual(val, actual)
                    else:
                        self.assertEqual(ref.loc[col], val)            


if __name__ == '__main__':
    unittest.main()
