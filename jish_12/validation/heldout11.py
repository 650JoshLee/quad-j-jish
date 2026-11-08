from game import Action

class HeldOut:
    def __init__(self,style):self.style=style
    def new_half(self,config,memory):memory.clear()
    def on_hand_end(self,result,memory):pass
    def choose_action(self,obs,memory):
        if not obs.board:return Action.CHECK_CALL
        if self.style=='bluff_then_fold':
            if obs.to_call:return Action.FOLD
            return Action.RAISE_POT if Action.RAISE_POT in obs.legal_actions else Action.CHECK_CALL
        large=False
        if obs.to_call:
            for e in reversed(obs.action_history):
                if not e.is_me and e.street==obs.street and e.action in (Action.RAISE_HALF,Action.RAISE_POT):
                    before_bet=e.street_total-e.amount
                    before_pot=obs.pot-e.amount
                    before_call=max(0,obs.my_bet-before_bet)
                    large=(e.street_total-obs.my_bet)/max(1,before_pot+before_call)>=.75
                    break
            if self.style=='size_folder' and large:return Action.FOLD
            if self.style=='small_reraiser' and not large and Action.RAISE_POT in obs.legal_actions:return Action.RAISE_POT
        return Action.CHECK_CALL
