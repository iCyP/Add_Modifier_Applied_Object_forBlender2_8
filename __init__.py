#MIT License @iCyP 2019

import bpy,bmesh

bl_info = {
    "name":"Add_Modifier_applied_object",
    "author": "iCyP",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "ObjectMode->Right click",
    "description": "Add_Modifier_applied_object",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}



class ICYP_OT_Add_Modifier_applied_object(bpy.types.Operator):
    bl_idname = "object.icyp_add_modifier_applied_object"
    bl_label = "Add Modifier applied object with shapekeys"
    bl_description = "Duplicate active object with modifier applied"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        base_obj = context.active_object
        base_key_blocks = base_obj.data.shape_keys.key_blocks if base_obj.data.shape_keys else []
        shapes = []

        #init
        for kb in base_key_blocks:
            kb.value = 0
        if  len(base_key_blocks)!=0:
            for tmp_mod in base_obj.modifiers:
                if tmp_mod.type == "MIRROR":
                    tmp_mod.use_mirror_merge = False

        #Duplicate meshes
        if len(base_key_blocks) > 0:           
            for kb in base_key_blocks:
                kb.value = 1
                shapes.append(base_obj.to_mesh(depsgraph = context.view_layer.depsgraph,preserve_all_data_layers = True).copy())
                shapes[-1].name = kb.name
                kb.value = 0
        else:
            shapes.append(base_obj.to_mesh(depsgraph = context.view_layer.depsgraph,preserve_all_data_layers = True).copy())
        
        dup_obj = bpy.data.objects.new(f"{base_obj.name}.dup",shapes[0])
        context.collection.objects.link(dup_obj)
        bpy.context.view_layer.objects.active = dup_obj
        dup_obj.location = base_obj.location

        #transfer vertex group(to_mesh breaks vertex index)
        for vg in base_obj.vertex_groups:
            dup_obj.vertex_groups.new(name=vg.name)
        mod = dup_obj.modifiers.new(name="tmp", type="DATA_TRANSFER")
        mod.object = base_obj
        mod.use_vert_data = True
        mod.data_types_verts = {'VGROUP_WEIGHTS'}
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)


        dup_obj.location = [p + d for p, d in zip(base_obj.location, [base_obj.bound_box[5][0]-base_obj.bound_box[0][0], 0, 0])]
        
        #shapekey_transfer
        dup_obj.shape_key_add(name="Basis")

        for shape in shapes[1:]:
            kb = dup_obj.shape_key_add(name=shape.name)
            for id,v in enumerate(shape.vertices):
                kb.data[id].co = v.co
        for shape in shapes[1:]:
            bpy.data.meshes.remove(shape)

        return {'FINISHED'}
    
# アドオン有効化時の処理
classes = [
    ICYP_OT_Add_Modifier_applied_object
    ]
    
def add_button(self, context):
    self.layout.operator(ICYP_OT_Add_Modifier_applied_object.bl_idname)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.append(add_button)
    
# アドオン無効化時の処理
def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(add_button)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if "__main__" == __name__:
    register()
