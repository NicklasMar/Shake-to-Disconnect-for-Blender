# Shake to Disconnect for Blender
Bring the intuitive Houdini workflow to Blender!

This add-on allows you to disconnect any node simply by grabbing it and shaking it back and forth. No more Ctrl+Right Click cutting or manually detaching wires. Just shake and break.

## ✨ Features
- **Houdini-Style Workflow**: Inspired by the "Shake to Disconnect" feature in SideFX Houdini.
- **Global Support**: Works in all Node Editors (Shader, Geometry Nodes, Compositor, Texture Nodes).
- **Auto-Start**: Runs automatically in the background when Blender starts. No manual activation required.
- **Customizable**: Adjust sensitivity and shake range directly in the N-Panel.
- **Smart Detection**: Detects rapid movement within a small radius to prevent accidental disconnects during normal layout adjustments.

## 📥 Installation
1. Download the latest `.zip`
2. Unzip the downloaded file.
3. Open Blender and go to `Edit > Preferences`.
4. Select the `Add-ons` tab and click `Install...`.
5. Browse to the unzipped folder and select the `shake_disconnect.py` file.
6. Check the box next to `Node: Shake to Disconnect` to enable it.

## 🎮 How to Use
1. Open any Node Editor (e.g., Shader Editor or Geometry Nodes).
2. Select a node and grab it (press `G` or click and drag).
3. Shake it quickly back and forth (like erasing an Etch A Sketch).
4. The connections will automatically snap, and the node is free!

## ⚙️ Configuration
You can adjust the sensitivity in the N-Panel (Sidebar) of the Node Editor under the "Shake" tab, or in the Add-on Preferences.

- **Shake Threshold**: Controls how much total distance the mouse must travel to register a shake.
  - Lower value = More sensitive (easier to trigger).
  - Higher value = Requires more vigorous shaking.
- **Range Limit**: The maximum radius the node is allowed to move away from its starting point during the shake.
  - Prevents the addon from triggering when you are just dragging a node across the screen.

👨‍💻 Author
Created by Nicklas.mar Follow on Instagram