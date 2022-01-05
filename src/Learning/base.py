"""Commonly used functions and methods"""
import pandas as pd 
import numpy as np 
import sys 
import os 

class TestRuntimeError(Exception):
    def __init__(self, func_name, test_input) -> None:
        super().__init__(f"Function {func_name} failed to run on input:\n{test_input}")

class TestAssertionError(AssertionError):
    def __init__(self, func_name: str, test_input, test_output, true_output) -> None:
        super().__init__(
            f"\nTest of {func_name} failed with input:\n{test_input}.\n\
            Output was{test_output}.\nExpected output was {true_output}"
        )

class CommonTest:
    def __init__(self, func, test_inputs: list, true_outputs: list, suppress_printing=True) -> None:
        
        if suppress_printing:
            sys.stdout = open(os.devnull, 'w')
            
        try:
            self._applyTest(func, test_inputs, true_outputs)
        except Exception as e:
            print(e)
        
        if suppress_printing:
            sys.stdout = sys.__stdout__
    
    def _applyTest(self, func, test_inputs: list, true_outputs: list):
        fname = func.__name__
    
        for test_input, true_output in zip(test_inputs, true_outputs):
            
            try:
                test_output = func(test_input)
            except Exception as e:
                print(e)
                TestRuntimeError(fname, test_input)
            
            if isinstance(true_output, pd.Series) or isinstance(true_output, pd.DataFrame):
                test_output = test_output.loc[true_output.index, :]
                
            compared = (test_output == true_output)
            
            try:
                if isinstance(true_output, pd.Series):
                        assert compared.all()
                elif isinstance(true_output, pd.DataFrame):
                        assert compared.all().all()
                elif isinstance(true_output, np.ndarray):
                    assert np.all(compared)
                else:
                    assert compared 
                    
            except AssertionError:
                TestAssertionError(fname, test_input, test_output, true_output)
                
        return True 

