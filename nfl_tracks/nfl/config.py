class NFLTracksConfig:
    """
    A configuration class to manage column mappings for the nfl_tracks library.
    """
    def __init__(self,
                 game_col='game_id',
                 play_col='play_id',
                 frame_col='frame_id',
                 player_id_col='nfl_id',
                 player_side_col='player_side',
        ):
        """
        Initializes the configuration with specified or default column names.
        According to the NFL Big Data Bowl 2026 dataset.
        """
        self.game_col = game_col
        self.play_col = play_col
        self.frame_col = frame_col
        self.player_id_col = player_id_col
        self.player_side_col = player_side_col
