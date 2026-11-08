# Public jish_4 Docker image — Team A complete

Image: `ghcr.io/650joshlee/quad-j-jish:jish_4`

The image is published and anonymous registry access was verified. It includes the bot and its required preflop data. Docker selects the native Linux amd64 or Linux arm64 build automatically, supporting Intel/AMD computers and Apple Silicon through Docker Desktop.

Both architecture builds passed the official build and restricted smoke check: one CPU, 4 GB RAM, no network during the smoke test, read-only root, limited /tmp, and official startup/action limits. [Publishing workflow](https://github.com/650JoshLee/quad-j-jish/actions/runs/42458999699).

## Send these commands to your friend

They need Docker running. Pull your image:

```sh
docker pull ghcr.io/650joshlee/quad-j-jish:jish_4
```

Run your bot on their computer's port 5009:

```sh
docker run --rm --name jish4-match --cpus 1 --memory 4g -p 127.0.0.1:5009:5008 ghcr.io/650joshlee/quad-j-jish:jish_4
```

Keep that terminal open. In a separate terminal, they run their own bot on port 5008. In a third terminal, from the official bundle folder:

```sh
python judge_engine.py --agent1 5008 --agent2 5009 --deals 1000 --seed friends-container-20261108-59317 --json friends-container-result.json
```

Agent 1 is their bot; agent 2 is your jish_4. The match covers 2,000 hands. If their own bot enables authentication, set AGENT1_TOKEN for the judge. The container command above does not enable a token on jish_4.

To repeat, stop both bots with Control+C, then rerun both startup commands before starting another judge match with a fresh seed. `--rm` removes the stopped practice container; it does not remove the downloaded image.

## Pin this exact published version

Use this tag instead of `:jish_4` if you want the publication tied to its source commit:

```text
ghcr.io/650joshlee/quad-j-jish:jish_4-fc4fd7e5ae833f15ad9e1fdb9ac01816b053ba5e
```

The published image contains the unchanged jish_4 strategy. The repository default remains jish_4. Full publication metadata, platform manifest, anonymous-access check and CI outcomes are saved alongside this guide. Container smoke verification is separate from the full local tournament-strength tests.
