import datetime

class Logger:

    @staticmethod
    def log(level, cls, msg):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [{cls}] [{level}] {msg}")

    @staticmethod
    def debug(cls, msg):
        Logger.log("DEBUG", cls, msg)

    @staticmethod
    def info(cls, msg):
        Logger.log("INFO", cls, msg)

    @staticmethod
    def error(cls, msg):
        Logger.log("ERROR", cls, msg)