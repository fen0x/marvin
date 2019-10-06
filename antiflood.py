"""
Antiflood functions.

Associate a timestamp and a counter to every user. When the counter exceeds the
message limit inside the allowed timeframe, it is marked as "flooding".

Since the timespan of flooding user is short enough, no persistent storage is
keeped.
"""
from datetime import datetime, timedelta

class Antiflood():
    # dict containing user_id as keys
    # values are dict in the form { begin: datetime, counter: int }
    _flood_data = {}


    def is_flooding(self, user_id):
        """
        is_flooding returns a boolean indicating if the specified user is flooding.
        This function must be called every time an user sends a message.

        If the user is not flooding, it's counter is incremented accordingly.
        """
        if user_id not in self._flood_data:
            # initial condition
            self._init_user(user_id)
            return False

        if not is_in_timeframe(self._flood_data[user_id]["begin"], self.time_limit):
            # user was present but last activity was too old
            self._init_user(user_id)
            return False

        self._flood_data[user_id]["counter"] += 1
        return self._flood_data[user_id]["counter"] >= self.count_limit

    def _init_user(self, user_id):
        self._flood_data[user_id] = dict(begin=datetime.now(), counter=1)

    def __init__(self, time_limit, count_limit):
        self.time_limit = time_limit
        self.count_limit = count_limit


def is_in_timeframe(start, seconds_from_now):
    """
    is_in_timeframe returns True if start date is less than seconds_from_now
    seconds in the past.
    """
    return datetime.now() - start < timedelta(seconds=seconds_from_now)
