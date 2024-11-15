# NFL Field Visualization and Animation Library

This library provides utilities to visualize a football field, plot player positions, and animate plays. It is designed to handle data from tracking datasets, such as those used in football analytics.

Installing the library:

```bash
pip install nfl_tracks
```

After successfully installing the nfl_tracks package, import it in the file using the code below:
```python
# Import nfl_tracks
from nfl import visuals
```
## Table of Contents
1. Function Overview
   * field()
   * snap()
   * play_game()
2. Usage Examples 
3. Error Handling 
4. Customization Options
---
## 1. Function Overview
## field()
Generates a plot of a football field with customizable features.

```pythonverboseregexp
field(yard_numbers=True, touchdown_markings=True, fifty_yard=False, fig_size=(12, 6.33))
```

#### Parameters:
* **yard_numbers (bool, default True)**: Whether to display yard numbers on the field.
* **touchdown_markings (bool, default True)**: Whether to show touchdown zone labels.
* **fifty_yard (bool, default False)**: Highlights the 50-yard line in gold.
* **fig_size (tuple, default (12, 6.33))**: Specifies the figure size.

#### Returns:
* **fig (matplotlib.figure.Figure)**: The figure object.
* **ax (matplotlib.axes.Axes)**: The axes object containing the plot.

#### Example Usage:
```python
fig, ax = visuals.field()
plt.show()
```
![field.png](https://raw.githubusercontent.com/shammeer-s/nfl-tracks/e0d4dcada2bab940d84978964a52b3f5a06ed60b/outputs/field.png "Field")
---

## snap()
Plots the positions of players during a specific frame of a play.

```pythonverboseregexp
snap(data, gameId, playId, frameId, yard_numbers=True, touchdown_markings=True, fifty_yard=False, fig_size=(12, 6.33), **kwargs)
```

#### Parameters:
* **data (pd.DataFrame)**: Contains tracking data with columns including gameId, playId, frameId, x, y, and club.
* **gameId (int)**: Identifier for the game.
* **playId (int)**: Identifier for the play.
* **frameId (int)**: Identifier for the specific frame within the play. 
* **yard_numbers (bool, default True)**: Whether to display yard numbers on the field.
* **touchdown_markings (bool, default True)**: Whether to show touchdown zone labels.
* **fifty_yard (bool, default False)**: Highlights the 50-yard line in gold.
* **fig_size (tuple, default (12, 6.33))**: Specifies the figure size.
* ****kwargs**: Additional arguments
  * **size (int, default 10)**: Marker size for players.
  * **club_colors (dict)**: Custom mapping of club indices to colors.

#### Returns:
* **fig (matplotlib.figure.Figure)**: The figure object.
* **ax (matplotlib.axes.Axes)**: The axis object.

#### Example Usage:
```python
fig, ax = visuals.snap(data, gameId=2022091200, playId=64, frameId=10)
plt.show()
```
![snap.png](https://raw.githubusercontent.com/shammeer-s/nfl-tracks/refs/heads/master/outputs/snap.png "snap")
---

## play_game()
Animates a play by visualizing player movements over time.
```pythonverboseregexp
play_game(data, gameId, playId, kaggle=True, yard_numbers=True, touchdown_markings=True, fifty_yard=False, fig_size=(12, 6.33), save=False, loop=False, **kwargs)
```

#### Parameters:
* **data (pd.DataFrame)**: Contains tracking data with columns including gameId, playId, frameId, x, y, and club.
* **gameId (int)**: Identifier for the game.
* **playId (int)**: Identifier for the play.
* **kaggle (bool, default True)**: Enables compatibility with Kaggle's notebook environments.
* **yard_numbers (bool, default True)**: Whether to display yard numbers on the field.
* **touchdown_markings (bool, default True)**: Whether to show touchdown zone labels.
* **fifty_yard (bool, default False)**: Highlights the 50-yard line in gold.
* **fig_size (tuple, default (12, 6.33))**: Specifies the figure size.
* **save (bool, default False)**: Saves the animation as a play.gif file if True.
* **loop (bool, default False)**: Repeats the animation if True.
* ****kwargs**: Additional arguments
  * **size (int, default 10)**: Marker size for players.
  * **speed (int, default 100)**: Time interval between frames (in milliseconds).
  * **club_colors (dict)**: Custom mapping of club indices to colors.
  * **save_params (dict)**: Parameters for saving the animation.

#### Returns:
* **ani (matplotlib.animation.FuncAnimation)**: The animation object.

#### Example Usage:
```python
ani = visuals.play_game(data, gameId=2022091200, playId=64)
ani
```
![play.gif](https://raw.githubusercontent.com/shammeer-s/nfl-tracks/refs/heads/master/outputs/play.gif "play_game")
---
## 2. Usage Examples
Plotting a Field
```python
fig, ax = visuals.field(touchdown_markings=False, fifty_yard=True)
plt.show()
```

Visualizing a Single Frame
```python
fig, ax = visuals.snap(data, gameId=2022091200, playId=52, frameId=15, size=20)
plt.show()
```

Plotting a Field
```python
ani = visuals.play_game(data, gameId=2022091200, playId=24, save=True, speed=150)
ani
```
---
## 3. Error Handling
* **Data Validation**: Functions check whether _gameId_, _playId_, and _frameId_ exist in the data.
* **Color Mapping**: Ensures all _club_ values map to valid colors. Raises an error if a _club_ is unmapped.
* **Saving Animations**: Errors in saving are explained with links to relevant Matplotlib documentation.
---
## 4. Customization Options
* **Player Marker Sizes**: Control player marker sizes using the _size_ parameter.
* **Color Mapping**: Customize player colors by passing a dictionary to _club_colors_.
* **Animation Speed**: Adjust frame transition time with the _speed_ parameter.
* **Output Formats**: Save animations with customized parameters for the _PillowWriter_.
---
## 5. License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/shammeer-s/nfl/blob/master/LICENSE) file for details.

---
This library is ideal for visualizing football plays with clear, customizable graphics and animations. For further assistance, refer to Matplotlib's documentation or provide specific details for troubleshooting.