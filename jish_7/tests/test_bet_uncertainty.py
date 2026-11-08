import math
import numpy as np
import agent


def test_certain_identical_payoffs_have_zero_increment_uncertainty():
    weights=np.full(8,1/8);outcomes=np.full(8,.5)
    assert agent._increment_uncertainty(weights,outcomes,np.ones(8),10,0,5,5)==0


def test_uncertainty_preserves_bet_check_covariance():
    # A 50/50 win/loss sample gives incremental payoffs -5 and +5.
    # The SE is sqrt((.5*-5)^2 + (.5*5)^2), not the much larger
    # standalone variance of the bet's total pot payoff.
    actual=agent._increment_uncertainty(np.array([.5,.5]),np.array([0.,1.]),np.ones(2),10,0,5,5)
    assert math.isclose(actual,math.sqrt(12.5))


def test_more_independent_samples_reduce_increment_uncertainty():
    small=agent._increment_uncertainty(np.full(2,.5),np.array([0.,1.]),np.ones(2),10,0,5,5)
    large=agent._increment_uncertainty(np.full(8,1/8),np.array([0.,1.]*4),np.ones(8),10,0,5,5)
    assert math.isclose(large,small/2)
