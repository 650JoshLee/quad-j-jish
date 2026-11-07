"""Check shared board evaluation against the independent referee evaluator."""
from itertools import combinations
import numpy as np
import agent
from evaluator import cards_from_str,omaha_score,score_five


def test_pair_board_scores_use_exactly_two_hole_cards():
    hole=cards_from_str('Ah Kh 6c 7d 8s')
    board=cards_from_str('Qh Jh Th 9c 6d')
    for length in (3,4,5):
        pair=agent._pair_board(np.array(board,dtype=np.int32),length,agent._SCORE)
        for a,b in combinations(hole,2):
            expected=max(score_five([a,b,*triple]) for triple in combinations(board[:length],3))
            assert pair[a,b]==expected
        expected=max(score_five([*h,*b]) for h in combinations(hole,2) for b in combinations(board[:length],3))
        assert agent._from_pair_board(np.array(hole,dtype=np.int32),pair)==expected


def test_turn_equity_enumerates_every_legal_river_for_each_sampled_hand():
    hero=cards_from_str('Ah Kh 6c 7d 8s');board=cards_from_str('Qh Jh 9c 6d')
    other,scores,outcomes=agent._shared_sample(np.array(hero,dtype=np.int32),np.array(board,dtype=np.int32),10,0,np.uint64(177),agent._SCORE,agent._PREFLOP)
    for hand,outcome in zip(other,outcomes):
        hole=hand.tolist();remaining=set(range(36))-set(hero+board+hole)
        assert len(remaining)==22
        wins=0.
        for river in remaining:
            mine=omaha_score(hero,board+[river]);theirs=omaha_score(hole,board+[river])
            wins+=1 if mine>theirs else .5 if mine==theirs else 0
        assert abs(outcome-wins/22)<1e-12


def test_flop_equity_enumerates_all_253_legal_runouts_per_sampled_hand():
    hero=cards_from_str('Ah Kh 6c 7d 8s');board=cards_from_str('Qh Jh 9c')
    other,scores,outcomes=agent._shared_sample(np.array(hero,dtype=np.int32),np.array(board,dtype=np.int32),3,0,np.uint64(191),agent._SCORE,agent._PREFLOP)
    for hand,outcome in zip(other,outcomes):
        hole=hand.tolist();remaining=set(range(36))-set(hero+board+hole)
        wins=0.;count=0
        for turn,river in combinations(remaining,2):
            mine=omaha_score(hero,board+[turn,river]);theirs=omaha_score(hole,board+[turn,river])
            wins+=1 if mine>theirs else .5 if mine==theirs else 0
            count+=1
        assert count==253
        assert abs(outcome-wins/count)<1e-12


def test_river_samples_are_legal_and_outcomes_match_referee():
    hero=cards_from_str('Ah Kh 6c 7d 8s');board=cards_from_str('Qh Jh 9c 6d 9s')
    other,scores,outcomes=agent._shared_sample(np.array(hero,dtype=np.int32),np.array(board,dtype=np.int32),100,0,np.uint64(199),agent._SCORE,agent._PREFLOP)
    mine=omaha_score(hero,board)
    for hand,score,outcome in zip(other,scores,outcomes):
        hole=hand.tolist()
        assert len(set(hole))==5 and not set(hole)&set(hero+board)
        theirs=omaha_score(hole,board)
        assert score[3]==theirs
        assert outcome==(1 if mine>theirs else .5 if mine==theirs else 0)
