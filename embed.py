import discord
from database import db


def build_ticket_panel_embed() -> discord.Embed:
    """
    Fill in title/description/color/emojis yourself below.
    No banner image for now.
    """
    embed = discord.Embed(
        title="Support Tickets",
        description="Please select an option from the dropdown below to open a ticket.",
        color=discord.Color.from_str("#2b2d31")
    )
    return embed


class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="General Help",
                value="general",
                description="Open a general support ticket"
            )
        ]
        super().__init__(
            placeholder="Select an option to open a ticket",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        config = interaction.client.config

        existing_id, existing = db.get_open_ticket_for_user(interaction.user.id, guild.id)
        if existing:
            channel = guild.get_channel(int(existing_id))
            if channel:
                await interaction.response.send_message(
                    f"You already have an open ticket: {channel.mention}", ephemeral=True
                )
                return

        category = guild.get_channel(config["ticket_category_id"])
        support_role = guild.get_role(config["support_role_id"])

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}".lower(),
            category=category,
            overwrites=overwrites
        )

        db.create_ticket(channel.id, interaction.user.id, guild.id, category="general")

        ticket_embed = discord.Embed(
            title="General Help Ticket",
            description=f"{interaction.user.mention}, staff will be with you shortly.\nPlease describe your issue.",
            color=discord.Color.from_str("#2b2d31")
        )
        await channel.send(embed=ticket_embed, view=CloseTicketView())
        await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        db.close_ticket(interaction.channel.id)
        await interaction.response.send_message("Closing this ticket in 5 seconds...")
        await interaction.channel.delete(delay=5)
