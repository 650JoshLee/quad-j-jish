"""Refine an initial equity table near decision thresholds, entirely offline.
Example: python tools/refine_preflop.py --base data/preflop_initial.npy --output data/preflop.npy
"""
import argparse,itertools,json,sys,time
from pathlib import Path


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--base',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--base-samples',type=int,default=65536)
 p.add_argument('--additional-samples',type=int,default=262144)
 p.add_argument('--band',type=float,default=.004)
 p.add_argument('--thresholds',type=float,nargs='+',default=[.48,.525,.56,.57,.605,.64,.675])
 args=p.parse_args()
 if args.base.resolve()==args.output.resolve():p.error('Use a separate output file to preserve the initial table.')
 if min(args.base_samples,args.additional_samples)<=0:p.error('Simulation counts must be positive.')
 import numpy as np
 import train_preflop as training
 agent=training.agent
 started=time.perf_counter()
 base=np.load(args.base,allow_pickle=False)
 if base.shape!=(376992,) or base.dtype!=np.float32:p.error('Invalid initial table.')
 hands=np.array(list(itertools.combinations(range(36),5)),dtype=np.int32)
 by_index=np.empty_like(hands)
 for h in hands:by_index[agent._index(h)]=h
 permutations=np.array(list(itertools.permutations(range(4))),dtype=np.int32)
 mapping=training.canonical_map(by_index,permutations)
 classes=np.unique(mapping)
 selected=[int(i) for i in classes if np.min(np.abs(np.asarray(args.thresholds)-float(base[i])))<args.band]
 refined=base.copy()
 for n,index in enumerate(selected):
  value=training.estimate(by_index[index],args.additional_samples,np.uint64(981237+index*21379),agent._SCORE)
  refined[index]=(args.base_samples*float(base[index])+args.additional_samples*value)/(args.base_samples+args.additional_samples)
  if n%250==0:print(f'{n}/{len(selected)} classes',flush=True)
 result=refined[mapping]
 args.output.parent.mkdir(parents=True,exist_ok=True)
 np.save(args.output,result,allow_pickle=False)
 metadata=dict(base_samples_per_class=args.base_samples,additional_samples_per_refined_class=args.additional_samples,total_samples_per_refined_class=args.base_samples+args.additional_samples,refined_classes=len(selected),total_classes=len(classes),thresholds=args.thresholds,selection_band=args.band,additional_trials=len(selected)*args.additional_samples,seed_formula='981237 + canonical_index * 21379',mean_equity=float(result.mean()),elapsed_seconds=time.perf_counter()-started)
 args.output.with_name(args.output.stem+'_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
 print(json.dumps(metadata,indent=2),flush=True)


if __name__=='__main__':main()
