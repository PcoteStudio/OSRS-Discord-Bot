import traceback
from datetime import datetime
import nextcord
import logging
from nextcord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Extend this dict with your custom errors. Put the error class as key and the message you want to send as value.
    # The message can be formatted with the context referred as "ctx" and the error object as "err".
    # For more info on formatting, read https://pyformat.info/
    _error_messages = {
        nextcord.ApplicationCheckFailure: 'You do not have the rights to use this command',
        commands.CheckFailure: 'You do not have the rights to use this command',
        commands.NoPrivateMessage: 'This command cannot be used in private messages',
        commands.BotMissingPermissions: '{err}',
        commands.DisabledCommand: 'This command is disabled and cannot be used',
        commands.CommandOnCooldown: '{err}',
        commands.MissingRequiredArgument: 'You are missing a required argument! (See `{ctx.prefix}help {ctx.command.qualified_name}` for info on how to use this command).',
        commands.BadArgument: 'Invalid argument given! (See `{ctx.prefix}help {ctx.command.qualified_name}` for info on how to use this command).',
        commands.CommandNotFound: None,

    }

    def _format_traceback(self, error, maxlength):
        v = ''
        for line in traceback.format_tb(error.__traceback__):
            if len(v) + len(line) > maxlength:
                return v
            v = f'{v}\n{line}'
        if len(v) > 0:
            return v

    async def _send_traceback_embed(self, ctx: commands.Context, embed: nextcord.Embed):

        cfg_value = self.bot.config.get('error_report_channel')

        if not cfg_value:
            return

        if cfg_value == 1:
            app_info = await ctx.bot.application_info()

            channel = app_info.owner.dm_channel if app_info.owner.dm_channel else await app_info.owner.create_dm()
        else:
            channel = self.bot.get_channel(cfg_value)

            if not channel:
                return

            perms = channel.permissions_for(ctx.guild.me if ctx.guild else None)
            if not perms.view_channel or not perms.send_messages or not perms.embed_links:
                return

        try:
            await channel.send(embed=embed)
        except:
            pass

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: nextcord.Interaction, error):
        classname = error.__class__
        if classname in self._error_messages.keys():
            msg = self._error_messages.get(classname, None)
            if isinstance(msg, str):
                await interaction.send(":x: " + msg.format(err=error))
        else:
            logging.error("TODO Handle application command errors")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        classname = error.__class__

        if classname in self._error_messages.keys():
            msg = self._error_messages.get(classname, None)

            if isinstance(msg, str):
                await ctx.send(msg.format(ctx=ctx, err=error))
        else:

            if isinstance(error, (commands.CommandError, commands.CheckFailure, nextcord.ApplicationCheckFailure)) and not isinstance(error, commands.CommandInvokeError):
                return await ctx.send(f':x: {error}')

            await ctx.send(':rotating_light: An error occured while trying to execute that command')

            logging.error(error.original)

            embed = nextcord.Embed(
                color=nextcord.Colour(0xff0000),
                title='Command execution failed',
                timestamp=datetime.now()
            )

            embed.add_field(name='Command', value=ctx.command)
            embed.add_field(name='Original message',
                            value=ctx.message.content[:1021] + (ctx.message.content[1021:] and '...'))
            embed.add_field(name='Channel', value='Private Message' if isinstance(
                ctx.channel, nextcord.DMChannel) else f'#{ctx.channel.name} (`{ctx.channel.id}`)')
            embed.add_field(name='Sender', value=f'{ctx.author} (`{ctx.author.id}`)')
            embed.add_field(name='Exception', value=error)

            # Embed desc limit is 4096 characters, which includes the codeblock markers
            formatted_traceback = self._format_traceback(error.original, 4090)

            embed.description = f'```{formatted_traceback}```'

            await self._send_traceback_embed(ctx, embed)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))