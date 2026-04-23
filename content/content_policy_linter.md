# Content Policy Linter Notes

The script at `tools/content_linter.py` scans publishable drafts for high-risk phrasing and missing X disclosures.

## Banned / High-Risk Examples

- buy now
- guaranteed
- risk free
- 100x
- moon soon
- send it
- pump
- ape in
- easy money
- next Doge
- insider
- listing soon unless verified and phrased neutrally
- burn coming
- buyback
- lock supply
- coordinated
- raid
- raid this
- spam
- no risk
- financial advice unless in the phrase "not financial advice" or "no financial advice"
- official ChatGPT
- official OpenAI

## Safer Alternatives

- meme/community experiment
- highly volatile
- can go to zero
- not affiliated
- creator disclosure
- do your own research
- public transparency log updated
- no promises, no guarantees

## Command

```bash
python3 tools/content_linter.py
```

