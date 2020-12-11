import asyncio
import os
import discord
import yaml
import discord.utils
import json
import time
import logging
from discord import PermissionOverwrite
from discord.ext import commands

bot_version = '2.3.0'
# Logging module
log_files = os.listdir(os.path.join('./logs/errors/'))
log_number = int(len(log_files))
log_name = 'log-{}.txt'.format(log_number)
logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename=os.path.join('./logs/errors/' + log_name), encoding='utf-8', mode='w')
handler.setFormatter(
    logging.Formatter('[%(asctime)s] %(levelname)s:\n'
                      '\t%(funcName)s\n'
                      '\t%(message)s\n'
                      '\t%(pathname)s\n\n')
)
logger.addHandler(handler)

# Loading config.yml file.
with open('config.yml', 'r') as cfg:
    config = yaml.load(cfg, Loader=yaml.SafeLoader)

# Loading up the bot.
prefix = config.get('Discord_Configs').get('prefix')
guild_id = int(config.get('Discord_Configs').get('discord_server_id'))
public_vc_id = int(config.get('Auto_VC_Configs').get('public_vc_id'))
hidden_vc_id = int(config.get('Auto_VC_Configs').get('hidden_vc_id'))
category_id = int(config.get('Auto_VC_Configs').get('category_id'))
embed_color = int(('0x' + str(config.get('Discord_Configs').get('embed_color')).lower()), 16)
channeldata_file = os.path.join('./data/channeldata.json')
emotes = ['🔒', '🔓', '🤫', '<a:circlecheckmark:591721777520967692>', '<:red_x_box:718640094864474223>']
intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix=[prefix, prefix.upper()], intents=intents)
bot.remove_command('help')


def load_json(file):
    """
    :param file: file_name.json as a string
    :return: returns data (type: Any)
    """
    json_file = open(str(file), 'r')
    data = json.load(json_file)
    json_file.close()
    return data


def get_key(val, dic):
    for key in dic:
        if dic[key][0] == val:
            return key


async def record_usage(ctx):
    print(ctx.author, 'used', ctx.command, 'at', ctx.message.created_at)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=prefix + "help"
        )
    )
    guild_obj = bot.get_guild(guild_id)
    info1 = 'Discord Bot online @ {0.user}'.format(bot)
    info2 = 'Guild: {} [{}]'.format(guild_obj.name, guild_id)
    print(info1)
    print(info2)


