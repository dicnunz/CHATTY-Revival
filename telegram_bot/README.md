# Optional Telegram Bot

This is an optional no-dependency bot scaffold. It does not auto-DM, join groups, delete messages, trade, connect wallets, or spend money.

Human setup required:

1. Create a bot with BotFather.
2. Set the token locally, never in chat:

```bash
export CHATTY_TELEGRAM_BOT_TOKEN="..."
```

3. Run:

```bash
python3 telegram_bot/bot.py
```

Commands:

- `/contract`
- `/disclosure`
- `/rules`
- `/stats`
- `/faq`

