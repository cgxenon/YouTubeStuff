import bpy
import mathutils

move_root = False  # Whether to move root bones

# --- Define arm1 and arm2 from selection ---
sel = [o for o in bpy.context.selected_objects if o.type == 'ARMATURE']

if len(sel) != 2:
    raise Exception("Select 2 armatures: reference and target.")

arm2 = bpy.context.view_layer.objects.active  # The one being moved (target)
arm1 = sel[0] if sel[1] == arm2 else sel[1]   # The reference one

print("Reference:", arm1.name)
print("Target:", arm2.name)

# --- Switch both to Edit Mode ---
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.objects.active = arm1
bpy.ops.object.mode_set(mode='EDIT')
bpy.context.view_layer.objects.active = arm2
bpy.ops.object.mode_set(mode='EDIT')

def collect_chain(bone):
    arr = [bone]
    for c in bone.children:
        arr.extend(collect_chain(c))
    return arr

# Collect chain from the reference root
roots = [b for b in arm1.data.edit_bones if b.parent is None]
root = roots[0]
chain = collect_chain(root)

mw1 = arm1.matrix_world
mw2_inv = arm2.matrix_world.inverted()

# --- Main transfer ---
for src in chain:

    # Skip root bone if needed
    if src.parent is None and not move_root:
        continue

    # Bones must match by name
    if src.name not in arm2.data.edit_bones:
        continue

    dst = arm2.data.edit_bones[src.name]

    # Reference head -> world space
    src_head_world = mw1 @ src.head

    # Target's old head -> world space
    dst_head_world = arm2.matrix_world @ dst.head

    # New dst head position in arm2 local space
    new_head_local = mw2_inv @ src_head_world

    # Local delta
    delta_local = new_head_local - dst.head

    # Shift bone body without changing orientation
    dst.head += delta_local
    dst.tail += delta_local

print("Done — working based on selection!")