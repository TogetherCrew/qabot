from enum import Enum

from server.broker import EventBroker


class BotBaseEvent:
    FETCH = "FETCH"


class AnalyzerBaseEvent:
    RUN = "RUN"
    SAVE = "SAVE"
    RUN_ONCE = "RUN_ONCE"


class ServerEvent:
    UPDATE_GUILD = "UPDATE_GUILD"


class DiscordBotEvent:
    FETCH = BotBaseEvent.FETCH
    SEND_MESSAGE = "SEND_MESSAGE"
    FETCH_MEMBERS = "FETCH_MEMBERS"


class DiscordAnalyzerEvent:
    RUN = AnalyzerBaseEvent.RUN  # RECOMPUTE
    RUN_ONCE = AnalyzerBaseEvent.RUN_ONCE
    # SAVE = AnalyzerBaseEvent.SAVE


class Event:
    SERVER_API = ServerEvent
    DISCORD_BOT = DiscordBotEvent
    DISCORD_ANALYZER = DiscordAnalyzerEvent


# class Queue:
#     SERVER_API = Event.SERVER_API
#     DISCORD_BOT = Event.DISCORD_BOT
#     DISCORD_ANALYZER = Event.DISCORD_ANALYZER
#     # TWITTER_BOT = Event.
#     # TWITTER_ANALYZER = "TWITTER_ANALYZER"

class QueueObj(Enum):
    SERVER_API = Event.SERVER_API
    DISCORD_BOT = Event.DISCORD_BOT
    DISCORD_ANALYZER = Event.DISCORD_ANALYZER
    # TWITTER_BOT = Event.TWITTER_BOT
    # TWITTER_ANALYZER = Event.TWITTER_ANALYZER

    def queue(self):
        return self.name


EventBroker.get_queue_by_event("RUN")
EventBroker.get_queue_by_event("UPDATE_GUILD")
EventBroker.get_queue_by_event("SEND_MESSAGE")
EventBroker.get_queue_by_event("FETCH")
