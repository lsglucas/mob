import discord

from discord.ext import commands, tasks
from settings import *
from style import *


# General use bot commands 
class General(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Print in the console when the bot starts to run (if everything is working perfectly)
    @commands.Cog.listener()
    async def on_ready(self):
        print('The Bot is Online!')
        self.change_status.start()
        
    #Discord live status that rotate from the list each 600 seconds
    @tasks.loop(seconds=600)
    async def change_status(self):
        await self.client.change_presence(activity=discord.Game(next(status_list)))
        print("Next status")

    # Allow and disallow and show the list of the text channel in which the bot can send messages, the variable is stored in /bot/settings.py
    @commands.command()
    async def chat_permission(self, ctx, option=""):
        channel_id = ctx.channel.id
        option = option.lower()
        if option != "allow" and option != "revoke" and option != "list" and option == "":
            embed = main_messages_style("Command **permission** allow or prohibit the bot messages in this chat","Option not available, you must use Allow, "
            "Prohibit or List ", " 😕")
            await ctx.send(embed=embed)
            await ctx.message.add_reaction(next(negative_emojis_list))

        else:
            if option == "allow":
                if channel_id not in allowed_channels:
                    allowed_channels.append(ctx.channel.id)
                    embed = main_messages_style(f"Now I will operate in #{self.client.get_channel(ctx.channel.id)}")
                    await ctx.send(embed=embed)
                    await ctx.message.add_reaction(next(positive_emojis_list))
                else:
                    embed =main_messages_style("I already operate in this channel")
                    await ctx.send(embed=embed)
                    await ctx.message.add_reaction(next(negative_emojis_list))

            elif option == "revoke":
                if channel_id in allowed_channels:
                    allowed_channels.remove(ctx.channel.id)
                    embed = main_messages_style(f"I will no longer operate in #{self.client.get_channel(ctx.channel.id)}")
                    await ctx.send(embed=embed)
                    await ctx.message.add_reaction(next(positive_emojis_list))
                else:
                    embed = main_messages_style("I already don't have permission to operate in this channel")
                    await ctx.send(embed=embed)            
                    await ctx.message.add_reaction(next(negative_emojis_list))

            elif option == "list":
                if channel_id in allowed_channels:
                    list_allowed = []
                    for i in range(len(allowed_channels)):
                        list_allowed.append(str(self.client.get_channel((allowed_channels[i]))))
                    
                    if len(list_allowed) != 0:
                        str_list_allowed = ''
                        for elem in list_allowed:
                            str_list_allowed += elem + ',  #' if list_allowed.index(elem) != len(list_allowed)-1 else elem
                        
                        embed = main_messages_style(f"Channels allowed: #{str_list_allowed}")
                        await ctx.send(embed=embed)
                        await ctx.message.add_reaction(next(positive_emojis_list))
                else:
                    embed = main_messages_style(f"I don't have permission to chat here, type **mack bot allow** to give me the authorization to send messages and read commands in"
                    f" #{self.client.get_channel(ctx.channel.id)}")
                    await ctx.send(embed=embed)
                    await ctx.message.add_reaction(next(negative_emojis_list))

    # Clear the previous line for x amout of times
    @commands.command()
    async def clear(self, ctx, amount=2):
        if ctx.channel.id in allowed_channels:
            await ctx.channel.purge(limit=amount)
            await ctx.message.add_reaction(next(positive_emojis_list))
            print("clear command")


def setup(client):
    client.add_cog(General(client))