@bot.event
async def on_voice_state_update(member, before, after):
    await bot.wait_until_ready()
    # Data stored as {"channel_id": ["owner_discord_id", "true/false depending on whether channel is hidden"]}
    channeldata = load_json(channeldata_file)
    try:
        ### If channel becomes empty, delete channel // check to make sure channel is not 'join here!' channel:
        if len(before.channel.members) == 0 and before.channel.category_id == category_id:
            if len(before.channel.members) == 0:
                if before.channel.id != public_vc_id and before.channel.id != hidden_vc_id:
                    await before.channel.delete()  # Deletes empty channel.
                    if str(before.channel.id) in channeldata:  # Removes channel from channeldata.json file.
                        t = channeldata.pop(str(before.channel.id))
                        json_file = open(channeldata_file, 'w+')
                        json_file.write(json.dumps(channeldata, indent=4))
                        json_file.close()
                    else:
                        pass
                else:
                    pass
            else:
                pass
    except:
        pass

    # --------------

    try:
        # A) If user joins pre-defined PUBLIC_vc 'join here!' channel:"""
        if after.channel.id == public_vc_id:
            vc = await member.guild.create_voice_channel(
                name='{}'.format(member.display_name),
                category=member.guild.get_channel(category_id),
                overwrites={
                    discord.utils.get(member.guild.roles, name='Verify IGN'): discord.PermissionOverwrite(
                        view_channel=False,
                        connect=False
                    ),
                    discord.utils.get(member.guild.roles, name='Discord Staff ☆'): discord.PermissionOverwrite(
                        view_channel=True,
                        connect=True
                    ),
                    member: discord.PermissionOverwrite(
                        view_channel=True,
                        connect=True
                    )
                }
            )

            # // prevented by 2 name edits per 10 min rate limit :(
            # if after.channel.id == public_vc_id:
            #     vc = await member.guild.create_voice_channel(
            #         name='{}| {}'.format(emotes[1], member.display_name),
            #         category=member.guild.get_channel(category_id),
            #         overwrites={
            #             discord.utils.get(member.guild.roles, name='Verify IGN'): discord.PermissionOverwrite(
            #                 view_channel=False,
            #                 connect=False
            #             ),
            #             discord.utils.get(member.guild.roles, name='Discord Staff ☆'): discord.PermissionOverwrite(
            #                 view_channel=True,
            #                 connect=True
            #             ),
            #             member: discord.PermissionOverwrite(
            #                 view_channel=True,
            #                 connect=True
            #             )
            #         }
            #     )

            # Moves channel owner into the channel.
            await member.move_to(vc)
            # Log channel data & owner to channeldata.json file.
            channel_data = load_json(channeldata_file)
            channel_data[str(vc.id)] = [str(member.id), "false"]
            json_file = open(channeldata_file, 'w+')
            json_file.write(json.dumps(channel_data, indent=4))
            json_file.close()

        # B) If user joins pre-defined PRIVATE_vc 'join here!' channel:
        if after.channel.id == hidden_vc_id:
            vc = await member.guild.create_voice_channel(
                name='{}'.format(member.display_name),
                category=member.guild.get_channel(category_id),
                overwrites={
                    member.guild.roles[0]: discord.PermissionOverwrite(
                        view_channel=False,
                        connect=False
                    ),
                    discord.utils.get(member.guild.roles, name='Verify IGN'): discord.PermissionOverwrite(
                        view_channel=False,
                        connect=False
                    ),
                    discord.utils.get(member.guild.roles, name='Discord Staff ☆'): discord.PermissionOverwrite(
                        view_channel=True,
                        connect=True
                    ),
                    member: discord.PermissionOverwrite(
                        view_channel=True,
                        connect=True
                    )
                }
            )

            # // prevented by 2 name edits per 10 min rate limit :(
            # vc = await member.guild.create_voice_channel(
            #     name='{}{}| {}'.format(emotes[2], emotes[0], member.display_name),
            #     category=member.guild.get_channel(category_id),
            #     overwrites={
            #         member.guild.roles[0]: discord.PermissionOverwrite(
            #             view_channel=False,
            #             connect=False
            #         ),
            #         discord.utils.get(member.guild.roles, name='Verify IGN'): discord.PermissionOverwrite(
            #             view_channel=False,
            #             connect=False
            #         ),
            #         discord.utils.get(member.guild.roles, name='Discord Staff ☆'): discord.PermissionOverwrite(
            #             view_channel=True,
            #             connect=True
            #         ),
            #         member: discord.PermissionOverwrite(
            #             view_channel=True,
            #             connect=True,
            #         )
            #     }
            # )

            # Moves channel owner into the channel.
            await member.move_to(vc)
            # Log channel data & owner to channeldata.json file.
            channel_data = load_json(channeldata_file)
            channel_data[str(vc.id)] = [str(member.id), "true"]
            json_file = open(channeldata_file, 'w+')
            json_file.write(json.dumps(channel_data, indent=4))
            json_file.close()
    except:
        pass
    return


