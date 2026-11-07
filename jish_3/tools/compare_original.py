"""Real HTTP duplicate matches against a reference agent; restart each half.
Example: python tools/compare_original.py --reference ../quad-j/agent.py
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from validate_matches import launch
ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reference',type=Path,default=ROOT.parent/'quad-j/agent.py')
    parser.add_argument('--seeds',nargs='+',default=['http-independent-401','http-independent-402'])
    parser.add_argument('--output',type=Path,default=ROOT/'validation/http-original')
    args=parser.parse_args()
    reference=args.reference.resolve()
    if not reference.is_file():
        parser.error(f'Reference agent not found: {reference}')
    args.output.mkdir(parents=True,exist_ok=True)
    startup=[]
    for seed in args.seeds:
        for half in (1,2):
            procs=[]
            with (args.output/f'{seed}-half{half}-servers.log').open('w') as log:
                try:
                    bot,elapsed=launch(ROOT/'agent.py',5038,log)
                    procs.append(bot)
                    startup.append(dict(seed=seed,half=half,seconds=elapsed))
                    rival,_=launch(reference,5039,log)
                    procs.append(rival)
                    result=subprocess.run([sys.executable,str(ROOT/'judge_engine.py'),'--agent1','5038','--agent2','5039','--half',str(half),'--seed',seed,'--deals','1000','--json',str((args.output/f'{seed}-half{half}.json').resolve()),'--logs'],cwd=ROOT,capture_output=True,text=True,timeout=180,check=True)
                    (args.output/f'{seed}-half{half}.txt').write_text(result.stdout)
                finally:
                    for p in procs: p.terminate()
                    for p in procs: p.wait(timeout=10)
        result=subprocess.run([sys.executable,str(ROOT/'judge_engine.py'),'combine',str((args.output/f'{seed}-half1.json').resolve()),str((args.output/f'{seed}-half2.json').resolve())],capture_output=True,text=True,check=True,timeout=30)
        (args.output/f'{seed}-combined.txt').write_text(result.stdout)
        print(result.stdout,flush=True)
    (args.output/'startup.json').write_text(json.dumps(startup,indent=2)+'\n')


if __name__=='__main__':
    main()
