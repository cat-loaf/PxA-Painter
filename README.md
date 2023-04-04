# PxA-Painter <img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/icons/normal/paint.png" width="20">
This is a pixel art painting program made in Python.

## Libraries
The technologies used in this project are:
<ul>
<li> Pygame
<li> Tkinter
<li> Scikit-Image
</ul>

## Execution
To run this project, there are a few requirements:
<ul>
  <li> You must have Python 3.10 or onwards installed
  <li> You must have pygame installed
  <li> You must have scikit-image installed
  <li> You must have numpy
</ul>

To install all the modules, run `pip install -r requirements.txt` in the root of the folder.

When all the modules are installed, you can run `python main.py` or `py main.py` in the root of the folder to start the program.

## Program Abilities
There are 5 tools, a loading/saving function and colour selecting.

### Tools
<ul>
  <li> Move <img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/icons/normal/move.png"> - Moves the canvas to a desired position
  <li> Pencil <img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/icons/normal/paint.png"> - Paints the cell selected by the mouse with a selected colour
  <li> Erase <img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/icons/normal/eraser.png"> - Erases the cell selected by the mouse
  <li> Fill <img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/icons/normal/fill.png"> - Fills the section selected by the mouse
  <li> Splash <img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/icons/normal/clear.png"> - Clears the canvas to the selected colour
</ul>

### Saving/Loading
The program saves and loads canvases in the `.pxa` format. 

It is text-editable since the content of the file is a list of RGB triplets, with a header of the size of the canvas.

### Colour Palette
The colour palette can be changed, but do so at your own risk. There are plans to fix the way the palette is loaded, but at the current time, palettes under 25 colours are guaranteed to work.

There is an issue with loading files that are not saved with the same colour palette as the current colour palette. Because of this issue, I recommend that you do not change the colour palette at all if possible, and if not possible, remember to reload the correct colour palette.

## Preview
<img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/screenshots/0.png" width="300">
<img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/screenshots/1.png" width="300">
<img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/screenshots/2.png" width="300">
<img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/screenshots/3.png" width="300">
<img src="https://raw.githubusercontent.com/cat-loaf/PxA-Painter/main/screenshots/4.png" width="300">