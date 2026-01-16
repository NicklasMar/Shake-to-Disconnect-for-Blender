bl_info = {
    "name": "Shake to Disconnect",
    "author": "Nicklas.mar",
    "doc_url": "https://www.instagram.com/nicklas.mar/",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "Node Editor > N-Panel > Shake",
    "description": "Disconnect nodes by shaking them (Auto-Start)",
    "category": "Node",
}

import bpy
import mathutils
from collections import deque
from bpy.app.handlers import persistent

# ------------------------------------------------------------------------
# 1. SETTINGS (PREFERENCES)
# ------------------------------------------------------------------------
class NODE_Shake_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    shake_threshold: bpy.props.FloatProperty(
        name="Shake Threshold",
        description="Required travel distance. Lower = More sensitive.",
        default=150.0,
        min=10.0,
        max=1000.0
    )

    range_limit: bpy.props.FloatProperty(
        name="Range Limit",
        description="Maximum radius. If dragged too far, it won't trigger.",
        default=200.0,
        min=50.0,
        max=500.0
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Sensitivity Settings:")
        layout.prop(self, "shake_threshold")
        layout.prop(self, "range_limit")

# ------------------------------------------------------------------------
# 2. LOGIC (OPERATOR)
# ------------------------------------------------------------------------
class NODE_OT_shake_disconnect_global(bpy.types.Operator):
    """Background Worker for Shake Detection"""
    bl_idname = "node.shake_disconnect_global"
    bl_label = "Shake Detection Worker"
    
    _timer = None
    _is_running = False
    
    history_len = 8          
    check_interval = 0.05    
    position_history = None
    last_node_name = ""

    def modal(self, context, event):
        # Clean exit if addon is disabled
        if not NODE_OT_shake_disconnect_global._is_running:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # Load Settings
            try:
                prefs = context.preferences.addons[__name__].preferences
                threshold = prefs.shake_threshold
                r_limit = prefs.range_limit
            except:
                threshold = 150.0
                r_limit = 200.0

            # Scan Nodes
            active_node_found = False
            for area in context.window.screen.areas:
                if area.type == 'NODE_EDITOR':
                    for space in area.spaces:
                        if space.type == 'NODE_EDITOR':
                            tree = space.edit_tree
                            if tree and tree.nodes.active:
                                self.process_node(tree, tree.nodes.active, threshold, r_limit)
                                active_node_found = True
                                break 
                if active_node_found: break

        return {'PASS_THROUGH'}

    def process_node(self, tree, node, threshold, r_limit):
        node_id = f"{tree.name}_{node.name}"
        if node_id != self.last_node_name:
            self.position_history.clear()
            self.last_node_name = node_id
        
        current_pos = mathutils.Vector(node.location)
        
        # Optimization: Only record if moved > 0.1 units
        if len(self.position_history) > 0 and (self.position_history[-1] - current_pos).length < 0.1:
            return

        self.position_history.append(current_pos)
        
        if len(self.position_history) == self.history_len:
            if self.detect_shake(threshold, r_limit):
                self.disconnect_node(tree, node)
                self.position_history.clear() 
                self.report({'INFO'}, f"Disconnected: {node.name}")

    def detect_shake(self, threshold, r_limit):
        if not self.position_history: return False
        history = list(self.position_history)
        
        total_travel = sum((history[i+1] - history[i]).length for i in range(len(history) - 1))
        net_displacement = (history[-1] - history[0]).length
        
        if total_travel > threshold and net_displacement < r_limit:
            return True
        return False

    def disconnect_node(self, tree, node):
        for input_socket in node.inputs:
            for link in input_socket.links:
                tree.links.remove(link)
        for output_socket in node.outputs:
            for link in output_socket.links:
                tree.links.remove(link)

    def execute(self, context):
        if not NODE_OT_shake_disconnect_global._is_running:
            NODE_OT_shake_disconnect_global._is_running = True
            self.position_history = deque(maxlen=self.history_len)
            self.last_node_name = ""
            
            wm = context.window_manager
            self._timer = wm.event_timer_add(self.check_interval, window=context.window)
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        return {'FINISHED'}

    def cancel(self, context):
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)
            self._timer = None
        NODE_OT_shake_disconnect_global._is_running = False

# ------------------------------------------------------------------------
# 3. UI PANEL (N-Panel) - Clean
# ------------------------------------------------------------------------
class NODE_PT_shake_panel(bpy.types.Panel):
    bl_label = "Shake Disconnect"
    bl_idname = "NODE_PT_shake_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Shake'

    def draw(self, context):
        layout = self.layout
        
        try:
            prefs = context.preferences.addons[__name__].preferences
            layout.prop(prefs, "shake_threshold", text="Threshold")
            layout.prop(prefs, "range_limit", text="Range")
        except:
            layout.label(text="Addon not found/active")

# ------------------------------------------------------------------------
# AUTO-START HANDLERS
# ------------------------------------------------------------------------
@persistent
def auto_start_handler(dummy):
    if not NODE_OT_shake_disconnect_global._is_running:
        try:
            bpy.ops.node.shake_disconnect_global('INVOKE_DEFAULT')
        except:
            pass

# ------------------------------------------------------------------------
# REGISTRATION
# ------------------------------------------------------------------------
classes = (NODE_Shake_Preferences, NODE_OT_shake_disconnect_global, NODE_PT_shake_panel)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    if auto_start_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(auto_start_handler)
    
    # Start immediately upon activation
    bpy.app.timers.register(lambda: bpy.ops.node.shake_disconnect_global('INVOKE_DEFAULT'), first_interval=0.5)

def unregister():
    NODE_OT_shake_disconnect_global._is_running = False
    
    if auto_start_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(auto_start_handler)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()