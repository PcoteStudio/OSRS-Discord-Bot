import nextcord
from datetime import datetime
from nextcord.ext import application_checks
from internal.gol import gameoflife
from internal.gol import golerrors


def get_game(interaction: nextcord.Interaction):
    game = gameoflife.get_game(interaction.guild.id)
    if not game:
        raise golerrors.ApplicationNoGolSession
    return game


def get_team(interaction: nextcord.Interaction):
    game = get_game(interaction)
    team = game.get_team_by_player_id(interaction.user.id)
    if not team:
        raise golerrors.ApplicationPlayerNotInTeam
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
            raise golerrors.ApplicationGolNotReady
        return True
    return application_checks.check(predicate)


def player_is_in_team():
    def predicate(interaction: nextcord.Interaction):
        get_team(interaction)
        return True
    return application_checks.check(predicate)


def game_is_in_progress():
    def predicate(interaction: nextcord.Interaction):
        game = get_game(interaction)
        now = datetime.now()
        if now < game.start_time:
            raise golerrors.ApplicationGolNotStarted
        if now > game.end_time:
            raise golerrors.ApplicationGolAlreadyEnded
        return True
    return application_checks.check(predicate)


def game_has_not_started():
    def predicate(interaction: nextcord.Interaction):
        game = get_game(interaction)
        now = datetime.now()
        if now > game.start_time:
            raise golerrors.ApplicationGolAlreadyStarted
        return True
    return application_checks.check(predicate)
