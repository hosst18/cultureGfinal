from __future__ import annotations

from discord.ext import commands


class Profiles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="profile")
    async def profile(self, ctx: commands.Context) -> None:
        """Commande test pour les profils."""
        await ctx.send(f"Profil de {ctx.author.display_name} (placeholder).")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Profiles(bot))
