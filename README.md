# NFL Play Visualizer

This Python script provides tools for visualizing NFL play data on a football field. Using `matplotlib`, it creates static snapshots and animated plays of NFL games based on tracking data.

## Requirements

- Python 3.x
- pandas
- matplotlib

To install the dependencies:

```bash
pip install nfl
```

After successfully installing the nfl package, import it in the file using the code below:```python
```python
# Import nfl
from nfl import visuals
```
## Overview

### The script contains three main functions:

1. **field**: Sets up the visual representation of a football field.
2. **snap**: Creates a static snapshot of a specific play frame.
3. **play_game**: Animates a play, showing player movements across frames.

Individual functions are listed below.

---
## _field()_
This function sets up the football field with customizable features, such as yard numbers, touchdown markings, and a highlighted 50-yard line.

```pythonverboseregexp
visuals.field(yard_numbers, touchdown_markings, fifty_yard, fig_size)
```

#### Parameters:
* **yard_numbers (bool)**: Whether to display yard numbers. Default is True.
* **touchdown_markings (bool)**: Whether to display touchdown markings. Default is True.
* **fifty_yard (bool)**: Whether to highlight the fifty-yard line. Default is False.
* **fig_size (tuple)**: The size of the figure in inches. Default is (12, 6.33).

#### Returns:
* **fig (matplotlib.figure.Figure)**: The figure object containing the field.
* **ax (matplotlib.axes._subplots.AxesSubplot)**: The axis object representing the field.

#### Example Usage:
```python
fig, ax = visuals.field(yard_numbers=True, touchdown_markings=True)
```
---

## _snap()_
Creates a static snapshot of a specific frame in a play. The snapshot includes player positions and can be customized with field features.

```pythonverboseregexp
snap(data, gameId, playId, frameId, yard_numbers, touchdown_markings, fifty_yard, fig_size)
```

#### Parameters:
* **data (pd.DataFrame)**: The DataFrame containing play data.
* **gameId (int)**: The unique ID of the game. 
* **playId (int)**: The unique ID of the play. 
* **frameId (int)**: The frame ID of the play. 
* **yard_numbers (bool)**: Whether to display yard numbers. Default is True. 
* **touchdown_markings (bool)**: Whether to display touchdown markings. Default is True. 
* **fifty_yard (bool)**: Whether to highlight the fifty-yard line. Default is False. 
* **fig_size (tuple)**: The size of the figure in inches. Default is (12, 6.33).

#### Returns:
* **fig (matplotlib.figure.Figure)**: The figure object.
* **ax (matplotlib.axes._subplots.AxesSubplot)**: The axis object.

#### Example Usage:
```python
fig, ax = visuals.snap(data, gameId=2019090800, playId=75, frameId=10)
```
---

## _play_game()_
Animates an entire play, showing player positions and movements frame by frame. The animation can be saved as a GIF.
```pythonverboseregexp
play_game(data, gameId, playId, yard_numbers, touchdown_markings, fifty_yard, fig_size, save, loop, **kwargs)
```

#### Parameters:
* **data (pd.DataFrame)**: The DataFrame containing play data.
* **gameId (int)**: The unique ID of the game. 
* **playId (int)**: The unique ID of the play. 
* **yard_numbers (bool)**: Whether to display yard numbers. Default is True. 
* **touchdown_markings (bool)**: Whether to display touchdown markings. Default is True. 
* **fifty_yard (bool)**: Whether to highlight the fifty-yard line. Default is False. 
* **fig_size (tuple)**: The size of the figure in inches. Default is (12, 6.33).
* **save (bool)**: Whether to save the animation as a GIF. Default is False.
* **loop (bool)**: Whether to loop the animation. Default is False.
* ****kwargs**: Additional keyword arguments for save_params in case saving as a GIF, such as fps and bitrate.

#### Returns:
* **fig (matplotlib.figure.Figure)**: The figure object.
* **ax (matplotlib.axes._subplots.AxesSubplot)**: The axis object.
* **ani (matplotlib.animation.FuncAnimation)**: The animation object.

#### Example Usage:
```python
fig, ax, ani = visuals.play_game(data, gameId=2019090800, playId=75, save=True, loop=True)
```
---

### Example of Full Usage:
```python
import pandas as pd
from nfl import visuals

# Load your data into a pandas DataFrame
data = pd.read_csv("week_1.csv")

# Create a field visualization
fig, ax = visuals.field(yard_numbers=True, touchdown_markings=True, fifty_yard=False, fig_size=(12, 6.33))

# Snap a specific frame of a play
fig, ax = visuals.snap(data, gameId=2019090800, playId=75, frameId=10, yard_numbers=True, touchdown_markings=True, fifty_yard=False, fig_size=(12, 6.33))

# Animate a full play and save as GIF
fig, ax, ani = visuals.play_game(data, gameId=2019090800, playId=75, yard_numbers=True, touchdown_markings=True, fifty_yard=False, fig_size=(12, 6.33), save=True, loop=False)

```
---

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/shammeer-s/nfl/blob/master/LICENSE) file for details.
