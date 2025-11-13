from __future__ import annotations

import random
from typing import List, Optional

import discord
from discord import Embed, Interaction, app_commands
from discord.ext import commands

from bot.core.questions_store import get_categories, load_questions

DIFFICULTIES = ["facile", "moyen", "difficile"]


class Quiz(commands.Cog):
    """Cog de quiz de culture générale."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #
    # Autocomplete sur la catégorie
    #
    @app_commands.autocomplete(name="category")
    async def category_autocomplete(
        self,
        interaction: Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        cats = get_categories()
        if current:
            cats = [c for c in cats if current.lower() in c.lower()]
        return [app_commands.Choice(name=c, value=c) for c in cats[:25]]

    #
    # Slash command /quiz
    #
    @app_commands.command(name="quiz", description="Lancer un quiz de culture générale.")
    @app_commands.describe(
        nb="Nombre de questions (5-15)",
        category="Catégorie (sport, esport, culture, ...). Vide = toutes.",
        difficulty="Niveau de difficulté (facile, moyen, difficile). Optionnel.",
    )
    async def quiz(
        self,
        interaction: Interaction,
        nb: app_commands.Range[int, 1, 20] = 5,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        # Charge les questions
        pool = load_questions(category)

        if difficulty:
            difficulty = difficulty.lower()
            pool = [q for q in pool if q.get("difficulty", "").lower() == difficulty]

        if not pool:
            msg = "Aucune question trouvée"
            if category:
                msg += f" pour la catégorie **{category}**"
            if difficulty:
                msg += f" et la difficulté **{difficulty}**"
            await interaction.followup.send("❌ " + msg, ephemeral=True)
            return

        if nb > len(pool):
            nb = len(pool)

        questions = random.sample(pool, k=nb)

        score = 0
        for idx, q in enumerate(questions, start=1):
            correct = await self.ask_one_question(interaction, q, idx, nb)
            if correct:
                score += 1

        await interaction.followup.send(
            f"🏁 Quiz terminé !\n\nTu as obtenu **{score}/{nb}** ✅",
            ephemeral=True,
        )

    async def ask_one_question(
        self,
        interaction: Interaction,
        question_data: dict,
        index: int,
        total: int,
    ) -> bool:
        """Pose une question et attend la réponse de l'utilisateur sous forme de message."""

        q_text = question_data.get("q", "Question ?")
        choices = question_data.get("choices", [])
        correct_index = question_data.get("a", 0)
        category = question_data.get("category", "inconnue")
        difficulty = question_data.get("difficulty", "inconnue")

        # Construction de l'embed
        embed = Embed(
            title=f"Question {index}/{total}",
            description=q_text,
            color=discord.Color.blurple(),
        )
        labels = ["A", "B", "C", "D"]
        lines = []
        for i, choice in enumerate(choices):
            if i >= len(labels):
                break
            lines.append(f"**{labels[i]}** — {choice}")
        embed.add_field(name="Réponses possibles :", value="\n".join(lines), inline=False)
        embed.set_footer(text=f"Catégorie: {category} • Difficulté: {difficulty}")

        await interaction.followup.send(
            "Réponds dans le chat avec **A**, **B**, **C** ou **D**.",
            embed=embed,
            ephemeral=True,
        )

        def check(m: discord.Message) -> bool:
            return (
                m.author == interaction.user
                and m.channel == interaction.channel
                and m.content.strip().upper() in ["A", "B", "C", "D"]
            )

        try:
            msg: discord.Message = await self.bot.wait_for(
                "message",
                timeout=30.0,
                check=check,
            )
        except TimeoutError:
            await interaction.followup.send(
                "⏰ Temps écoulé pour cette question.",
                ephemeral=True,
            )
            return False

        answer_letter = msg.content.strip().upper()
        mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
        user_index = mapping[answer_letter]

        is_correct = user_index == correct_index

        if is_correct:
            await interaction.followup.send("✅ Bonne réponse !", ephemeral=True)
        else:
            correct_letter = [k for k, v in mapping.items() if v == correct_index][0]
            correct_choice = choices[correct_index] if 0 <= correct_index < len(choices) else "?"
            await interaction.followup.send(
                f"❌ Mauvaise réponse. La bonne réponse était **{correct_letter}** — {correct_choice}",
                ephemeral=True,
            )

        return is_correct


async def setup(bot: commands.Bot):
    await bot.add_cog(Quiz(bot))
