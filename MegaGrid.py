import bpy
import bmesh
import random
grid_size = 10
grid_subdivisions = 5
num_grids = 10
face_base = grid_size / grid_subdivisions
num_iterations = 5
select_random_percent = 50

bpy.ops.mesh.primitive_plane_add(size=grid_size, enter_editmode=False, location=(0, 0, 0))
bpy.ops.object.editmode_toggle()
bpy.context.tool_settings.mesh_select_mode = (False, False, True)
bpy.ops.mesh.subdivide(number_cuts=grid_subdivisions-1, quadcorner='INNERVERT')
bpy.ops.object.modifier_add(type='ARRAY')
bpy.context.object.modifiers["Array"].use_merge_vertices = True
bpy.context.object.modifiers["Array"].use_relative_offset = False
bpy.context.object.modifiers["Array"].use_constant_offset = True
bpy.context.object.modifiers["Array"].constant_offset_displace[2] = face_base
bpy.context.object.modifiers["Array"].count = num_grids
bpy.ops.object.editmode_toggle()
bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Array")
bpy.ops.object.editmode_toggle()
for i in range(num_iterations):
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.edge_split()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_random(percent=select_random_percent,seed=random.randint(1, 10000))
    bpy.ops.mesh.subdivide()
bpy.ops.object.editmode_toggle()
#all surface areas
bpy.ops.mesh.primitive_plane_add(size=face_base, enter_editmode=True, location=(0, 0, 0))
arrayAreas = []
for i in range(num_iterations):
    bpy.ops.mesh.subdivide()
    ob = bpy.context.edit_object
    me = ob.data
    bm = bmesh.from_edit_mesh(me)
    bm.faces.ensure_lookup_table()
    area = bm.faces[0].calc_area()            
    arrayAreas.append(area)
bpy.ops.object.editmode_toggle()
bpy.ops.object.delete(use_global=False)

ob = bpy.context.scene.objects["Plane"]
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.ops.object.editmode_toggle()
#duplicate faces based on area size
for j in range(num_iterations):
    ob = bpy.context.edit_object
    me = ob.data
    bm = bmesh.from_edit_mesh(me)
    for f in bm.faces:
        f.select = f.calc_area() == arrayAreas[j]
    factor = 2**(j+1)
    for g in range(factor-1):
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, face_base/factor)})
bpy.ops.object.editmode_toggle()
bpy.ops.object.select_all(action='DESELECT')
#parent cube and instance
ob = bpy.context.scene.objects["Cube"]
ob.select_set(True)
ob = bpy.context.scene.objects["Plane"]
ob.select_set(True)    
bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
bpy.ops.object.select_all(action='DESELECT')
ob = bpy.context.scene.objects["Plane"]
bpy.context.view_layer.objects.active = ob
ob.select_set(True)
bpy.context.object.instance_type = 'FACES'
bpy.context.object.use_instance_faces_scale = True
bpy.context.object.show_instancer_for_viewport = False
bpy.context.object.show_instancer_for_render = False

bpy.ops.object.vertex_group_add()
bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_EDIT')
bpy.context.object.modifiers["VertexWeightEdit"].vertex_group = "Group"
bpy.context.object.modifiers["VertexWeightEdit"].use_add = True
bpy.context.object.modifiers["VertexWeightEdit"].use_remove = True
bpy.context.object.modifiers["VertexWeightEdit"].falloff_type = 'CURVE'

bpy.ops.texture.new()
tex = bpy.data.textures.new("Noise", 'DISTORTED_NOISE')
bpy.data.textures["Noise"].noise_basis = 'CELL_NOISE'
bpy.data.textures["Noise"].noise_distortion = 'CELL_NOISE'
bpy.data.textures["Noise"].noise_scale = 0.55
bpy.data.textures["Noise"].distortion = 2
bpy.data.textures["Noise"].contrast = 0.5

bpy.context.object.modifiers["VertexWeightEdit"].mask_texture = bpy.data.textures['Noise']

bpy.ops.object.modifier_add(type='MASK')
bpy.context.object.modifiers["Mask"].vertex_group = "Group"



#it changes the curve but crashes blender when clicking modifier tab
#curve = bpy.context.object.modifiers["VertexWeightEdit"].map_curve
#curve.clip_min_x = 0.0
#curve.clip_min_y = 1.0
#curve.update()
