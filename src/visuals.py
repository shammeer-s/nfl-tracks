import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

def field(yard_numbers,
          touchdown_markings,
          fifty_yard,
          fig_size):

    fig, ax = plt.subplots(1, figsize=fig_size)
    ax.set_xlim(0, 120)
    ax.set_ylim(-5, 58.3)
    ax.axis("off")

    # Field
    field = patches.Rectangle((0, 0), 120, 53.3, lw=0.3, ec='black', fc='darkgray')
    ax.add_patch(field)

    # Touchdown Zones
    td_zones = [(0, 'Touchdown', 90), (110, 'Touchdown', 270)]
    for x_pos, label, rotation in td_zones:
        td_zone = patches.Rectangle((x_pos, 0), 10, 53.3, lw=0.1, ec='r', fc='white', alpha=0.2, zorder=0)
        ax.add_patch(td_zone)
        if touchdown_markings:
            ax.text(x_pos + 5, 53.3 / 2, label, ha='center', va='center', fontsize=20, fontweight='bold', color='white', rotation=rotation)

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
        (0.4, 0.7),      # Bottom yard markers
        (53.0, 52.5),    # Top yard markers
        (22.91, 23.57),  # Middle markers (bottom)
        (29.73, 30.39)   # Middle markers (top)
    ]
    for x in x_ranges:
        for y_start, y_end in y_ranges:
            ax.plot([x, x], [y_start, y_end], color='white', alpha=0.2 if (y_start, y_end) in y_ranges[2:] else 1)

    return fig, ax

def snap(data, gameId, playId, frameId,
         yard_numbers = True,
         touchdown_markings = True,
         fifty_yard = False,
         fig_size = (12, 6.33)):

    play = data[(data['gameId'] == gameId) & (data['playId'] == playId) & (data['frameId'] == frameId)]
    fig, ax = field(yard_numbers,
                    touchdown_markings,
                    fifty_yard,
                    fig_size)
    ax.scatter(play.x, play.y, c=pd.factorize(play.club)[0], s=10)
    return fig, ax

def play_game(data, gameId, playId,
         yard_numbers=True,
         touchdown_markings=True,
         fifty_yard=False,
         fig_size=(12, 6.33),
         save=False,
         loop=False,
         **kwargs):

    fig, ax = field(yard_numbers,
                    touchdown_markings,
                    fifty_yard,
                    fig_size)

    # Using boolean indexing to filter the dataframe
    play = data[(data['gameId'] == gameId) & (data['playId'] == playId)]
    play['club'] = pd.factorize(play['club'])[0]

    # Define colors for each club based on the factorized values
    club_colors = {0: "red", 1: "blue", 2: "gray"}
    play['club_color'] = play['club'].map(club_colors)

    # Get unique frames
    frames = sorted(play['frameId'].unique())

    # Initialize scatter plot with empty data
    scatter = ax.scatter([], [], c="gray", s=20)

    # Update function for animation
    def update(frame):
        current_frame = frames[frame]
        current_data = play[play['frameId'] == current_frame]

        # Set data and colors based on current frame
        scatter.set_offsets(current_data[['x', 'y']])
        scatter.set_color(current_data['club_color'])

    # Create the animation
    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=100, repeat=loop)

    if save:
        try:
            default_save_params = {'fps': 15, 'metadata': {'artist': 'Me'}, 'bitrate': 1800}
            if kwargs["save_params"] is None:
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
        except Exception as e:
            print(f"An error occurred while saving the animation; {e}")

    return fig, ax, ani

