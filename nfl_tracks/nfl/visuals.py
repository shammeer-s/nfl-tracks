import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.image as mimage
import matplotlib.font_manager as fm
from io import BytesIO
from PIL import Image
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
import inspect
import urllib.request
from datetime import datetime

from .config import NFLTracksConfig

font_path = '/path/to/your/font/MyCustomFont.ttf'

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams['font.sans-serif'] = ['Tahoma', 'DejaVu Sans',
                               'Lucida Grande', 'Verdana']

def _draw_field_on_axes(ax, yard_numbers=True, touchdown_markings=True, fifty_yard=False):
    """Helper to draw a football field on a given matplotlib Axes object."""
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 53.3)
    ax.axis("off")

    ax.add_patch(patches.Rectangle((0, 0), 120, 53.3, fc='#166f29', zorder=0))
    ax.add_patch(patches.Rectangle((0, 0), 10, 53.3, fc='#0b541c', zorder=1))
    ax.add_patch(patches.Rectangle((110, 0), 10, 53.3, fc='#0b541c', zorder=1))
    if touchdown_markings:
        ax.text(5, 53.3 / 2, 'Touchdown', ha='center', va='center', fontsize=20, fontweight='bold', color='white', rotation=90)
        ax.text(115, 53.3 / 2, 'Touchdown', ha='center', va='center', fontsize=20, fontweight='bold', color='white', rotation=270)

    for x in range(20, 110, 10):
        ax.plot([x, x], [0, 53.3], color='white', alpha=0.7, lw=1)
    if fifty_yard:
        ax.plot([60, 60], [0, 53.3], color='gold', lw=2)

    if yard_numbers:
        for x in range(20, 110, 10):
            yard_num = x if x <= 60 else 120 - x
            ax.text(x-0.6, 3, str(yard_num - 10), ha='center', fontsize=12, color='white')
            ax.text(x-0.6, 53.3 - 3, str(yard_num - 10), ha='center', fontsize=12, color='white', rotation=180)

    for x in range(11, 110):
        ax.plot([x, x], [0.4, 0.7], color='white', lw=1)
        ax.plot([x, x], [53.0, 52.5], color='white', lw=1)
        if x % 5 != 0:
            ax.plot([x, x], [22.91, 23.57], color='white', alpha=0.5, lw=1)
            ax.plot([x, x], [29.73, 30.39], color='white', alpha=0.5, lw=1)

def field(yard_numbers=True, touchdown_markings=True, fifty_yard=False, fig_size=(12, 6.33)):
    """Generates a plot of a standard American football field."""
    fig, ax = plt.subplots(1, figsize=fig_size)
    _draw_field_on_axes(ax, yard_numbers, touchdown_markings, fifty_yard)
    return fig, ax

