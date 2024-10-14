import bpy
from . import operators


class MeddleSetterUpper(bpy.types.Panel):
    bl_idname = "OBJECT_PT_Meddle_Setter_Upper"
    bl_label = "WOL Shader"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "Lizzer Tools"

    def draw(self, context):
        obj = context.object

        layout = self.layout

        row = layout.row()
        row.operator(operators.ImportShaderWOLOperator.bl_idname)
        
        row = layout.row()
        row.label(text="Add WOL shader to objects")

        row = layout.row()
        row.operator(operators.ActiveMatFixOperator.bl_idname, text='Current')
        row.operator(operators.AutoMatFixOperator.bl_idname, text='Auto')


classes = [
    MeddleSetterUpper
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)