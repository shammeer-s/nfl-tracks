import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

from .config import NFLTracksConfig


def field(yard_numbers=True,
          touchdown_markings=True,
          fifty_yard=False,
          fig_size=(12, 6.33)):
    try:
        # Plot
        fig, ax = plt.subplots(1, figsize=fig_size)
        ax.set_xlim(0, 120)
        ax.set_ylim(-5, 58.3)
        ax.axis("off")

        # Field
        field = patches.Rectangle((0, 0), 120, 53.3, fc='green')
        ax.add_patch(field)

        # Touchdown Zones
        td_zones = [(0, 'Touchdown', 90), (110, 'Touchdown', 270)]
        for x_pos, label, rotation in td_zones:
            td_zone = patches.Rectangle((x_pos, 0), 10, 53.3, fc='darkgreen', zorder=1)
            ax.add_patch(td_zone)
            if touchdown_markings:
                ax.text(x_pos + 5, 53.3 / 2, label, ha='center', va='center', fontsize=20, fontweight='bold',
                        color='white', rotation=rotation)

        # Yard Lines and 50-yard line
        for x in range(10, 111, 10):
            ax.plot([x, x], [0, 53.3], color='white', alpha=0.7 if x in [10, 110] else 0.2)
        if fifty_yard:
            ax.plot([60, 60], [0, 53.3], color='gold')

        # Yard Numbers
        if yard_numbers:
            for x in range(20, 110, 10):
                yard_num = x if x <= 50 else 120 - x
                ax.text(x, 2, str(yard_num - 10), ha='center', fontsize=10, color='white')
                ax.text(x, 53.3 - 3, str(yard_num - 10), ha='center', fontsize=10, color='white', rotation=180)

        # Yard Line Markers
        x_ranges = range(11, 110)
        y_ranges = [
            (0.4, 0.7),  # Bottom yard markers
            (53.0, 52.5),  # Top yard markers
            (22.91, 23.57),  # Middle markers (bottom)
            (29.73, 30.39)  # Middle markers (top)
        ]
        for x in x_ranges:
            for y_start, y_end in y_ranges:
                ax.plot([x, x], [y_start, y_end], color='white', alpha=0.2 if (y_start, y_end) in y_ranges[2:] else 1)

        return fig, ax
    except Exception as e:
        print(f"An unexpected error occurred while plotting the field; {e}")


def snap(data, gameId, playId, frameId,
         config=NFLTracksConfig(),
         yard_numbers=True,
         touchdown_markings=True,
         fifty_yard=False,
         fig_size=(12, 6.33),
         **kwargs):
    try:
        fig, ax = field(yard_numbers,
                        touchdown_markings,
                        fifty_yard,
                        fig_size)

        play = data[(data[config.game_col] == gameId) &
            (data[config.play_col] == playId) &
            (data[config.frame_col] == frameId)]

        if play.empty:
            if gameId not in data[config.game_col].values:
                raise ValueError(f"The value gameId={gameId} is not present in the data.")
            if playId not in data[config.play_col].values:
                raise ValueError(f"The value playId={playId} is not present in the data.")
            if frameId not in data[config.frame_col].values:
                raise ValueError(f"The value frameId={frameId} is not present in the data.")
            raise ValueError(f"No data found for gameId={gameId} and playId={playId} and frameId={frameId}.")

        if "size" not in kwargs:
            size = 10
        else:
            size = kwargs["size"]

        # Define colors for each club based on the factorized values
        try:
            default_club_colors = {0: "red", 1: "blue", 2: "yellow"}

            club_colors = kwargs.get("club_colors", default_club_colors)
            club_colors = {**default_club_colors, **club_colors}

            play = play.copy()
            play['club'] = pd.factorize(play['club'])[0]
            play['club_colors'] = play['club'].map(club_colors)

            # Check if any club value is mapped to an invalid color
            if play['club_colors'].isnull().any():
                missing_clubs = play.loc[play['club_colors'].isnull(), 'club'].unique()
                raise ValueError(f"The following club values are not mapped to a valid color: {missing_clubs}")

        except ValueError as ve:
            print(
                "An error occurred while coloring the plot using the parameters provided. Please refer matplotlib colors for valid values. "
                f"{ve}")

        ax.scatter(play.x, play.y, c=play['club_colors'], s=size)
        return fig, ax
    except Exception as e:
        print(f"An unexpected error occurred while plotting the snap of the play; {e}")


def play_game(data, gameId, playId,
              config=NFLTracksConfig(),
              kaggle=True,
              yard_numbers=True,
              touchdown_markings=True,
              fifty_yard=False,
              fig_size=(12, 6.33),
              save=False,
              loop=False,
              **kwargs):
    try:

        if kaggle:
            matplotlib.rc('animation', html='jshtml')

        fig, ax = field(yard_numbers,
                        touchdown_markings,
                        fifty_yard,
                        fig_size)

        # Using boolean indexing to filter the dataframe
        play = data[(data[config.game_col] == gameId) &
                    (data[config.play_col] == playId)]

        if play.empty:
            if gameId not in data[config.game_col].values:
                raise ValueError(f"The value gameId={gameId} is not present in the data.")
            if playId not in data[config.play_col].values:
                raise ValueError(f"The value playId={playId} is not present in the data.")
            raise ValueError(f"No data found for gameId={gameId} and playId={playId}.")

        # Define colors for each club based on the factorized values
        try:
            default_club_colors = {0: "red", 1: "blue", 2: "yellow"}

            club_colors = kwargs.get("club_colors", default_club_colors)
            club_colors = {**default_club_colors, **club_colors}

            play = play.copy()
            play['club'] = pd.factorize(play['club'])[0]
            play['club_colors'] = play['club'].map(club_colors)

            # Check if any club value is mapped to an invalid color
            if play['club_colors'].isnull().any():
                missing_clubs = play.loc[play['club_colors'].isnull(), 'club'].unique()
                raise ValueError(f"The following club values are not mapped to a valid color: {missing_clubs}")

        except ValueError as ve:
            print(
                "An error occurred while coloring the plot using the parameters provided. Please refer matplotlib colors for valid values. "
                f"{ve}")

        # Get unique frames
        frames = sorted(play[config.play_col].unique())

        if "size" not in kwargs:
            size = 10
        else:
            size = kwargs["size"]
        # Initialize scatter plot with empty data
        scatter = ax.scatter([], [], c="gray", s=size)

        # Update function for animation
        def update(frame):
            current_frame = frames[frame]
            current_data = play[play[config.play_col] == current_frame]

            # Set data and colors based on current frame
            scatter.set_offsets(current_data[['x', 'y']])
            scatter.set_color(current_data['club_colors'])

        if "speed" not in kwargs:
            interval = 100
        else:
            interval = kwargs["speed"]

        # Create the animation
        ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=interval, repeat=loop)

        if save:
            try:
                default_save_params = {'fps': 15, 'metadata': {'artist': 'Me'}, 'bitrate': 1800}
                if "save_params" not in kwargs:
                    save_params = default_save_params
                else:
                    save_params = {**default_save_params, **kwargs["save_params"]}

                writer = animation.PillowWriter(**save_params)
                ani.save('play.gif', writer=writer)
            except ValueError as ve:
                print("An error occurred while saving the animation; Pillow writer only accepts a handful of known "
                      "parameters, recheck the parameter and compare with the documentation "
                      "(https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.PillowWriter.html#matplotlib.animation.PillowWriter) "
                      f"{ve}")
        if kaggle:
            plt.close()
        return ani
    except Exception as e:
        print(f"An unexpected error occurred while playing the animation; {e}")