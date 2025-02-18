from datetime import timezone, datetime
from src.hotp import Hotp

class Totp:
    def __init__(self, secret, algorithm="sha1", time_step=30):
        self.hotp = Hotp(secret)
        self.time_step = time_step
        self.algorithm = algorithm

    def generate_code(self, current_timestamp):
        current_timestamp = current_timestamp or int(datetime.now(tz=timezone.utc).timestamp())

        t = int(current_timestamp / self.time_step)
        return self.hotp.generate_code(t)
