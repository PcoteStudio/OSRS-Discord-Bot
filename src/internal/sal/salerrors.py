import nextcord
from typing import Optional
from nextcord import ApplicationCheckFailure


class ApplicationNoSalSession(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "There is no active SaL session on this server.")


class ApplicationSalNotReady(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "The SaL session is not ready yet. Some configurations are still missing.")


class ApplicationSalNotStarted(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "The SaL event has not started yet.")


class ApplicationSalAlreadyEnded(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "The SaL event has already ended.")


class ApplicationPlayerNotInTeam(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "You are not in any team.")


class ApplicationNotInTeamChannel(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "Team commands should be done in your team's channel.")


class ApplicationSalAlreadyStarted(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "The SaL event has already started.")
