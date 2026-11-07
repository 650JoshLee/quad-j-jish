"""Run the real judge with a fresh bot process for each half.
Use: python tools/validate_matches.py --output validation
All subprocesses started here are stopped on exit.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def launch(file, port, log):
    env = dict(os.environ, PORT=str(port), PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', NUMBA_NUM_THREADS='1')
    proc = subprocess.Popen([sys.executable, str(file)], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    start = time.perf_counter()
    try:
        while time.perf_counter() - start < 15:
            if proc.poll() is not None:
                raise RuntimeError(f'{file} exited with {proc.returncode}')
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=0.25) as response:
                    if response.status == 200:
                        return proc, time.perf_counter() - start
            except OSError:
                time.sleep(0.05)
        raise RuntimeError(f'{file} startup exceeded 15 seconds')
    except BaseException:
        proc.terminate()
        proc.wait(timeout=10)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='validation')
    parser.add_argument('--deals', type=int, default=1000)
    parser.add_argument('--seed', default='held-out-http-47')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    startup = []
    for name in ('random', 'calling_station', 'always_pot', 'always_half'):
        for half in (1, 2):
            processes = []
            with (output / f'{name}-half{half}-server.log').open('w') as log:
                try:
                    bot, seconds = launch(ROOT / 'agent.py', 5038, log)
                    processes.append(bot)
                    startup.append(dict(opponent=name, half=half, bot_startup_seconds=seconds))
                    rival, _ = launch(ROOT / 'baseline-bots' / f'baseline_{name}.py', 5039, log)
                    processes.append(rival)
                    cmd = [sys.executable, 'judge_engine.py', '--agent1', '5038', '--agent2', '5039', '--half', str(half), '--deals', str(args.deals), '--seed', args.seed, '--json', str(output / f'{name}-half{half}.json')]
                    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=180, check=True)
                    (output / f'{name}-half{half}.txt').write_text(result.stdout)
                finally:
                    for process in processes:
                        process.terminate()
                    for process in processes:
                        process.wait(timeout=10)
        cmd = [sys.executable, 'judge_engine.py', 'combine', str(output / f'{name}-half1.json'), str(output / f'{name}-half2.json')]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=30, check=True)
        (output / f'{name}-combined.txt').write_text(result.stdout)
        print(result.stdout, flush=True)
    (output / 'startup.json').write_text(json.dumps(startup, indent=2)+'\n')


if __name__ == '__main__':
    main()