@bot.command()
async def transfer(ctx, m: discord.User = None):
    """Transfer ownership of a channel to a user // can only be used by channel owner."""
    if m is None:
        embed = discord.Embed(
            title='⚠ Error - Invalid Arguments',
            description='**Usage**: `{}transfer <@user>`'.format(prefix),
            color=0xff5555
        )
        await ctx.send(embed=embed)
    else:
        await bot.wait_until_ready()
        channeldata = load_json(channeldata_file)
        if str(ctx.message.author.id) in [x for v in channeldata.values() for x in v]:
            channel_id = get_key(str(ctx.message.author.id), channeldata)
            channeldata[channel_id] = [str(m.id), channeldata[channel_id][1]]
            json_file = open(channeldata_file, 'w+')
            json_file.write(json.dumps(channeldata, indent=4))
            json_file.close()
            # channel_obj = ctx.guild.get_channel(int(channel_id))
            # c_attr = channel_obj.name.split('| ')[0] + '| '
            # // prevented by 2 name edits per 10 min rate limit :(
            embed = discord.Embed(
                title='',
                description='{} Successfully made {} the owner of your channel!'.format(emotes[3], m.mention),
                color=embed_color
            )
            # await channel_obj.edit(name=c_attr + m.display_name)
            # // prevented by 2 name edits per 10 min rate limit :(
            if channeldata[channel_id][1] == "true":
                await ctx.message.delete()
            else:
                await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title='',
                description='{} You do not own a channel!'.format(emotes[4]),
                color=embed_color
            )
            await ctx.channel.send(embed=embed)


@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def limit(ctx, i):
    """Changes the member limit of the voice channel // can only be used by channel owner."""
    await bot.wait_until_ready()
    # Ensures user entered an integer less than 99 greater than 0.
    if int(i) > 99 or int(i) < 1:
        embed = discord.Embed(
            title='⚠ Error - Invalid Arguments',
            description='**Usage**: `{}limit 5`'.format(prefix),
            color=0xff5555
        )
        await ctx.send(embed=embed)
    else:
        channeldata = load_json(channeldata_file)
        if str(ctx.message.author.id) in [x for v in channeldata.values() for x in v]:
            channel_id = get_key(str(ctx.message.author.id), channeldata)
            channel_obj = ctx.guild.get_channel(int(channel_id))
            await channel_obj.edit(user_limit=int(i))
            embed = discord.Embed(
                title='',
                description='{} Successfully limited `{}` to `{}` users!'.format(emotes[3], channel_obj.name, str(i)),
                color=embed_color
            )
            if channeldata[channel_id][1] == "true":
                await ctx.message.delete()
            else:
                await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(
                title='',
                description='{} You do not own a channel!'.format(emotes[4]),
                color=embed_color
            )
            await ctx.channel.send(embed=embed)


@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def hide(ctx):
    """Makes voice channel invisible // can only be used by channel owner."""
    await bot.wait_until_ready()
    channeldata = load_json(channeldata_file)
    if str(ctx.message.author.id) in [x for v in channeldata.values() for x in v]:
        channel_id = get_key(str(ctx.message.author.id), channeldata)
        channel_obj = ctx.guild.get_channel(int(channel_id))
        # if channel_obj.name.startswith(emotes[2]): // prevented by 2 name edits per 10 min rate limit :(
        # await channel_obj.edit(name=emotes[2] + channel_obj.name)
        # // prevented by 2 name edits per 10 min rate limit :(
        overwrites = PermissionOverwrite(view_channel=False)
        await channel_obj.set_permissions(target=ctx.guild.default_role, overwrite=overwrites)
        for m in channel_obj.members:
            await channel_obj.set_permissions(
                target=m,
                overwrite=PermissionOverwrite(view_channel=True)
            )
        channeldata[channel_id] = [str(ctx.message.author.id), "true"]
        json_file = open(channeldata_file, 'w+')
        json_file.write(json.dumps(channeldata, indent=4))
        json_file.close()
        await ctx.message.delete()
    else:
        embed = discord.Embed(
            title='',
            description='{} You do not own a channel!'.format(emotes[4]),
            color=embed_color
        )
        await ctx.channel.send(embed=embed)


