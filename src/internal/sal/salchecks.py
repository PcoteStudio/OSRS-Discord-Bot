import nextcord
from datetime import datetime
from nextcord.ext import application_checks
from internal.sal import snakesandladders
from internal.sal import salerrors


def get_game(interaction: nextcord.Interaction):
    game = snakesandladders.get_game(interaction.guild.id)
    if not game:
        raise salerrors.ApplicationNoSalSession
    return game


def get_team(interaction: nextcord.Interaction):
    game = get_game(interaction)
    team = game.get_team_by_player_id(interaction.user.id)
    if not team:
        raise salerrors.ApplicationPlayerNotInTeam
    return team


def game_exists():
    def predicate(interaction: nextcord.Interaction):
        get_game(interaction)
        return True
    return application_checks.check(predicate)


def game_is_ready():
    def predicate(interaction: nextcord.Interaction):
        game = get_game(interaction)
        if not game.is_ready():
            raise salerrors.ApplicationSalNotReady
        return True
    return application_checks.check(predicate)


def player_is_in_team():
    def predicate(interaction: nextcord.Interaction):
        get_team(interaction)
        return True
    return application_checks.check(predicate)


def command_is_in_team_channel():
    def predicate(interaction: nextcord.Interaction):
        team = get_team(interaction)
        if team.channel and interaction.channel.id != team.channel:
            raise salerrors.ApplicationNotInTeamChannel
        return True
    return application_checks.check(predicate)


def game_is_in_progress():
    def predicate(interaction: nextcord.Interaction):
        game = get_game(interaction)
        now = datetime.utcnow().replace(tzinfo=None)
        if now < game.start_time:
            raise salerrors.ApplicationSalNotStarted
        if now > game.end_time:
            raise salerrors.ApplicationSalAlreadyEnded
        return True
    return application_checks.check(predicate)


def game_has_not_started():
    def predicate(interaction: nextcord.Interaction):
        game = get_game(interaction)
        now = datetime.utcnow().replace(tzinfo=None)
        if now > game.start_time:
            raise salerrors.ApplicationSalAlreadyStarted
        return True
    return application_checks.check(predicate)
