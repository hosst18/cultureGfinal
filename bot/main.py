from __future__ import annotations

import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Charge le .env (DISCORD_TOKEN, etc.)
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # nécessaire pour lire les réponses au quiz

log = logging.getLogger("bot")
logging.basicConfig(
    level=logging.INFO,
    format="[{asctime}] [{levelname:<8}] {name}: {message}",
    style="{",
)


class CultureGBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=os.getenv("APPLICATION_ID", None),
        )

    async def setup_hook(self) -> None:
        # Charge les Cogs
        await self.load_extension("bot.cogs.quiz")
        # Si ton profiles.py est déjà fait :
        try:
            await self.load_extension("bot.cogs.profiles")
        except Exception as exc:  # pragma: no cover
            log.warning("Impossible de charger bot.cogs.profiles: %r", exc)

        # Sync des commandes slash
        await self.tree.sync()
        log.info("Commandes slash synchronisées.")

    async def on_ready(self) -> None:
        log.info(f"Connecté en tant que {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Game(name="/quiz pour jouer 🎮"),
            status=discord.Status.online,
        )


def main() -> None:
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN manquant dans le .env")
    bot = CultureGBot()
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
