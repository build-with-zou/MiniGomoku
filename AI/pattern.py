# File name: pattern.py
# Content : Pattern recognition for Gomoku game
class Pattern:
    """A class to contain all patterns for Gomoku game"""
    def __init__(self, player,weights = None):
        self.player = player
        self.opponent = 2 if player == 1 else 1
        self.defensive_weight = 0.5  # Default defensive weight, can be adjusted by genetic algorithm
        if weights is not None:
            self.set_weights(weights)
        if self.player == 1:
            self.pattern = {
                '0110': '活二',
                '01110': '活三',
                '011110': '活四',
                '01010': '跳二',
                '011010': '跳三',
                '010110': '跳三',
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
                '02020': '跳二',
                '022020': '跳三',
                '020220': '跳三',
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
                '02020': '跳二',
                '022020': '跳三',
                '020220': '跳三',
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
                '01010': '跳二',
                '011010': '跳三',
                '010110': '跳三',
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
                '跳二': 5,
                '活三': 1000,
                '跳三': 500,
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
        
    def set_weights(self, chromosome):
        """
        Set the pattern list for the given player based on the chromosome
        0-5: potential pattern scores
        6-8: sleep pattern scores
        9: defense_weight
        """
        self.pattern_score = {
            'potential': {
                '活二': chromosome[0], '跳二': chromosome[1],
                '活三': chromosome[2], '跳三': chromosome[3],
                '活四': chromosome[4], '五': chromosome[5]
            },
            'sleep': {
                '眠二': chromosome[6], '眠三': chromosome[7], '眠四': chromosome[8]
            }
        }
        if len(chromosome) > 9:
            self.defense_weight = chromosome[9]
        