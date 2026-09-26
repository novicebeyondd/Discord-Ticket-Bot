import json
import discord
from discord.ext import commands

from embed import build_ticket_panel_embed, TicketPanelView

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True 

bot = commands.Bot(command_prefix=",", intents=intents)
bot.config = config  


@bot.event
async def on_ready():
    bot.add_view(TicketPanelView())  # re-register persistent view after restart

    activity = discord.Streaming(
        name="join resurgence",
        url=config["stream_url"]
    )
    await bot.change_presence(activity=activity)

    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.command(name="msg")
@commands.has_permissions(administrator=True)
async def msg(ctx: commands.Context):
    embed = build_ticket_panel_embed()
    await ctx.send(embed=embed, view=TicketPanelView())


@msg.error
async def msg_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need to be an administrator to use this command.")


if __name__ == "__main__":
    bot.run(config["token"])
