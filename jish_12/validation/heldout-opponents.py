from game import Action
from heldout11 import HeldOut as OldHeldOut
class HeldOut:
 def __init__(self,style):self.style=style;self.old=OldHeldOut(style)
 def new_half(self,config,memory):memory.clear()
 def on_hand_end(self,result,memory):pass
 def choose_action(self,obs,memory):
  if self.style in ['size_folder','small_reraiser','bluff_then_fold']:return self.old.choose_action(obs,memory)
  if self.style=='fast_switch':
   attack=(obs.hand_index//20)%2==1
   return Action.RAISE_POT if attack and Action.RAISE_POT in obs.legal_actions else Action.CHECK_CALL
  if self.style=='late_trap':
   if not obs.board:return Action.CHECK_CALL
   # Build a fold-heavy history, then switch to relentless re-raises.
   if obs.hand_index<200:
    if obs.to_call:return Action.FOLD
    return Action.RAISE_HALF if Action.RAISE_HALF in obs.legal_actions else Action.CHECK_CALL
   return Action.RAISE_POT if Action.RAISE_POT in obs.legal_actions else Action.CHECK_CALL
  if self.style=='alternating_sizes':
   if not obs.board:return Action.CHECK_CALL
   # Switch which size is attacked rather than folded every 75 hands.
   other_raises=[e for e in obs.action_history if not e.is_me and e.street==obs.street and e.action in (Action.RAISE_HALF,Action.RAISE_POT)]
   if obs.to_call and other_raises:
    large=other_raises[-1].action==Action.RAISE_POT
    attack=large==((obs.hand_index//75)%2==1)
    if not attack:return Action.FOLD
    if Action.RAISE_POT in obs.legal_actions:return Action.RAISE_POT
   return Action.CHECK_CALL
  raise ValueError(self.style)
