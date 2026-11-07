"""Print hand counts: python tools/count_hands.py match-result.json"""
import argparse
import json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('result')
    args=parser.parse_args()
    data=json.loads(Path(args.result).read_text())
    if isinstance(data,list):
        for r in data:
            if 'hands_won' not in r:
                parser.error('This benchmark report predates hand counts. Rerun the benchmark.')
            print(f"{r['opponent']}: jish_4 {r['hands_won']} wins; opponent {r['hands_lost']} wins; {r['hands_tied']} ties ({r['hands']} hands)")
        return
    if data.get('kind')=='half_result':
        nets=data['nets_agent1']
    elif isinstance(data.get('logs'),dict):
        nets=[hand['nets'][seat] for half,seat in [('half1',0),('half2',1)] for hand in data['logs'][half]]
    else:
        parser.error('Individual hands were not saved. Run the judge again with --logs --json match-result.json.')
    wins=sum(n>0 for n in nets)
    losses=sum(n<0 for n in nets)
    ties=sum(n==0 for n in nets)
    print(f"Agent 1 ({data.get('agent1_name','')}): {wins} hands won")
    print(f"Agent 2 ({data.get('agent2_name','')}): {losses} hands won")
    print(f'Ties: {ties}\nTotal hands: {len(nets)}')

if __name__=='__main__':
    main()