@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def unhide(ctx):
    """Makes voice channel visible to anyone // can only be used by channel owner."""
    await bot.wait_until_ready()
    channeldata = load_json(channeldata_file)
    if str(ctx.message.author.id) in [x for v in channeldata.values() for x in v]:
        channel_id = get_key(str(ctx.message.author.id), channeldata)
        channel_obj = ctx.guild.get_channel(int(channel_id))
        # if channel_obj.name.startswith(emotes[2]): // prevented by 2 name edits per 10 min rate limit :(
        # await channel_obj.edit(name=channel_obj.name[1:]) // prevented by 2 name edits per 10 min rate limit :(

        overwrites = PermissionOverwrite(view_channel=True)
        await channel_obj.set_permissions(target=ctx.guild.default_role, overwrite=overwrites)
        channeldata[channel_id] = [str(ctx.message.author.id), "false"]
        json_file = open(channeldata_file, 'w+')
        json_file.write(json.dumps(channeldata, indent=4))
        json_file.close()
        await ctx.message.add_reaction(emoji=emotes[3])

    else:
        embed = discord.Embed(
            title='',
            description='{} You do not own a channel!'.format(emotes[4]),
            color=embed_color
        )
        await ctx.channel.send(embed=embed)


@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def lock(ctx):
    """Makes voice channel private // can only be used by channel owner."""
    await bot.wait_until_ready()
    channeldata = load_json(channeldata_file)
    if str(ctx.message.author.id) in [x for v in channeldata.values() for x in v]:
        channel_obj = ctx.guild.get_channel(int(get_key(str(ctx.message.author.id), channeldata)))
        # if emotes[0] in channel_obj.name:
        # embed = discord.Embed(
        # title='',
        # description='{} is already locked!'.format(channel_obj.name),
        # color=embed_color
        # )
        # await ctx.send(embed=embed)

        # c_name = channel_obj.name.replace(emotes[1], emotes[0])  # Replace unlock with lock.
        # await channel_obj.edit(name=c_name)
        # // prevented by 2 name edits per 10 min rate limit :(
        overwrites = PermissionOverwrite(connect=False)
        await channel_obj.set_permissions(target=ctx.guild.default_role, overwrite=overwrites)
        for m in channel_obj.members:
            await channel_obj.set_permissions(
                target=m,
                overwrite=PermissionOverwrite(connect=True)
            )
        await ctx.message.add_reaction(emotes[0])
    else:
        embed = discord.Embed(
            title='',
            description='{} You do not own a channel!'.format(emotes[4]),
            color=embed_color
        )
        await ctx.channel.send(embed=embed)


@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def unlock(ctx):
    """Makes voice channel public // can only be used by channel owner."""
    await bot.wait_until_ready()
    channeldata = load_json(channeldata_file)
    if str(ctx.message.author.id) in [x for v in channeldata.values() for x in v]:
        channel_obj = ctx.guild.get_channel(int(get_key(str(ctx.message.author.id), channeldata)))
        # if emotes[1] in channel_obj.name:
        #     embed = discord.Embed(
        #         title='',
        #         description='{} is already unlocked!'.format(channel_obj.name),
        #         color=embed_color
        #     )
        #     await ctx.send(embed=embed)
        # c_name = channel_obj.name.replace(emotes[0], emotes[1])  # Replace lock with unlock.
        # await channel_obj.edit(name=c_name)
        # // prevented by 2 name edits per 10 min rate limit :(
        overwrites = PermissionOverwrite(connect=True)
        await channel_obj.set_permissions(target=ctx.guild.default_role, overwrite=overwrites)
        await ctx.message.add_reaction(emotes[1])
    else:
        embed = discord.Embed(
            title='',
            description='{} You do not own a channel!'.format(emotes[4]),
            color=embed_color
        )
        await ctx.channel.send(embed=embed)


