import discord
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!$", intents=intents)
bot.remove_command("help")


# ---------------------------------------------------------
# ID LISTS
# ---------------------------------------------------------

LEADS = {
    1386376198514409493, # Chloe
    1423072086275919977, # Bear
    1428168893704306728, # Ham
    1435363459817537643, # Trip
    1420491676111077438, # Sarge
    1179228928053870623, # Hemorrhage
    1224505736667856939, # Nat
    740668151313727528   # Froend

}

BAN_PERMS = {
    1015743528489451690,  # Owner Adrian
    489388658902695944,   # Dragon
    1029919801671438336,  # Maddox
    370372665447284738,   # Onyx
    981898351471644692,   # Anna
    1362902418358145186,  # Dabber
    1255287940775678048   # DJ
}


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