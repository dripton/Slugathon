class Game:
    """Central class holding information about one game."""

    def __init__(self, name, creator, create_time, start_time, min_players,
      max_players):
        self.name = name
        self.creator = creator
        self.create_time = create_time
        self.start_time = start_time
        self.min_players = min_players
        self.max_players = max_players

