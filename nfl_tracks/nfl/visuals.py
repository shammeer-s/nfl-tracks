import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
from .config import NFLTracksConfig

# The 'field' function remains unchanged.
def field(yard_numbers=True,
          touchdown_markings=True,
          fifty_yard=False,
          fig_size=(12, 6.33)):
    """Generates a plot of a standard American football field."""
    try:
        fig, ax = plt.subplots(1, figsize=fig_size)
        ax.set_xlim(0, 120)
        ax.set_ylim(-5, 58.3)
        ax.axis("off")
        ax.add_patch(patches.Rectangle((0, 0), 120, 53.3, fc='green'))
        ax.add_patch(patches.Rectangle((0, 0), 10, 53.3, fc='darkgreen', zorder=1))
        ax.add_patch(patches.Rectangle((110, 0), 10, 53.3, fc='darkgreen', zorder=1))
        if touchdown_markings:
            ax.text(5, 53.3 / 2, 'Touchdown', ha='center', va='center', fontsize=20, fontweight='bold', color='white', rotation=90)
            ax.text(115, 53.3 / 2, 'Touchdown', ha='center', va='center', fontsize=20, fontweight='bold', color='white', rotation=270)
        for x in range(10, 111, 10):
            ax.plot([x, x], [0, 53.3], color='white', alpha=0.7 if x in [10, 110] else 0.2)
        if fifty_yard:
            ax.plot([60, 60], [0, 53.3], color='gold')
        if yard_numbers:
            for x in range(20, 110, 10):
                yard_num = x if x <= 50 else 120 - x
                ax.text(x, 2, str(yard_num - 10), ha='center', fontsize=10, color='white')
                ax.text(x, 53.3 - 3, str(yard_num - 10), ha='center', fontsize=10, color='white', rotation=180)
        for x in range(11, 110):
            ax.plot([x, x], [0.4, 0.7], color='white')
            ax.plot([x, x], [53.0, 52.5], color='white')
            if x % 5 != 0:
                ax.plot([x, x], [22.91, 23.57], color='white', alpha=0.2)
                ax.plot([x, x], [29.73, 30.39], color='white', alpha=0.2)
        return fig, ax
    except Exception as e:
        print(f"An unexpected error occurred while plotting the field; {e}")


class Play:
    def __init__(self, data: pd.DataFrame, gameId: int, playId: int, config: NFLTracksConfig = NFLTracksConfig()):
        self.config = config
        self.gameId = gameId
        self.playId = playId
        self.data = data[(data[self.config.game_col] == gameId) & (data[self.config.play_col] == playId)].copy()
        if self.data.empty:
            raise ValueError(f"No data found for gameId={gameId} and playId={playId}.")

        self.players = self.data[self.data[self.config.player_id_col].notna()].copy()
        self.ball = self.data[self.data[self.config.player_id_col].isna()].copy()

    def _get_colorized_frame_data(self, frameId: int, highlight_players: list = None, club_colors: dict = None):
        """Internal method to get data for a frame with appropriate colors."""
        frame_data = self.players[self.players[self.config.frame_col] == frameId].copy()

        default_club_colors = {0: "red", 1: "blue"}
        final_colors = {**default_club_colors, **(club_colors or {})}

        # Use the 'player_side_col' (e.g., your 'team' column) for coloring
        frame_data['team_factorized'] = pd.factorize(frame_data[self.config.player_side_col])[0]
        frame_data['plot_color'] = frame_data['team_factorized'].map(final_colors)

        # Only if highlighting is requested, fade the other players to gray
        if highlight_players:
            highlight_mask = frame_data[self.config.player_id_col].isin(highlight_players)
            frame_data.loc[~highlight_mask, 'plot_color'] = 'lightgray'

        return frame_data

    def plot_snap(self, frameId: int,
                  highlight_players: list = None,
                  save: bool = False,
                  filename: str = None,
                  **kwargs):
        """Plots a single snapshot of the play."""
        try:
            fig, ax = field(**kwargs)

            player_data = self._get_colorized_frame_data(frameId, highlight_players, kwargs.get('club_colors'))
            if player_data.empty:
                raise ValueError(f"No player data for frameId={frameId}.")
            ax.scatter(player_data.x, player_data.y, c=player_data['plot_color'], s=kwargs.get('size', 100))

            if not self.ball.empty:
                ball_data = self.ball[self.ball[self.config.frame_col] == frameId]
                ax.scatter(ball_data.x, ball_data.y, c='brown', s=kwargs.get('size', 50) / 2, marker='o')

            if save:
                if filename is None:
                    filename = f"{self.gameId}_{self.playId}_frame_{frameId}.png"
                if not filename.lower().endswith('.png'):
                    filename += '.png'
                fig.savefig(filename, dpi=kwargs.get('dpi', 150), bbox_inches='tight', pad_inches=0.1)
                print(f"Snap saved to {filename}")

            return fig, ax
        except Exception as e:
            print(f"An unexpected error in plot_snap: {e}")

    def animate(self,
                highlight_players: list = None,
                trace_players: list = None,
                track_ball_path: bool = False,
                save: bool = False,
                filename: str = None,
                **kwargs):
        """Animates the play."""
        try:
            fig, ax = field(**kwargs)
            frames = sorted(self.players[self.config.frame_col].unique())

            player_scatter = ax.scatter([], [], s=kwargs.get('size', 30))
            ball_scatter = ax.scatter([], [], s=kwargs.get('size', 50) / 2, c='brown')

            if trace_players:
                for player_id in trace_players:
                    player_path = self.players[self.players[self.config.player_id_col] == player_id]
                    ax.plot(player_path.x, player_path.y, linestyle='--', alpha=0.5, color='red')

            if track_ball_path and not self.ball.empty:
                ax.plot(self.ball.x, self.ball.y, color='brown', linestyle=':', alpha=0.4, label='Ball Path')
                if not ax.get_legend():
                    ax.legend()

            def update(frame_idx):
                frame_id = frames[frame_idx]

                player_data = self._get_colorized_frame_data(frame_id, highlight_players, kwargs.get('club_colors'))
                player_scatter.set_offsets(player_data[['x', 'y']])
                player_scatter.set_color(player_data['plot_color'])

                if not self.ball.empty:
                    ball_data = self.ball[self.ball[self.config.frame_col] == frame_id]
                    if not ball_data.empty:
                        ball_scatter.set_offsets(ball_data[['x', 'y']])

                return player_scatter, ball_scatter

            ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=kwargs.get('speed', 100), blit=True)

            if save:
                if filename is None:
                    filename = f"{self.gameId}_{self.playId}.gif"
                if not filename.lower().endswith('.gif'):
                    filename += '.gif'
                print(f"Saving animation to {filename}...")
                writer = animation.PillowWriter(fps=kwargs.get('fps', 15))
                ani.save(filename, writer=writer)

            return ani
        except Exception as e:
            print(f"An unexpected error in animate: {e}")