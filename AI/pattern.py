# File name: pattern.py
# Content : Pattern recognition for Gomoku game
class Pattern:
    """A class to contain all patterns for Gomoku game"""
    def __init__(self, player):
        self.player = player
        self.opponent = 2 if player == 1 else 1
        
        if self.player == 1:
            self.pattern = {
                '0110': '活二',
                '01110': '活三',
                '011110': '活四',
                '2110': '眠二',
                '0112': '眠二',
                '21110': '眠三',
                '01112': '眠三',
                '211110': '眠四',
                '011112': '眠四',
                '11111': '五',
            }
            self.opponent_pattern = {
                '0220': '活二',
                '02220': '活三',
                '022220': '活四',
                '1220': '眠二',
                '0221': '眠二',
                '12220': '眠三',
                '02221': '眠三',
                '122220': '眠四',
                '022221': '眠四',
                '22222': '五',
            }
        else:
            self.pattern = {
                '0220': '活二',
                '02220': '活三',
                '022220': '活四',
                '1220': '眠二',
                '0221': '眠二',
                '12220': '眠三',
                '02221': '眠三',
                '122220': '眠四',
                '022221': '眠四',
                '22222': '五',
            }
            self.opponent_pattern = {
                '0110': '活二',
                '01110': '活三',
                '011110': '活四',
                '2110': '眠二',
                '0112': '眠二',
                '21110': '眠三',
                '01112': '眠三',
                '211110': '眠四',
                '011112': '眠四',
                '11111': '五',
            }
        self.pattern_score = {
            "potential": {
                '活二': 10,
                '活三': 1000,
                '活四': 10000,
                '五': 10000,
            },
            "sleep": {
                '眠二': 5,
                '眠三': 50,
                '眠四': 2000,
            }
        }

    def get_pattern(self,player):
        """Return the pattern dictionary for the given player"""
        if player == self.player:
            return self.pattern
        else:
            return self.opponent_pattern