@bot.command()
@commands.cooldown(2, 120, commands.BucketType.guild)
async def rename(ctx, *name):
    """Renames a voice channel // can only be used by channel owner."""
    await bot.wait_until_ready()
    channeldata = load_json(channeldata_file)
    if str(ctx.message.author.id) in [x for v in channeldata.values() for x in v]:
        channel_id = get_key(str(ctx.message.author.id), channeldata)
        channel_obj = ctx.guild.get_channel(int(channel_id))
        if not name:
            embed = discord.Embed(
                title='⚠ Error - Invalid Arguments',
                description='**Usage**: `{}rename <new-channel-name>`'.format(prefix),
                color=0xff5555
            )
            await ctx.send(embed=embed)
        elif type(name) == str:
            await channel_obj.edit(name=name)
            if channeldata[channel_id][1] == "true":
                await ctx.message.delete()
            else:
                await ctx.message.add_reaction(emoji=emotes[3])
        elif type(name) == tuple:
            given_name = ' '.join(name)
            await channel_obj.edit(name=given_name)
            if channeldata[channel_id][1] == "true":
                await ctx.message.delete()
            else:
                await ctx.message.add_reaction(emoji=emotes[3])
        else:
            await ctx.message.add_reaction(emoji=emotes[4])



@bot.command()
@commands.cooldown(5, 15, commands.BucketType.user)
async def invite(ctx, m: discord.Member = None):
    """Permits a user to join a voice channel // can only be used by channel owner."""
    await bot.wait_until_ready()
    channeldata = load_json(channeldata_file)
    if str(ctx.message.author.id) in [x for v in channeldata.values() for x in v]:
        if m is None:
            embed = discord.Embed(
                title='⚠ Error - Invalid Arguments',
                description='**Usage**: `{}invite <@user>`'.format(prefix),
                color=0xff5555
            )
            await ctx.send(embed=embed)
        else:
            channeldata = load_json(channeldata_file)
            channel_id = get_key(str(ctx.message.author.id), channeldata)
            channel_obj = ctx.guild.get_channel(int(channel_id))
            await channel_obj.set_permissions(
                target=m,
                overwrite=PermissionOverwrite(view_channel=True, connect=True)
            )
            if channeldata[channel_id][1] == "true":
                await ctx.message.delete()
            else:
                await ctx.message.add_reaction(emoji=emotes[3])


@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def uninvite(ctx, m: discord.Member = None):
    """Removes the invite given with invite() command // can only be used by channel owner."""
    await bot.wait_until_ready()
    channeldata = load_json(channeldata_file)
    if str(ctx.message.author.id) in [x for v in channeldata.values() for x in v]:
        if m is None:
            embed = discord.Embed(
                title='⚠ Error - Invalid Arguments',
                description='**Usage**: `{}uninvite <@user>`'.format(prefix),
                color=0xff5555
            )
            await ctx.send(embed=embed)
        else:
            channeldata = load_json(channeldata_file)
            channel_id = get_key(str(ctx.message.author.id), channeldata)
            channel_obj = ctx.guild.get_channel(int(channel_id))
            await channel_obj.set_permissions(
                target=m,
                overwrite=None
            )
            if channeldata[channel_id][1] == "true":
                await ctx.message.delete()
            else:
                await ctx.message.add_reaction(emoji=emotes[3])


@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def kick(ctx, m: discord.Member = None):
    """Kicks someone from a voice channel // can only be used by channel owner."""
    await bot.wait_until_ready()
    channeldata = load_json(channeldata_file)
    if str(ctx.message.author.id) in [x for v in channeldata.values() for x in v]:
        if m is None:
            embed = discord.Embed(
                title='⚠ Error - Invalid Arguments',
                description='**Usage**: `{}kick <@user>`'.format(prefix),
                color=0xff5555
            )
            await ctx.send(embed=embed)
        elif str(m.voice.channel.id) == str(get_key(str(ctx.message.author.id), channeldata)):
            channel_id = get_key(str(ctx.message.author.id), channeldata)
            channel_obj = ctx.guild.get_channel(int(channel_id))
            await m.move_to(channel=None)  # Disconnects user from channel
            await channel_obj.set_permissions(
                target=m,
                overwrite=PermissionOverwrite(connect=False)
            )
            if channeldata[channel_id][1] == "true":
                await ctx.message.delete()
            else:
                await ctx.message.add_reaction(emoji=emotes[3])
        else:
            await ctx.message.add_reaction(emoji=emotes[4])


