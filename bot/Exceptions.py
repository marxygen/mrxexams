class StopBot(Exception):
    """
    The only way to stop PyTelegramBot from polling is to raise an Exception
    SystemExit and KeyboardInterrupt don't work
    """
    def __str__(self):
        return 'Bot has been stopped via /stop command'