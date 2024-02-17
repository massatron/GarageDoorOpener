import bpy

# Loop through all objects in the scene
for obj in bpy.context.scene.objects:
    # Make sure the object is the active object
    bpy.context.view_layer.objects.active = obj
    # Ensure the object is selected
    obj.select_set(True)
    
    # Check if the object has modifiers
    if obj.modifiers:
        # Apply all modifiers for the object
        for modifier in obj.modifiers[:]:
            # Try to apply the modifier, but catch exceptions for modifiers that cannot be applied
            try:
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            except RuntimeError as e:
                print(f"Could not apply modifier {modifier.name} to {obj.name}: {e}")

    # Deselect the object before moving on to the next
    obj.select_set(False)
