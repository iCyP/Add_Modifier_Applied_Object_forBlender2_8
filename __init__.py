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
    bl_label = "Add_Modifier_applied_object"
    bl_description = "Add_Modifier_applied_object"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        base_obj = context.active_object
        shapes = []
        #init
        for kb in base_obj.data.shape_keys.key_blocks:
            kb.value = 0
        for kb in base_obj.data.shape_keys.key_blocks:
            kb.value = 1
            shapes.append(base_obj.to_mesh(context.depsgraph,True))
            shapes[-1].name = f"{base_obj.name}_{kb.name}"
            kb.value = 0
        dup_obj = bpy.data.objects.new(f"{base_obj.name}.dup",shapes[0])
        context.collection.objects.link(dup_obj)
        dup_obj.location = [p+d for p,d in zip(base_obj.location,[3,0,0])]
        bpy.context.view_layer.objects.active = dup_obj

        
        dup_obj.shape_key_add(name="Basis")

        for shape in shapes[1:]:
            kb = dup_obj.shape_key_add(name = shape.name)
            for id,v in enumerate(shape.vertices):
                kb.data[id].co = v.co
        for shape in shapes[1:]:
            bpy.data.meshes.remove(shape)
        if "MIRROR" in [m.type for m in base_obj.modifiers]:
            bpy.ops.object.vertex_group_mirror(mirror_weights=True, flip_group_names=True, all_groups=True, use_topology=False)
        return {'FINISHED'}
    
# アドオン有効化時の処理
classes = [
    ICYP_OT_Add_Modifier_applied_object
    ]
    
def add_button(self, context):
    if context.active_object.type == "Mesh":
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
