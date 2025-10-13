import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import inspect

from .config import NFLTracksConfig
from .metrics import calculate_separation, get_play_speed_stats, get_total_distance_traveled


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

        # Field and touchdown zones
        ax.add_patch(patches.Rectangle((0, 0), 120, 53.3, fc='green'))
        ax.add_patch(patches.Rectangle((0, 0), 10, 53.3, fc='darkgreen', zorder=1))
        ax.add_patch(patches.Rectangle((110, 0), 10, 53.3, fc='darkgreen', zorder=1))
        if touchdown_markings:
            ax.text(5, 53.3 / 2, 'Touchdown', ha='center', va='center', fontsize=20, fontweight='bold', color='white', rotation=90)
            ax.text(115, 53.3 / 2, 'Touchdown', ha='center', va='center', fontsize=20, fontweight='bold', color='white', rotation=270)

        # Yard lines
        for x in range(10, 111, 10):
            ax.plot([x, x], [0, 53.3], color='white', alpha=0.7 if x in [10, 110] else 0.2)
        if fifty_yard:
            ax.plot([60, 60], [0, 53.3], color='gold')

        # Yard numbers
        if yard_numbers:
            for x in range(20, 110, 10):
                yard_num = x if x <= 50 else 120 - x
                ax.text(x, 2, str(yard_num - 10), ha='center', fontsize=10, color='white')
                ax.text(x, 53.3 - 3, str(yard_num - 10), ha='center', fontsize=10, color='white', rotation=180)

        # Hash marks
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
    def __init__(self, data: pd.DataFrame, gameId: int, playId: int, context_data: pd.DataFrame = None, config: NFLTracksConfig = NFLTracksConfig()):
        self.config = config
        self.gameId = gameId
        self.playId = playId

        # Filter for the specific play, ensuring we have a clean copy
        self.data = data[(data[self.config.game_col] == gameId) & (data[self.config.play_col] == playId)].copy()
        if self.data.empty:
            raise ValueError(f"No data found for gameId={gameId} and playId={playId}.")

        # Store context data if provided, for use with the relay feature
        self.context_data = context_data

        # We will handle ball and players within the plotting functions
        # This simplifies logic and avoids issues with data separation

    def _get_colorized_frame_data(self, frameId: int, highlight_players: list = None, club_colors: dict = None):
        """Internal method to get data for a frame with appropriate colors."""
        frame_data = self.data[self.data[self.config.frame_col] == frameId].copy()

        # Define default colors and merge with user-provided colors
        default_club_colors = {"Offense": "red", "Defense": "blue"}
        final_colors = {**default_club_colors, **(club_colors or {})}

        # Map player side to colors
        frame_data['plot_color'] = frame_data[self.config.player_side_col].map(final_colors)

        # Handle highlighting if requested
        if highlight_players:
            highlight_mask = frame_data[self.config.player_id_col].isin(highlight_players)
            frame_data.loc[~highlight_mask, 'plot_color'] = 'lightgray'

        return frame_data

    def _split_kwargs(self, kwargs):
        """Splits kwargs into those for field() and others."""
        field_args = inspect.signature(field).parameters
        field_kwargs = {k: v for k, v in kwargs.items() if k in field_args}
        other_kwargs = {k: v for k, v in kwargs.items() if k not in field_args}
        return field_kwargs, other_kwargs

    def plot_snap(self, frameId: int,
                  highlight_players: list = None,
                  save: bool = False,
                  filename: str = None,
                  **kwargs):
        """Plots a single snapshot of the play."""
        try:
            field_kwargs, snap_kwargs = self._split_kwargs(kwargs)
            fig, ax = field(**field_kwargs)

            player_data = self._get_colorized_frame_data(frameId, snap_kwargs.get('club_colors'))
            if player_data.empty:
                raise ValueError(f"No player data for frameId={frameId}.")

            # Use marker size from kwargs, with a default of 100
            marker_size = snap_kwargs.get('size', 30)
            ax.scatter(player_data.x, player_data.y, c=player_data['plot_color'], s=marker_size)

            # Plot the static ball landing position
            # Get the ball landing coordinates from the first row of the play data
            ball_x = self.data['ball_land_x'].iloc[0]
            ball_y = self.data['ball_land_y'].iloc[0]
            ax.scatter(ball_x, ball_y, c='darkgoldenrod', s=marker_size, marker='o', zorder=5) # Ensure ball is on top

            if save:
                if filename is None:
                    filename = f"{self.gameId}_{self.playId}_frame_{frameId}.png"
                if not filename.lower().endswith('.png'):
                    filename += '.png'
                fig.savefig(filename, dpi=snap_kwargs.get('dpi', 150), bbox_inches='tight', pad_inches=0.1)
                print(f"Snap saved to {filename}")

            return fig  , ax
        except Exception as e:
            print(f"An unexpected error in plot_snap: {e}")

    def animate(self,
                trace_players: list = None,
                save: bool = False,
                filename: str = None,
                relay: bool = False,
                targeted_receiver_id: int = None,
                **kwargs):
        try:
            field_kwargs, animate_kwargs = self._split_kwargs(kwargs)
            fig, ax = field(**field_kwargs)
            frames = sorted(self.data[self.config.frame_col].unique())
            marker_size = animate_kwargs.get('size', 30)

            # Plot static ball position
            ball_x = self.data['ball_land_x'].iloc[0]
            ball_y = self.data['ball_land_y'].iloc[0]
            ax.scatter(ball_x, ball_y, c='darkgoldenrod', s=marker_size, marker='o', zorder=5)

            # Initialize player scatter plot
            player_scatter = ax.scatter([], [], s=marker_size)

            if trace_players:
                for player_id in trace_players:
                    player_path = self.data[self.data[self.config.player_id_col] == player_id]
                    ax.plot(player_path.x, player_path.y, linestyle='--', alpha=0.5)

            # --- Conditional Relay vs. Simple Animation ---
            if relay:
                if self.context_data is None:
                    raise ValueError("Context data must be provided when relay=True.")

                context_info_df = self.context_data[(self.context_data[self.config.game_col] == self.gameId) & (self.context_data[self.config.play_col] == self.playId)]
                context_info = context_info_df.iloc[0] if not context_info_df.empty else None

                separation_df = calculate_separation(self.data, self.config)
                live_text = ax.text(2, 55, '', color='white', fontsize=9, va='top', bbox=dict(boxstyle='round,pad=0.5', fc='black', alpha=0.6))
                receiver_marker = ax.scatter([], [], s=marker_size*2.5, facecolors='none', edgecolors='yellow', lw=2, zorder=4) if targeted_receiver_id else None

                def update(frame_idx):
                    frame_id = frames[frame_idx]
                    player_data = self._get_colorized_frame_data(frame_id, animate_kwargs.get('club_colors'))
                    player_scatter.set_offsets(player_data[['x', 'y']])
                    player_scatter.set_color(player_data['plot_color'])

                    display_text = f"Game: {self.gameId} | Play: {self.playId}\nFrame: {frame_id}"
                    if context_info is not None:
                        display_text += f"\n{context_info['down']} & {context_info['yards_to_go']} | Q{context_info['quarter']} | {context_info['game_clock']}"

                    updated_elements = [player_scatter, live_text]
                    if targeted_receiver_id:
                        receiver_data = player_data[player_data[self.config.player_id_col] == targeted_receiver_id]
                        if not receiver_data.empty:
                            receiver_marker.set_offsets(receiver_data[['x', 'y']])

                        current_sep = separation_df[(separation_df[self.config.frame_col] == frame_id) & (separation_df[self.config.player_id_col] == targeted_receiver_id)]
                        if not current_sep.empty:
                            sep_val = current_sep['separation'].iloc[0]
                            display_text += f"\nTarget Sep: {sep_val:.2f} yds"
                        updated_elements.append(receiver_marker)

                    live_text.set_text(display_text)
                    return tuple(filter(None, updated_elements))

            else:  # Original simple animation
                def update(frame_idx):
                    frame_id = frames[frame_idx]
                    player_data = self._get_colorized_frame_data(frame_id, animate_kwargs.get('club_colors'))
                    player_scatter.set_offsets(player_data[['x', 'y']])
                    player_scatter.set_color(player_data['plot_color'])
                    return player_scatter,

            # Create and save the animation
            ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=animate_kwargs.get('speed', 100), blit=True)

            if save:
                if filename is None:
                    filename = f"Anim{self.gameId}{self.playId}.gif"
                if not filename.lower().endswith('.gif'):
                    filename += '.gif'
                print(f"Saving animation to {filename}...")
                writer = animation.PillowWriter(fps=animate_kwargs.get('fps', 15))
                ani.save(filename, writer=writer)
                print(f"Animation saved successfully to {filename}.")

            return ani
        except Exception as e:
            print(f"An unexpected error in animate: {e}")