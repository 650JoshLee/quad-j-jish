"""Start two bot files and play a duplicate match with fresh processes each half."""
import argparse,json,subprocess,sys
from pathlib import Path
from validate_matches import launch
ROOT=Path(__file__).resolve().parents[1]


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--agent1',type=Path,default=ROOT/'agent.py')
 p.add_argument('--agent2',type=Path,required=True)
 p.add_argument('--seed',default='new2-http-1')
 p.add_argument('--deals',type=int,default=1000)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--port1',type=int,default=5058)
 p.add_argument('--port2',type=int,default=5059)
 args=p.parse_args()
 paths=[args.agent1.resolve(),args.agent2.resolve()]
 for path in paths:
  if not path.is_file():p.error(f'Agent not found: {path}')
 out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
 startup=[]
 for half in [1,2]:
  processes=[]
  with (out/f'half{half}-servers.log').open('w') as log:
   try:
    for number,(path,port) in enumerate(zip(paths,[args.port1,args.port2]),1):
     proc,seconds=launch(path,port,log);processes.append(proc)
     startup.append(dict(agent=number,path=str(path),half=half,seconds=seconds))
    command=[sys.executable,str(ROOT/'judge_engine.py'),'--agent1',str(args.port1),'--agent2',str(args.port2),'--half',str(half),'--deals',str(args.deals),'--seed',args.seed,'--logs','--json',str(out/f'half{half}.json')]
    result=subprocess.run(command,capture_output=True,text=True,check=True,timeout=180)
    (out/f'half{half}.txt').write_text(result.stdout)
   finally:
    for proc in processes:proc.terminate()
    for proc in processes:proc.wait(timeout=10)
 result=subprocess.run([sys.executable,str(ROOT/'judge_engine.py'),'combine',str(out/'half1.json'),str(out/'half2.json')],capture_output=True,text=True,check=True)
 (out/'result.txt').write_text(result.stdout)
 (out/'startup.json').write_text(json.dumps(startup,indent=2)+'\n')
 print(result.stdout,flush=True)


if __name__=='__main__':main()
