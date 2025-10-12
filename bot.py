"""Entrypoint for the check-in Discord bot.

Provides a `/set` slash command that posts the public participation message
with a button that starts the ephemeral confirmation flow.
"""
from __future__ import annotations

import os
import logging
import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from components import InitialView
from sheets import SheetsWriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("checkin-bot")

INTENTS = discord.Intents.default()


class CheckinBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=INTENTS, application_id=os.getenv("APPLICATION_ID"))
        self.sheets = SheetsWriter()

    async def setup_hook(self) -> None:
        # Register persistent views so they work after bot restart
        self.add_view(InitialView(self.sheets))
        # Sync commands at startup
        await self.tree.sync()


bot = CheckinBot()


@bot.tree.command(name="set", description="このチャンネルに参加ボタンを設置します")
@app_commands.guild_only()
async def set_command(interaction: discord.Interaction):
    """Post the public participation message into the current channel."""
    view = InitialView(bot.sheets)
    # Send as the command response so it appears in the channel (not ephemeral)
    await interaction.response.send_message("イベントへの参加はこちらから!", view=view)
    logger.info("Posted participation message in channel %s by user %s", interaction.channel_id, interaction.user.id)


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("Missing DISCORD_TOKEN environment variable")
        raise SystemExit("DISCORD_TOKEN is required")
    bot.run(token)


if __name__ == "__main__":
    main()
