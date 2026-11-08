import sys,random,itertools,json
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import agent as a
from game import Game,make_deal,Action
from evaluator import score_five,omaha_score
rng=random.Random(1010)
for cards in itertools.combinations(range(36),5):
 key=sum((c//4)*9**i for i,c in enumerate(cards));flush=int(len({c%4 for c in cards})==1)
 assert a._FIVE[flush,key]==score_five(cards)
for i in range(500):
 cards=rng.sample(range(36),10);n=rng.randrange(3,6)
 assert a._omaha(np.array(cards[:5]),np.array(cards[5:5+n]),a._FIVE)==max(score_five(h+b) for h in itertools.combinations(cards[:5],2) for b in itertools.combinations(cards[5:5+n],3))
checked=0
for hand in range(100):
 g=Game(make_deal('tree-check',hand),hand%2)
 while not g.is_terminal:
  hero=g.to_act;obs=g.observation(hero);actors,children,kinds,spent=a._betting_tree(obs)
  original=g.contributed[:]
  def walk(node,state):
   global checked
   checked+=1
   if actors[node]<0:
    assert state.is_terminal or state.street!=obs.street
    return
   assert state.to_act==(hero if actors[node]==0 else 1-hero)
   assert {int(x) for x in state.legal_actions()}=={x for x in range(4) if children[node,x]>=0}
   for act in state.legal_actions():
    child=children[node,int(act)];s=state.clone();s.apply(act)
    assert list(spent[child])==[s.contributed[hero]-original[hero],s.contributed[1-hero]-original[1-hero]]
    walk(child,s)
  walk(0,g.clone());g.apply(rng.choice(g.legal_actions()))
# Kuhn poker: chance deals distinct J/Q/K; one-unit ante and one-unit bet.
actors=np.array([0,1,0,-1,-1,-1,1,-1,-1],np.int32)
children=np.full((9,4),-1,np.int32)
children[0,1:3]=[1,6];children[1,1:3]=[5,2];children[2,:2]=[3,4];children[6,:2]=[7,8]
pay=np.zeros((9,3,3));sign=np.sign(np.arange(3)[:,None]-np.arange(3)[None,:])
pay[3]=-1;pay[4]=2*sign;pay[5]=sign;pay[7]=1;pay[8]=2*sign
# Solver requires parent-before-child ordering. Remap DFS order.
order=[0,1,5,2,3,4,6,7,8];lookup={old:new for new,old in enumerate(order)}
children=np.array([[lookup[c] if c>=0 else -1 for c in children[n]] for n in order],np.int32)
actors=actors[order];pay=pay[order];joint=(1-np.eye(3))/6
policy=a._solve(actors,children,pay,joint,10000)
def value(node,x,y):
 if actors[node]<0:return pay[node,x,y]
 t=x if actors[node]==0 else y
 return sum(policy[node,t,act]*value(c,x,y) for act,c in enumerate(children[node]) if c>=0)
v=sum(joint[x,y]*value(0,x,y) for x in range(3) for y in range(3))
assert abs(v+1/18)<.003,v
# Best response chooses one action per private type/public history, not per opponent card.
def br(player,node,reach):
 if actors[node]<0:
  u=pay[node] if player==0 else -pay[node]
  return (joint*u*reach[None,:]).sum(axis=1) if player==0 else (joint*u*reach[:,None]).sum(axis=0)
 actor=actors[node];vals=[]
 for act,c in enumerate(children[node]):
  if c>=0:vals.append(br(player,c,reach if actor==player else reach*policy[node,:,act]))
 return np.max(vals,axis=0) if actor==player else np.sum(vals,axis=0)
gap=br(0,0,np.ones(3)).sum()+br(1,0,np.ones(3)).sum()
assert gap<.015,gap
print(json.dumps(dict(five_card_checks=376992,omaha_checks=500,tree_nodes=checked,kuhn_value=v,kuhn_nash_gap=gap)),flush=True)
