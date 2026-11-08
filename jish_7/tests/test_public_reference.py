import numpy as np
import agent


def test_public_reference_samples_are_legal_and_match_the_evaluator():
    board=np.array([24,29,34,3,9],np.int32)
    samples,values=agent._board_reference(board,256,np.uint64(717),agent._SCORE)
    for h,v in zip(samples,values):
        assert len(set(h))==5 and not set(h)&set(board)
        assert v==agent._fast_score(h,board,agent._SCORE)
    # The reference is public-board-only: an otherwise legal private card
    # remains in the reference population instead of being silently removed.
    assert np.any(samples==0)


def test_public_board_reference_is_repeatable_without_private_information():
    board=np.array([24,29,34],np.int32)
    a,v=agent._board_reference(board,128,np.uint64(717),agent._SCORE)
    b,w=agent._board_reference(board,128,np.uint64(717),agent._SCORE)
    assert np.array_equal(a,b) and np.array_equal(v,w)
