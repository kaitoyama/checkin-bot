"""Discord UI components for check-in flow.

Uses discord.py component v2 (views & buttons).
"""
from __future__ import annotations

import logging
from typing import Optional
from datetime import datetime, timezone

import discord
from discord import ui

from sheets import SheetsWriter

logger = logging.getLogger("checkin-bot.components")


class ConfirmView(ui.View):
    """View shown after a user presses the initial "参加" button.

    Contains a confirmation button which finalizes the check-in and
    records it via SheetsWriter.
    """

    def __init__(self, author_id: int, sheets: SheetsWriter, *, timeout: float = 120.0):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.sheets = sheets

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only allow the original clicker to confirm
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("この操作はあなたには行えません。", ephemeral=True)
            return False
        return True

    @ui.button(label="参加を確定する", style=discord.ButtonStyle.success, custom_id="confirm_checkin")
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        """Handle final confirmation from the participant."""
        # Record timestamp in JST (UTC+9)
        from datetime import timedelta
        jst = timezone(timedelta(hours=9))
        ts = datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")
        username = interaction.user.name

        # Append to spreadsheet (blocking call expected to be run in executor by caller)
        try:
            self.sheets.append_checkin(ts, username)
        except Exception as exc:  # pragma: no cover - external I/O
            logger.exception("Failed to append checkin: %s", exc)
            await interaction.response.send_message("受付処理中にエラーが発生しました。スタッフに連絡してください。", ephemeral=True)
            return

        # Edit the original message to show completion, removing the button
        await interaction.response.edit_message(content="参加受付が完了しました。", view=None)



class InitialView(ui.View):
    """Main view containing the initial participation button. Persistent view."""

    def __init__(self, sheets: SheetsWriter):
        # persistent=True で永続化
        super().__init__(timeout=None)
        self.sheets = sheets

    @ui.button(label="参加する", style=discord.ButtonStyle.primary, custom_id="start_checkin")
    async def start(self, interaction: discord.Interaction, button: ui.Button):
        """When clicked, send an ephemeral confirmation dialog to the user."""
        view = ConfirmView(interaction.user.id, self.sheets)
        await interaction.response.send_message("受付スタッフの指示がなければ押さないでください。\n参加する場合は下のボタンで確定してください。", view=view, ephemeral=True)
