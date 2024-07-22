# Blendshape Wrapper for Maya

This tool is designed for applying blendweights between matching objects in a Maya scene, based on their namespace. It provides a user-friendly interface for selecting and pairing render geometry with animation caches, and then applying blendshapes between them.

## Features

- Automatically collects geometry objects from the Maya scene
- Groups objects by namespace
- Allows easy selection and pairing of render geometry and animation caches
- Applies blendshapes between paired objects
- Removes existing blendshapes before applying new ones
- Provides a visual feedback system for matched pairs

## Installation

1. Download or clone this repository to your local machine.

2. Ensure that the following files are in the `src` directory of the package:
   - `blendshape_wrapper.py`
   - `flow_layout.py`
   - `utils.py`
   - `widgets.py`

3. Add the following Python code to a shelf button in Maya:

```python
import sys
import os
import importlib

# Ensure the script directory is in the sys.path
script_dir = r'C:/Path/To/Your/Package/src'
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Import the modules with reloading
import utils
import flow_layout
import widgets
import blendshape_wrapper

importlib.reload(utils)
importlib.reload(flow_layout)
importlib.reload(widgets)
importlib.reload(blendshape_wrapper)

from blendshape_wrapper import BlendshapeDialog
from utils import collect_geo_objects, get_maya_main_window

def show_blendshape_wrapper():
    geo_dict = collect_geo_objects()
    maya_main_window = get_maya_main_window()
    dialog = BlendshapeDialog(geo_dict, maya_main_window)
    dialog.show()

# Call the function to show the blendshape wrapper
show_blendshape_wrapper()
```

   Replace `'C:/Path/To/Your/Package/src'` with the actual path to the `src` folder within your package.

4. Save the shelf.

## Usage

1. Click the shelf button you created to launch the Blendshape Wrapper tool.

2. In the dialog that appears:
   - Select the namespace for the render geometry from the "Render Geo" dropdown.
   - Select the namespace for the animation cache from the "Animation Cache" dropdown.
   - The tool will automatically pair objects with matching names across the two namespaces.
   - You can manually check or uncheck objects to include or exclude them from the blendshape process.
   - Matched pairs will be highlighted with the same color.

3. Click the "Apply Blendshapes" button to create blendshapes between the paired objects.

4. A results dialog will appear, showing the success or failure of each blendshape operation.

## Notes

- The tool automatically removes existing blendshapes before applying new ones.
- Objects are expected to end with '_GEO' to be recognized by the tool.
- The tool uses PySide2 for its user interface, which should be available in most recent Maya versions.

## Troubleshooting

If you encounter any issues:
- Ensure that all required files are in the correct directory (inside the `src` folder of your package).
- Check that the path in the shelf button script correctly points to your package's `src` directory.
- Make sure you have the necessary permissions to write to the Maya scripts directory.

For further assistance, please contact the tool's maintainer.