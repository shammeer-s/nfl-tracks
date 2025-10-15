# nfl-tracks

`nfl-tracks` is a Python library built on top of Matplotlib for creating insightful and customizable visualizations of NFL player tracking data. Designed with the NFL Big Data Bowl in mind, it provides a simple interface to plot static plays, generate dynamic animations, and view detailed, context-rich breakdowns of individual plays.

## Key Features
* Standard Field Visualization: Generate a regulation NFL field with customizable markings.
* Single Frame Plotting: Visualize player positions at any specific moment in a play.
* Dynamic Animations: Create smooth, animated GIFs or videos of entire plays.
* "Relay" Dashboard View: A comprehensive visualization that includes:
  * Live scoreboard with team details and win probabilities.
  * Highlighted player card with key stats (name, position, height, etc.).
  * On-field play and game context.
  * Automatic highlighting of the targeted or predicted player.
* Kaggle Notebook Compatibility: Easily render animations directly within Kaggle notebooks.
* Out-of-Bounds Tracking: Players and the ball are visualized even when they go outside the field of play, without distorting the field's proportions.

## Installation
You can install nfl-tracks using pip:
```bash
pip install nfl_tracks
```

## Function Overview
The core of the library is the visuals.Play class, which you initialize once for a specific play. You can then call its methods to generate different visualizations.

Initialization of a visualization object for a specific play. This is the first step before you can plot or animate anything.

* data (pd.DataFrame): The main tracking data.
* gameId (int): The unique identifier for the game.
* playId (int): The identifier for the play.
* context_data (pd.DataFrame): The supplementary data containing game and play context.

```python
# Data Preparation
import pandas as pd
from nfl import visuals

tracking_data = pd.read_csv(f'data/train/input_2023_w02.csv')
context_data = pd.read_csv(f'data/supplementary_data.csv', dtype={25: str})

data = tracking_data[(tracking_data['game_id'] == 2023091400) & (tracking_data['play_id'] == 3438)]
```

```python
play = visuals.Play(data, gameId, playId, context_data)
```

### plot_snap

This is useful for analyzing player formations and positions at a key moment, like the snap or the moment a pass is thrown.

**Standard View (`relay=False`)** <br>
This is the default mode. It generates a clean and simple plot of the football field with the players' positions.

```python
# Plots frame 10 of the play on a standard field
fig, ax = play.plot_snap(frameId=10)
plt.show()
```
![plot_snap](https://raw.githubusercontent.com/shammeer-s/nfl-tracks/refs/heads/master/outputs/snap.png)


**Relay Dashboard View (`relay=True`)** <br>
This mode creates a rich, informational dashboard around the field, providing deep context for the play. It includes a scoreboard, game information, and a detailed card for a highlighted player.

```python
# Plots frame 10 using the advanced relay dashboard
fig, ax = play.plot_snap(frameId=10, relay=True)
plt.show()
```
![plot_snap](https://raw.githubusercontent.com/shammeer-s/nfl-tracks/refs/heads/master/outputs/snap_relay.png)

### play.animate

Generates a full animation of the play from the first frame to the last. This is the best way to see a play unfold, showing player routes and movements in real-time.

**Standard Animation (`relay=False`)** <br>
This creates a simple, clean animation of the players moving on the field. It's great for embedding in presentations or for a quick look at the play's dynamics.

```python
# Generates a standard animation of the play
# Use kaggle=True to display it in a notebook
standard_animation = play.animate(kaggle=True)
standard_animation
```
![animate](https://raw.githubusercontent.com/shammeer-s/nfl-tracks/refs/heads/master/outputs/animate.gif)

**Relay Dashboard Animation (`relay=True`)** <br>
This creates a simple, clean animation of the players moving on the field. It's great for embedding in presentations or for a quick look at the play's dynamics.

```python
# Generates a relay dashboard animation of the play
relay_animation = play.animate(relay=True, kaggle=True)
relay_animation
```
![animate](https://raw.githubusercontent.com/shammeer-s/nfl-tracks/refs/heads/master/outputs/animate_relay.gif)

Additional Parameters (`**kwargs`)
You can customize your plots and animations with these optional arguments:

* `highlight_player_id` (int): Manually specify an `nfl_id` to highlight in the relay view. If not provided, it defaults to the player with `player_to_predict=True`.
* `club_colors` (dict): A dictionary to override default offense/defense colors (e.g., `{'Offense': '#006400', 'Defense': '#8B0000'}`).
* `size` (int): The marker size for players on the field.
* `speed` (int): The delay between frames in milliseconds for animations (a lower number is faster).


## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/shammeer-s/nfl/blob/master/LICENSE) file for details.

---
This library is ideal for visualizing football plays with clear, customizable graphics and animations. For further assistance, refer to Matplotlib's documentation or provide specific details for troubleshooting.