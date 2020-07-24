"""
Some simple unit tests for sanity checks in development
"""

from woba_evaluator import *
carpenter  = player_outcomes(572761)
carpenter.add_fg_woba(2019)
carpenter.add_fg_ab(2019)
carpenter.eval_model('../models/final_model')

def test_woba_calculator2013():
    """ Test woba calculator for Trout 2013 """
    
    woba_2013 = woba_calculator(wBB=0.690,
                                wHBP=0.722,
                                w1B=0.888,
                                w2B=1.271,
                                w3B=1.616,
                                wHR=2.101)
    calculated_woba = woba_2013.evaluate_events(bb=100,
                                                hbp=9,
                                                s=115,
                                                d=39,
                                                t=9,
                                                hr=27,
                                                ab=589,
                                                sf=8)
    actual_woba = 0.423

    assert (calculated_woba-actual_woba < 0.001)


def test_player_outcomes_init():
    """ 
    Test initalization of player_outcomes object 
    use matt carpenter 2019 as example
    """
    assert(carpenter.bb == 63)
    assert(carpenter.single == 57)
    assert(carpenter.hr == 15)
    assert(carpenter.sf == 5)
                            
def test_woba_download():
    assert(carpenter.fg_woba == 0.315)

def test_ab_download():
    assert(carpenter.fg_ab == 416)

def test_model_row():
    """
    Test model loads and is sensible
    """
    from random import randint
    # Check random evaluation add to 1
    checksum = 0
    row_to_check = randint(0,len(carpenter.df))
    for label in label_encoding:
        checksum += carpenter.df[f"{label}_prob"][row_to_check]
    
    assert( abs(checksum - 1.0) < 0.005)

def test_model_sums():
    # Check sum of all predictions add to number of rows
    checksum = 0
    for label in label_encoding:
        checksum += carpenter.df[f"{label}_prob"].sum()

    assert(abs(checksum - len(carpenter.df) < 0.05))

def test_model_woba():
    """
    Just tests that the model will load and return a value
    """
    wc = woba_calculator()
    assert(carpenter.eval_model_woba(wc) > 0)

if __name__ == "__main__":
    pass