class Play:
    def __init__(self, data: pd.DataFrame, gameId: int, playId: int, context_data: pd.DataFrame = None, config: NFLTracksConfig = NFLTracksConfig(), ball_image_path: str = None):
        self.config = config
        self.gameId = gameId
        self.playId = playId
        self.data = data[(data[self.config.game_col] == gameId) & (data[self.config.play_col] == playId)].copy()
        if self.data.empty:
            raise ValueError(f"No data found for gameId={gameId} and playId={playId}.")
        self.context_data = context_data
        self.ball_image_path = ball_image_path or "https://i.postimg.cc/c44XYZ8F/ball.png"

    def _get_colorized_frame_data(self, frameId: int, club_colors: dict = None):
        frame_data = self.data[self.data[self.config.frame_col] == frameId].copy()
        default_club_colors = {"Offense": "red", "Defense": "blue"}
        final_colors = {**default_club_colors, **(club_colors or {})}
        frame_data['plot_color'] = frame_data[self.config.player_side_col].map(final_colors)
        return frame_data

    def _split_kwargs(self, kwargs):
        field_args = inspect.signature(field).parameters
        field_kwargs = {k: v for k, v in kwargs.items() if k in field_args}
        other_kwargs = {k: v for k, v in kwargs.items() if k not in field_args}
        return field_kwargs, other_kwargs

    def _determine_highlight_player_id(self, highlight_player_id_arg):
        if highlight_player_id_arg is not None:
            return highlight_player_id_arg

        if 'player_to_predict' in self.data.columns:
            predicted_player_df = self.data[self.data['player_to_predict'] == True]
            if not predicted_player_df.empty:
                return predicted_player_df[self.config.player_id_col].iloc[0]

        return None

    def _draw_ball_image(self, ax):
        ball_x = self.data['ball_land_x'].iloc[0]
        ball_y = self.data['ball_land_y'].iloc[0]
        try:
            if self.ball_image_path.startswith('http'):
                with urllib.request.urlopen(self.ball_image_path) as req:
                    # Read the image data into an in-memory buffer
                    img_data = req.read()
                    img_stream = BytesIO(img_data)
                    img = mimage.imread(img_stream)
            else:
                img = mimage.imread(self.ball_image_path)

            imagebox = OffsetImage(img, zoom=0.05)
            ab = AnnotationBbox(imagebox, (ball_x, ball_y), frameon=False, zorder=5, annotation_clip=False)
            ax.add_artist(ab)
            # ab.set_clip_on(False)
        except Exception as e:
            print(f"Failed to load ball image: {e}")
            ax.scatter(ball_x, ball_y, c='saddlebrown', s=50, marker='o', zorder=5, clip_on=False)


    def _draw_header_and_footer(self, field_ax, context_info):

        # Axes-level Header
        season = context_info.get('season', 'N/A')
        week = context_info.get('week', 'N/A')
        game_date_str = context_info.get('game_date', 'N/A')
        game_time_str = context_info.get('game_time_eastern', 'N/A')

        try:
            game_date = datetime.strptime(game_date_str, '%m/%d/%Y').strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            game_date = game_date_str

        field_ax.text(0, 55.3, f"{self.gameId}    {self.playId}", fontsize=12, color='black')
        field_ax.text(120, 55.3, f"{season} - Week {week}     {game_date}    {game_time_str}", fontsize=12, color='black', ha='right')

        # Axes-level Footer
        play_desc = context_info.get('play_description', 'N/A')
        field_ax.text(60, -3, play_desc, ha='center', fontsize=12, style='italic', color='black',
                      bbox=dict(facecolor='white', alpha=0.5), zorder=6)


    def _draw_scoreboard(self, ax, context):
        """
        Draws the scoreboard with two separate subplots for possession and defense teams.
        """
        # Get the figure from the axes and turn off the main subplot's axis lines
        fig = ax.get_figure()
        ax.axis('off')

        # Create a nested GridSpec to divide the provided subplot into two rows
        gs = GridSpecFromSubplotSpec(2, 1, subplot_spec=ax.get_subplotspec(), hspace=0.1)
        ax_off = fig.add_subplot(gs[0])
        ax_def = fig.add_subplot(gs[1])

        # --- Data Preparation ---
        poss_team = context['possession_team']
        def_team = context['defensive_team']

        if poss_team == context['home_team_abbr']:
            off_score = context['pre_snap_home_score']
            def_score = context['pre_snap_visitor_score']
            off_wp = context['pre_snap_home_team_win_probability']
            def_wp = context['pre_snap_visitor_team_win_probability']
        else:
            off_score = context['pre_snap_visitor_score']
            def_score = context['pre_snap_home_score']
            off_wp = context['pre_snap_visitor_team_win_probability']
            def_wp = context['pre_snap_home_team_win_probability']

        ax_team_board = {
            "ax_off": {
                "obj": ax_off,
                "team": poss_team,
                "score": off_score,
                "wp": off_wp,
                "bg_color": '#ffadad',
                "border_color": 'red',
                "pos": "O"
            },
            "ax_def": {
                "obj": ax_def,
                "team": def_team,
                "score": def_score,
                "wp": def_wp,
                "bg_color": '#a1dbe3',
                "border_color": 'blue',
                "pos": "D"
            }
        }

        # --- Possession Team Box (Top Subplot) ---
        for team in ax_team_board:
            ax_team = ax_team_board[team]
            ax_team_obj = ax_team['obj']
            ax_team_obj.set_xlim(0, 1)
            ax_team_obj.set_ylim(0, 1)
            ax_team_obj.axis('off')

            ax_team_obj.add_patch(patches.Rectangle((0.0, 0), 1, 1, facecolor=ax_team['bg_color'], edgecolor=ax_team['border_color'], lw=1.5))
            ax_team_obj.text(0.1, 0.85, f"Team: {ax_team['team']}", ha='left', color='black', weight='bold', fontsize=12)
            ax_team_obj.text(0.5, 0.45, str(ax_team['score']), ha='center', color='black', fontsize=36)
            ax_team_obj.text(0.5, 0.35, "Score", ha='center', color='black', weight='bold', fontsize=10)
            ax_team_obj.text(0.1, 0.05, f"{ax_team['wp']*100:.0f}%", color='black', fontsize=10)
            ax_team_obj.add_patch(patches.Rectangle((0.8, 0.05), 0.1, 0.1, facecolor='#5e17eb', edgecolor='#ffde59'))
            ax_team_obj.text(0.85, 0.1, ax_team['pos'], ha='center', va='center', fontsize=8, color='white')


    def _draw_player_details(self, ax, player_info):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        ax.add_patch(patches.Rectangle((0, 0), 1, 1, facecolor='lightgray', edgecolor='black', lw=1.5))
        ax.text(0.5, 0.90, "Highlighted", ha='center', weight='bold', fontsize=14)
        ax.text(0.5, 0.83, "Player", ha='center', weight='bold', fontsize=14)

        details = {
            "Name": player_info.get('player_name', 'N/A'),
            "Role": player_info.get('player_role', 'N/A'),
            "Height": player_info.get('player_height', 'N/A'),
            "Weight": player_info.get('player_weight', 'N/A'),
            "DOB": player_info.get('player_birth_date', 'N/A'),
            "Position": player_info.get('player_position', 'N/A')
        }

        y_pos = 0.7
        for key, value in details.items():
            ax.text(0.5, y_pos, f"{key}", weight='bold', fontsize=10, ha="center")
            ax.text(0.5, y_pos-0.04, str(value), fontsize=10, ha="center")
            y_pos -= 0.12


    def _setup_relay_figure(self, highlight_player_id_arg):
        if self.context_data is None:
            raise ValueError("Context data must be provided for relay view.")


        fig = plt.figure(figsize=(22.5, 6), layout='tight')
        gs = GridSpec(1, 3, figure=fig, width_ratios=[2, 12, 2.5], wspace=0.05)

        ax_score = fig.add_subplot(gs[0, 0])
        ax_field = fig.add_subplot(gs[0, 1])
        ax_details = fig.add_subplot(gs[0, 2])

        final_highlight_id = self._determine_highlight_player_id(highlight_player_id_arg)
        context_info = self.context_data[(self.context_data[self.config.game_col] == self.gameId) & (self.context_data[self.config.play_col] == self.playId)].iloc[0]

        # Draw UI elements
        self._draw_header_and_footer(ax_field, context_info)
        self._draw_scoreboard(ax_score, context_info)

        if final_highlight_id:
            player_info_df = self.data[self.data[self.config.player_id_col] == final_highlight_id]
            if not player_info_df.empty:
                self._draw_player_details(ax_details, player_info_df.iloc[0])
        else:
            ax_details.axis('off')

        return fig, ax_field, final_highlight_id

    def plot_snap(self, frameId: int, save: bool = False, filename: str = None, relay: bool = False, highlight_player_id: int = None, **kwargs):
        if not relay:
            field_kwargs, snap_kwargs = self._split_kwargs(kwargs)
            fig, ax = field(**field_kwargs)
            player_data = self._get_colorized_frame_data(frameId, snap_kwargs.get('club_colors'))
            ax.scatter(player_data.x, player_data.y, c=player_data['plot_color'], s=snap_kwargs.get('size', 30), clip_on=False)
            self._draw_ball_image(ax)
        else:
            fig, ax_field, final_highlight_id = self._setup_relay_figure(highlight_player_id)
            field_kwargs, snap_kwargs = self._split_kwargs(kwargs)

            _draw_field_on_axes(ax_field, **field_kwargs)
            player_data = self._get_colorized_frame_data(frameId, snap_kwargs.get('club_colors'))
            ax_field.scatter(player_data.x, player_data.y, c=player_data['plot_color'], s=snap_kwargs.get('size', 30), clip_on=False)

            if final_highlight_id:
                p_info = player_data[player_data[self.config.player_id_col] == final_highlight_id]
                if not p_info.empty:
                    ax_field.scatter(p_info.x, p_info.y, s=100, facecolors='none', edgecolors='yellow', lw=1.5, clip_on=False)

            self._draw_ball_image(ax_field)
            ax = ax_field # for return consistency

        if save:
            fname = filename or f"{self.gameId}_{self.playId}_frame_{frameId}.png"
            fig.savefig(fname, dpi=kwargs.get('dpi', 150), bbox_inches='tight')
            print(f"Snap saved to {fname}")

        return fig, ax

    def animate(self, save: bool = False, filename: str = None, relay: bool = False, highlight_player_id: int = None, **kwargs):
        field_kwargs, animate_kwargs = self._split_kwargs(kwargs)

        if not relay:
            fig, ax = field(**field_kwargs)
            self._draw_ball_image(ax)
            final_highlight_id = self._determine_highlight_player_id(highlight_player_id)
        else:
            fig, ax, final_highlight_id = self._setup_relay_figure(highlight_player_id)
            _draw_field_on_axes(ax, **field_kwargs)
            self._draw_ball_image(ax)

        frames = sorted(self.data[self.config.frame_col].unique())
        marker_size = animate_kwargs.get('size', 30)

        player_scatter = ax.scatter([], [], s=marker_size, zorder=3, clip_on=False)
        highlight_marker = ax.scatter([], [], s=100, facecolors='none', edgecolors='yellow', lw=1.5, zorder=4, clip_on=False)

        def update(frame_idx):
            frame_id = frames[frame_idx]
            player_data = self._get_colorized_frame_data(frame_id, animate_kwargs.get('club_colors'))
            player_scatter.set_offsets(player_data[['x', 'y']])
            player_scatter.set_color(player_data['plot_color'])

            elements = [player_scatter]

            if final_highlight_id:
                p_info = player_data[player_data[self.config.player_id_col] == final_highlight_id]
                if not p_info.empty:
                    highlight_marker.set_offsets(p_info[['x', 'y']])
                elements.append(highlight_marker)

            return tuple(elements)

        ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=animate_kwargs.get('speed', 100), blit=True)

        if save:
            fname = filename or f"Anim_{self.gameId}_{self.playId}.gif"
            writer = animation.PillowWriter(fps=animate_kwargs.get('fps', 15))
            ani.save(fname, writer=writer)
            print(f"Animation saved to {fname}")

        return ani

