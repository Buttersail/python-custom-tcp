import re

class CounterUtils:
    def parse_counter(msg):
        match = re.search("^\w+-(\d+)", msg)
        if match:
            return int(match.group(1))
        else:
            return 0

    def parse_and_increment_counter(msg):
        return CounterUtils.parse_counter(msg) + 1

