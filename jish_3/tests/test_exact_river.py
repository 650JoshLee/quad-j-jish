"""Independent completeness, showdown, ranking, and budget checks."""
from dataclasses import replace
import math
import numpy as np
import agent
from evaluator import cards_from_str,omaha_score
from game import AgentConfig,Game,Street,make_deal


def test_all_river_hands_are_distinct_legal_and_complete():
    hero=cards_from_str('Ah Kh 6c 7d 8s');board=cards_from_str('Qh Jh 9c 6d 9s')
    hands,scores,outcomes=agent._river_all(np.array(hero,dtype=np.int32),np.array(board,dtype=np.int32),agent._SCORE,agent._PREFLOP)
    assert len(hands)==math.comb(26,5)==65780
    assert np.all(np.diff(hands,axis=1)>0)
    assert not np.isin(hands,hero+board).any()
    keys=sum(agent._BINOM[hands[:,i],i+1] for i in range(5))
    assert len(np.unique(keys))==65780
    mine=omaha_score(hero,board)
    for i in np.random.default_rng(731).choice(len(hands),100,replace=False):
        theirs=omaha_score(hands[i].tolist(),board)
        assert scores[i,3]==theirs
        assert outcomes[i]==(1. if mine>theirs else .5 if mine==theirs else 0.)


def test_compact_percentiles_preserve_exact_ties_and_order():
    rng=np.random.default_rng(632)
    values=agent._PREFLOP[rng.integers(0,len(agent._PREFLOP),20000)].astype(float)
    np.testing.assert_allclose(agent._compact_percentile(values),agent._percentile(values),rtol=0,atol=1e-15)
    values=agent._score_values[rng.integers(0,len(agent._score_values),20000)].astype(float)
    np.testing.assert_allclose(agent._compact_percentile(values),agent._percentile(values),rtol=0,atol=1e-15)


def test_expensive_enumeration_is_replaced_when_compute_allowance_is_low():
    memory={};agent.new_half(AgentConfig(),memory)
    memory['compute_seconds']=1000.
    obs=Game(make_deal('budget',0),0).observation(0)
    obs=replace(obs,street=Street.RIVER,board=(0,1,2,3,4),hole_cards=(5,6,7,8,9))
    cache=agent._simulation(obs,memory)
    assert cache['mode']=='sampled_budget'
    assert len(cache['opponents'])==96
    assert memory['simulation_modes']['sampled_budget']==1
