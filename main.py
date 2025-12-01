import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
from dotenv import load_dotenv
import os
import random
import logging

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!$", intents=intents)
bot.remove_command("help")

# ---------------------------------------------------------
# RANK SYSTEM (LOWER NUMBER = HIGHER POWER)
# ---------------------------------------------------------

RANKS = {
    1015743528489451690: 1,  # Owner Adrian
    489388658902695944: 2,   # Dragon
    1029919801671438336: 3,  # Maddox
    370372665447284738: 4,   # Onyx
    981898351471644692: 5,   # Anna
    1362902418358145186: 6,  # Dabber
    1255287940775678048: 7,  # DJ

    # Leads
    1386376198514409493: 10, # Chloe
    1423072086275919977: 10, # Bear
    1428168893704306728: 10, # Ham
    1435363459817537643: 10, # Trip
    1420491676111077438: 10, # Sarge
    1179228928053870623: 10, # Hemorrhage
    1224505736667856939: 10, # Nat
    740668151313727528:  10  # Froend
}

LEADS = set(uid for uid in RANKS if RANKS[uid] == 10)
BAN_PERMS = set(uid for uid in RANKS if RANKS[uid] <= 7)


def get_rank(user_id: int):
    return RANKS.get(user_id, 999)

# ---------------------------------------------------------
# Fun
# ---------------------------------------------------------
@tasks.loop(seconds=60)
async def status_rotator():
    statuses = [
        "Keeping order ⚖️",
        "Watching everything 👁️",
        f"Type !$help for commands 💬",
        "Serving justice 🔨"
    ]
    try:
        await bot.change_presence(activity=discord.Game(random.choice(statuses)))
    except Exception:
        logger.exception("Failed changing presence")

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    if not status_rotator.is_running():
        status_rotator.start()
# ---------------------------------------------------------
# Ban Approval UI
# ---------------------------------------------------------

class BanApproval(View):
    def __init__(self, target_user, requester):
        super().__init__(timeout=120)
        self.target_user = target_user
        self.requester = requester

    @discord.ui.button(label="Approve Ban", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id not in BAN_PERMS:
            return await interaction.response.send_message(
                "❌ You do not have permission to approve bans.",
                ephemeral=True
            )

        approver_rank = get_rank(interaction.user.id)
        target_rank = get_rank(self.target_user.id)

        if approver_rank >= target_rank:
            return await interaction.response.send_message(
                "❌ You cannot approve a ban on someone with equal or higher rank.",
                ephemeral=True
            )

        guild = interaction.guild
        await guild.ban(self.target_user, reason=f"Ban approved by {interaction.user}")

        await interaction.response.edit_message(
            content=f"✅ Ban approved.\nUser `{self.target_user}` has been banned.",
            view=None
        )

    @discord.ui.button(label="Reject Ban", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id not in BAN_PERMS:
            return await interaction.response.send_message(
                "❌ You do not have permission to reject bans.",
                ephemeral=True
            )

        await interaction.response.edit_message(
            content=f"❌ Ban request rejected by `{interaction.user}`.",
            view=None
        )


# ---------------------------------------------------------
# Commands
# ---------------------------------------------------------
@bot.command()
async def banrequest(ctx, member: discord.Member = None, *, reason=None):
    if ctx.author.id not in LEADS:
        return await ctx.send("❌ Only Leads can request bans.")

    if member is None:
        return await ctx.send("Usage: !$banrequest @user <reason>")

    requester_rank = get_rank(ctx.author.id)
    target_rank = get_rank(member.id)

    if requester_rank >= target_rank:
        return await ctx.send("❌ You cannot request to ban someone with higher or equal rank.")

    approval_channel = bot.get_channel(1434242050605449307)
    if approval_channel is None:
        return await ctx.send("❌ Error: Approval channel not found.")

    ping_list = " ".join([f"<@{uid}>" for uid in BAN_PERMS])

    embed = discord.Embed(
        title="Ban Request Pending",
        description=(
            f"User: {member.mention}\n"
            f"Requested By: {ctx.author.mention}\n"
            f"Reason: {reason or 'No reason provided'}"
        ),
        color=discord.Color.orange()
    )

    view = BanApproval(member, ctx.author)

    await approval_channel.send(
        content=f"{ping_list}\n⚠️ **Ban approval needed.**",
        embed=embed,
        view=view
    )

    await ctx.send(f"✅ Ban request sent to the approval channel.")
    return None


# ---------------------------------------------------------
# Run Bot
# ---------------------------------------------------------
bot.run(TOKEN)