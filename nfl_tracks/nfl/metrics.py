import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist

from .config import NFLTracksConfig

def calculate_separation(play_data: pd.DataFrame, config: NFLTracksConfig):
    """
    Calculates the distance between each offensive player and their nearest defender for each frame.

    This is a key metric for evaluating receiver route running and defensive coverage. It uses scipy's
    efficient cdist function to compute the pairwise distances between all offensive and defensive players.

    Returns:
        pd.DataFrame: A DataFrame containing frame-by-frame separation data for each offensive player.
    """
    separation_data = []
    for frame_id in sorted(play_data[config.frame_col].unique()):
        frame_df = play_data[play_data[config.frame_col] == frame_id]
        offense_df = frame_df[frame_df[config.player_side_col] == 'Offense']
        defense_df = frame_df[frame_df[config.player_side_col] == 'Defense']

        if offense_df.empty or defense_df.empty:
            continue

        distances = cdist(offense_df[['x', 'y']], defense_df[['x', 'y']])

        min_distances = np.min(distances, axis=1)

        for i, player_id in enumerate(offense_df[config.player_id_col]):
            separation_data.append({
                config.game_col: play_data[config.game_col].iloc[0],
                config.play_col: play_data[config.play_col].iloc[0],
                config.frame_col: frame_id,
                config.player_id_col: player_id,
                'separation': min_distances[i]
            })

    return pd.DataFrame(separation_data)

def get_play_speed_stats(play_data: pd.DataFrame, config: NFLTracksConfig):
    """
    Calculates the maximum and average speed for each player within a single play.
    """
    speed_stats = play_data.groupby(config.player_id_col)['s'].agg(['max', 'mean']).reset_index()
    speed_stats = speed_stats.rename(columns={'max': 'max_speed', 'mean': 'avg_speed'})

    player_info = play_data[[config.player_id_col, 'player_name']].drop_duplicates()
    speed_stats = pd.merge(speed_stats, player_info, on=config.player_id_col)

    return speed_stats

def get_total_distance_traveled(play_data: pd.DataFrame, config: NFLTracksConfig):
    """
    Calculates the total distance covered by each player during a play.
    """
    distance_data = []
    for player_id in play_data[config.player_id_col].unique():
        player_df = play_data[play_data[config.player_id_col] == player_id].sort_values(by=config.frame_col)
        diffs = np.diff(player_df[['x', 'y']].values, axis=0)
        total_distance = np.sum(np.sqrt(np.sum(diffs**2, axis=1)))

        distance_data.append({
            config.player_id_col: player_id,
            'total_distance': total_distance
        })

    distance_df = pd.DataFrame(distance_data)
    player_info = play_data[[config.player_id_col, 'player_name']].drop_duplicates()
    distance_df = pd.merge(distance_df, player_info, on=config.player_id_col)

    return distance_df