@bot.command()
async def botinfo(ctx):
    """Displays information about the bot."""
    await bot.wait_until_ready()
    embed = discord.Embed(color=embed_color)
    embed.add_field(name='About {}'.format(bot.user.display_name),
                    value='**Developer**: xEricL#0001\n'
                          '**Version**: `{}`\n'.format(bot_version)
                    )
    embed.set_thumbnail(url=ctx.guild.icon_url)
    await ctx.send(embed=embed)


@bot.command()
async def help(ctx):
    await bot.wait_until_ready()
    embed = discord.Embed(
        color=0x202225
    )
    # Commands
    embed.add_field(
        name='Commands',
        value='♕ **{0}lock**\n» Locks your voice channel.\n\n'
              '♕ **{0}unlock**\n» Unlocks your voice channel.\n\n'
              '♕ **{0}hide**\n» Hides your voice channel.\n\n'
              '♕ **{0}unhide**\n» Makes your voice channel visible.\n\n'
              '♕ **{0}invite <@user>**\n» Invites a user to your voice channel.\n\n'
              '♕ **{0}uninvite <@user>**\n» Revokes a previous invite from a user.\n\n'
              '♕ **{0}kick <@user>**\n» Disconnects a user from your voice channel.\n\n'
              '♕ **{0}rename <name>**\n» Renames your voice channel.\n\n'
              '♕ **{0}transfer <@user>**\n» Transfers your channel ownership to another user.\n\n'
              '♕ **{0}botinfo**\n» Displays info about this bot.\n\n'
              ''.format(prefix),
        inline=False
    )
    t = time.strftime('%I:%M:%S %p %x', time.localtime())
    embed.set_footer(text=t)
    await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title='',
            description='❌ Invalid command! » Use **{}help** for a list of commands.'.format(prefix),
            color=0xff5555
        )
        await ctx.send(embed=embed)

    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title='',
            description='🕒 You are on **cooldown**! » Please try again in `{}` seconds.'.format(
                int(error.retry_after)),
            color=0xff5555
        )
        await ctx.send(embed=embed)

    else:
        embed = discord.Embed(
            title='',
            description='Error: {}\nCtx: {}'.format(error, ctx),
            color=0xff5555
        )
        await ctx.send(embed=embed)


@invite.error
async def invite_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title='',
            description='❌ That is not a valid discord member!',
            color=0xff5555
        )
        await ctx.send(embed=embed)
    else:
        print("Ctx: {}\nError: {}".format(ctx, error))


@uninvite.error
async def uninvite_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title='',
            description='❌ That is not a valid discord member!',
            color=0xff5555
        )
        await ctx.send(embed=embed)
    else:
        print("Ctx: {}\nError: {}".format(ctx, error))


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, AttributeError):
        embed = discord.Embed(
            title='',
            description='❌ That user is not in your voice channel!',
            color=0xff5555
        )
        await ctx.send(embed=embed)
    if isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title='',
            description='❌ That is not a valid discord member!',
            color=0xff5555
        )
        await ctx.send(embed=embed)
    else:
        print("Ctx: {}\nError: {}".format(ctx, error))


@bot.event
async def on_type_error(ctx, error):
    if isinstance(error, AttributeError):
        print(ctx.user.name + '-' + 'Ignoring NoneType Error')


bot.run(config.get('Discord_Configs').get('discord_token'))
