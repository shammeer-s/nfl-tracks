import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from . import visuals
from .config import NFLTracksConfig


def plot_separation_over_time(separation_df: pd.DataFrame, target_receiver_id: int, config: NFLTracksConfig):
    """
    Generates a line plot showing a receiver's separation from the nearest defender over the play.
    This helps in analyzing how well a receiver creates space during their route.
    """
    receiver_sep = separation_df[separation_df[config.player_id_col] == target_receiver_id]

    if receiver_sep.empty:
        print(f"No separation data found for player {target_receiver_id}")
        return

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(receiver_sep[config.frame_col], receiver_sep['separation'], marker='o', linestyle='-')

    ax.set_title(f'Receiver Separation Over Time (Player ID: {target_receiver_id})')
    ax.set_xlabel('Frame ID')
    ax.set_ylabel('Separation from Nearest Defender (Yards)')
    ax.grid(True)
    plt.show()

def plot_play_max_speeds(speed_stats_df: pd.DataFrame):
    """
    Creates a horizontal bar plot to compare the maximum speeds achieved by players during a play.
    """
    if speed_stats_df.empty:
        print("Speed stats DataFrame is empty.")
        return

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 8))

    sorted_df = speed_stats_df.sort_values(by='max_speed', ascending=False)

    sns.barplot(x='max_speed', y='player_name', data=sorted_df, ax=ax, palette='viridis')

    ax.set_title('Maximum Player Speeds During Play')
    ax.set_xlabel('Max Speed (yards/second)')
    ax.set_ylabel('Player Name')
    plt.tight_layout()
    plt.show()

def plot_all_routes(play_data: pd.DataFrame, config: NFLTracksConfig):
    """
    Overlays the routes of all offensive players on a single football field diagram.
    This provides a clear view of the route combination for a given play.
    """
    fig, ax = visuals.field()

    offense_df = play_data[play_data[config.player_side_col] == 'Offense']

    # Use a color palette to distinguish routes
    palette = sns.color_palette('bright', n_colors=offense_df[config.player_id_col].nunique())

    for i, player_id in enumerate(offense_df[config.player_id_col].unique()):
        player_route = offense_df[offense_df[config.player_id_col] == player_id].sort_values(by=config.frame_col)
        ax.plot(player_route['x'], player_route['y'], color=palette[i], linestyle='-', label=player_route['player_name'].iloc[0])

    ax.set_title('Offensive Player Routes')
    # Place legend outside the plot
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()
