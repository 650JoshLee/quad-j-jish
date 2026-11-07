import os,sys,itertools,time,json
from pathlib import Path
os.environ['JISH5_TRAIN']='1'
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import agent as a
import numpy as np
from numba import njit
@njit
def canonical(hands,perms):
 result=np.empty(len(hands),np.int32)
 for i in range(len(hands)):
  value=376992
  for perm in perms:
   h=np.empty(5,np.int32)
   for j in range(5):h[j]=(hands[i,j]//4)*4+perm[hands[i,j]%4]
   value=min(value,a.hand_id(h))
  result[i]=value
 return result
start=time.perf_counter()
hands=np.array(list(itertools.combinations(range(36),5)),np.int32)
ordered=np.empty_like(hands)
for h in hands:ordered[a.hand_id(h)]=h
mapping=canonical(ordered,np.array(list(itertools.permutations(range(4))),np.int32))
classes=np.unique(mapping);values=np.zeros(376992,np.float32)
samples=8192
print(f'{len(classes)} classes, {samples} independent trials each',flush=True)
for i,key in enumerate(classes):
 values[key]=a.equity_trials(ordered[key],samples,np.uint64(20261107+int(key)*982451653),a._LOOKUP)
 if i%1000==0:print(i,round(time.perf_counter()-start,1),flush=True)
 if i%2000==0:np.save(ROOT/'data/training-checkpoint.npy',values)
result=values[mapping];np.save(ROOT/'data/opening_equity.npy',result)
(ROOT/'data/training.json').write_text(json.dumps(dict(classes=len(classes),samples_per_class=samples,total_trials=len(classes)*samples,seed_formula='20261107 + canonical_index * 982451653',elapsed_seconds=time.perf_counter()-start,mean=float(result.mean()),min=float(result.min()),max=float(result.max()),method='Fresh uniform legal deals, independent prime-product evaluator, suit-isomorphism expansion; no prior bot data reused'),indent=2))
print('TRAINING COMPLETE',flush=True)
