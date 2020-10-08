import discord, asyncio, re
from discord.ext import tasks
from discord.ext.commands import command, Cog
from utilities import main_messages_style, footer, positive_emojis_list, defaultcolor


class reactionRole(Cog):

    def __init__(self,client):
        self.client = client

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        role = None
        guild_id = str(payload.guild_id)

        ids_data = await self.client.pg_con.fetch("SELECT menu_id FROM bot_roles WHERE guild_id = $1", guild_id)
        ids_list = [item for i in ids_data for item in i]

        if str(payload.message_id) in ids_list:

            guild = self.client.get_guild(payload.guild_id)
            emojis_data = await self.client.pg_con.fetch("SELECT emoji_name FROM bot_roles WHERE guild_id = $1", guild_id)
            emojis_list = [item for i in emojis_data for item in i]

            role_data = await self.client.pg_con.fetch("SELECT role_name FROM bot_roles WHERE guild_id = $1", guild_id)
            role_list = [item for i in role_data for item in i]

            for i in range(len(emojis_list)):
                if ":" in emojis_list[i]:
                    emoji = str(emojis_list[i])
                    pattern = ":(.*?):"
                    emoji_name_db = re.search(pattern, emoji).group(1)

                if payload.emoji.name == emoji_name_db:
                    role = discord.utils.get(guild.roles, name=role_list[i])
                
            if role:
                member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                await member.add_roles(role)



    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        role = None
        guild_id = str(payload.guild_id)

        ids_data = await self.client.pg_con.fetch("SELECT menu_id FROM bot_roles WHERE guild_id = $1", guild_id)
        ids_list = [item for i in ids_data for item in i]

        if str(payload.message_id) in ids_list:
            guild = self.client.get_guild(payload.guild_id)

            emojis_data = await self.client.pg_con.fetch("SELECT emoji_name FROM bot_roles WHERE guild_id = $1", guild_id)
            emojis_list = [item for i in emojis_data for item in i]

            role_data = await self.client.pg_con.fetch("SELECT role_name FROM bot_roles WHERE guild_id = $1", guild_id)
            role_list = [item for i in role_data for item in i]
            
            for index in range(len(emojis_list)):
                if ":" in emojis_list[index]:
                    emoji = str(emojis_list[index])
                    pattern = ":(.*?):"
                    emoji_name_db = re.search(pattern, emoji).group(1)
                    

                if payload.emoji.name == emoji_name_db:
                    role = discord.utils.get(guild.roles, name=role_list[index])

            if role:
                member = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
                await member.remove_roles(role)
            

    @command(name="CreateRoles", aliases=["ReactionRoles", "CreateRole", "ReactionRole", "RoleCreate", "MenuRole", "createrole"])
    async def CreateRoles(self, ctx, amount):

        roles_list = []
        guild_id = str(ctx.guild.id)
        
        def check(ctx, m):
            return m.author == ctx.author

        embed = main_messages_style("Reaction Role Tool", "Type the Title for the embed message")
        await ctx.send(embed=embed)

        title = await self.client.wait_for('message')
        await asyncio.sleep(1)
        await ctx.channel.purge(limit=3)


        embed = main_messages_style("Reaction Role Tool", "Type the Description/Category for the roles")
        await ctx.send(embed=embed)


        main_description = await self.client.wait_for('message')

        await asyncio.sleep(1)
        await ctx.channel.purge(limit=2)

        for i in range(int(amount)):

            embed = main_messages_style("Reaction Role Tool", "Type the roles name")
            await ctx.send(embed=embed)

            Role = await self.client.wait_for('message')
            await asyncio.sleep(1)
            await ctx.channel.purge(limit=2)

            embed = main_messages_style("Reaction Role Tool", "Type the Emoji for the Role")
            await ctx.send(embed=embed)

            Emoji = await self.client.wait_for('message')
            await asyncio.sleep(1)
            await ctx.channel.purge(limit=2)

            embed = main_messages_style("Reaction Role Tool", "Type the roles Description")
            await ctx.send(embed=embed)

            Description = await self.client.wait_for('message')
            await asyncio.sleep(1)
            await ctx.channel.purge(limit=2)


            roles_dict = {
                "Emoji": Emoji.content,
                "Description": Description.content,
                "Role": Role.content
            }

            roles_list.append(roles_dict)



        embed = discord.Embed(title=title.content, description=main_description.content, color=defaultcolor)
        embed.set_author(name="Reaction Role")

        for item in range(int(amount)):
            embed.add_field(name=roles_list[item]["Role"] + " -  " + roles_list[item]["Emoji"] , value=roles_list[item]["Description"], inline=True)

        embed.set_footer(text=footer)

        menu = await ctx.send(embed=embed)

        menu_id = str(menu.id)
        

        for item in range(int(amount)):
            emoji = roles_list[item]["Emoji"]

            await menu.add_reaction(emoji)

            await self.client.pg_con.execute("INSERT INTO bot_roles (guild_id, emoji_name, role_name, menu_id) VALUES ($1, $2, $3, $4)", 
                                              guild_id, roles_list[item]["Emoji"], roles_list[item]["Role"], menu_id)


def setup(client):
    client.add_cog(reactionRole(client))