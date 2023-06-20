import nextcord
from typing import Optional
from nextcord import ApplicationCheckFailure


class ApplicationNoGolSession(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "There is no active GoL session on this server.")


class ApplicationGolNotReady(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "The GoL session is not ready yet. Some configurations are still missing.")


class ApplicationGolNotStarted(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "The GoL event has not started yet.")


class ApplicationGolAlreadyEnded(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "The GoL event has already ended.")


class ApplicationPlayerNotInTeam(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "You are not in any team.")


class ApplicationNotInTeamChannel(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "Team commands should be done in your team's channel.")


class ApplicationGolAlreadyStarted(ApplicationCheckFailure):
    def __init__(self, message: Optional[str] = None) -> None:
        super().__init__(message or "The GoL event has already started.")
