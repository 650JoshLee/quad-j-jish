import os,sys,json,time,itertools
from pathlib import Path
os.environ['RESEARCH_TRAIN']='1'
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import agent as policy
import numpy as np
start=time.perf_counter();hands=policy._HANDS
canonical=policy._MASKS.copy()
for relabel in itertools.permutations(range(4)):
 suits=np.array(relabel,np.int32)
 transformed=(hands//4)*4+suits[hands%4]
 masks=np.left_shift(np.uint64(1),transformed.astype(np.uint64)).sum(axis=1)
 canonical=np.minimum(canonical,masks)
keys,inverse=np.unique(canonical,return_inverse=True)
values=np.empty(len(keys),np.float32);trials=8192
print(len(keys),'suit classes;',trials,'fresh trials/class',flush=True)
for i,key in enumerate(keys):
 h=hands[np.searchsorted(policy._MASKS,key)]
 values[i]=policy._opening_trials(h,trials,int((int(key)*1009+611071)%2147483647),policy._GRID)
 if i%1000==0:print(i,round(time.perf_counter()-start,1),'seconds',flush=True)
result=values[inverse]
np.save(ROOT/'data/research_opening.npy',result,allow_pickle=False)
(ROOT/'data/generation.json').write_text(json.dumps(dict(source='Fresh simulations from the official evaluator and game rules only',suit_classes=len(keys),trials_per_class=trials,total_trials=len(keys)*trials,seed_formula='(canonical_card_mask * 1009 + 611071) modulo 2147483647',mean=float(result.mean()),min=float(result.min()),max=float(result.max()),elapsed_seconds=time.perf_counter()-start),indent=2)+'\n')
print('FRESH TRAINING COMPLETE',flush=True)
