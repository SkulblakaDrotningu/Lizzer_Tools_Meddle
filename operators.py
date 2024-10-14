import bpy
from os import path


class ActiveMatFixOperator(bpy.types.Operator):

    bl_idname = "material.material_fixer_active"
    bl_label = "Material Fix Active"

    def execute(self, context):
        if bpy.context.active_object.active_material is None:
            return {'CANCELLED'}
        mat = bpy.context.active_object.active_material.name
        shader = 'empty'
        for key in shaderType.keys():
            if key in mat:
                shader = shaderType.get(key)
            
        if shader != 'empty':
            materialFixer(mat, shader)
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
    
class AutoMatFixOperator(bpy.types.Operator):
    
    bl_idname = "material.material_fixer_auto"
    bl_label = "Material Fix Auto"
    
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.data is not None and hasattr(obj.data, 'materials'):
                for mat in obj.data.materials:
                    material = mat.name
                    shader = 'empty'

                    for key in shaderType.keys():
                        if key in material:
                            shader = shaderType.get(key)
                        
                    if shader != 'empty':
                        materialFixer(material, shader)

        return {'FINISHED'}

class ImportShaderWOLOperator(bpy.types.Operator):

    bl_idname = "append.import_wol"
    bl_label = "Import WOL Shader"
    
    def execute(self, context):
        
        nodegroups = [
            'Dawntrail etc_a Shader Skul Version',
            'Dawntrail etc_b Shader Skul Version',
            'Dawntrail etc_c Skul version',
            'Dawntrail Eye Shader Skul Version',
            'Dawntrail Face Shader Skul Version',
            'Dawntrail Hair Shader Skul Version',
            'Dawntrail Skin Shader Skul Version',
            'Lip Settings',
            'Roughness Influence',
            'Specular Influence',
            'SSS Influence'
        ]
        
        blendfile = path.dirname(path.abspath(__file__)) + "/WOL Shader V7 Distribution.blend"
        section = "\\NodeTree\\"

        for n in nodegroups:
                
            bpy.ops.wm.append(
                filepath= blendfile + section + n,
                filename= n,
                directory= blendfile + section,
                do_reuse_local_id = True
            )
        return {'FINISHED'}


nodeProperty = {
    "Skin Color": "SkinColor",
    "Lip Color": "LipColor",
    "Lip Color Strength": "LipStick",
    "Eye Color": "LeftIrisColor",
    "Second Eye Color": "RightIrisColor",
    "Hair Color": "MainColor",
    "Highlights Color": "MeshColor",
    "Enable Highlights": "Highlights",
    "Limbal Color": "OptionColor"
}

shaderType = {
    "bibo_skin": "Dawntrail Skin Shader Skul Version",
    "_fac_": "Dawntrail Face Shader Skul Version",
    "_hir_": "Dawntrail Hair Shader Skul Version",
    "_hair_": "Dawntrail Hair Shader Skul Version",
    "_iri_": "Dawntrail Eye Shader Skul Version",
    "_etc_a_": "Dawntrail etc_a Shader Skul Version",
    "_etc_b_": "Dawntrail etc_b Shader Skul Version",
    "_etc_c_": "Dawntrail etc_c Skul version"
}


def materialFixer(mat, group):
    
    material = bpy.data.materials[mat].node_tree
    properties = bpy.data.materials[mat]

    #Removes all nodes other than textures to make it simpler to construct a node setup
    for node in material.nodes:
        if node.type != "TEX_IMAGE":
            material.nodes.remove(node)
        
    #Sets Normal Map and Mask Textures to Non-Color
    for node in material.nodes:
        if node.label == 'NORMAL MAP' or node.label == 'SPECULAR':
            node.image.colorspace_settings.name='Non-Color'

    #Add Material Output
    output = material.nodes.new('ShaderNodeOutputMaterial')
    output.location = (500,300)

    #Add the appropriate shader node group

    groupNode = material.nodes.new('ShaderNodeGroup')
    groupNode.node_tree = bpy.data.node_groups[group]
    groupNode.location = (10, 300)
    groupNode.width = 300
    material.links.new(groupNode.outputs[0], material.nodes['Material Output'].inputs['Surface'])

    #Configure the shader node group with custom properties
    for setting in groupNode.inputs:
        if setting.name in nodeProperty.keys():
            groupNode.inputs[setting.name].default_value = getProperty(setting, properties)

    #Connect Image Texture Nodes
    for node in material.nodes:

        if node.label == "BASE COLOR":
            if 'Diffuse Texture' in groupNode.inputs:
                material.links.new(node.outputs['Color'], groupNode.inputs['Diffuse Texture'])
            if 'Diffuse Alpha' in groupNode.inputs:
                material.links.new(node.outputs['Alpha'], groupNode.inputs['Diffuse Alpha'])
        if node.label == "NORMAL MAP":
            if 'Normal Texture' in groupNode.inputs:
                material.links.new(node.outputs['Color'], groupNode.inputs['Normal Texture'])
            if 'Normal Alpha' in groupNode.inputs:
                material.links.new(node.outputs['Alpha'], groupNode.inputs['Normal Alpha'])
        if node.label == "SPECULAR":
            if 'Mask Texture' in groupNode.inputs:
                material.links.new(node.outputs['Color'], groupNode.inputs['Mask Texture'])
            if 'Mask Alpha' in groupNode.inputs:
                material.links.new(node.outputs['Alpha'], groupNode.inputs['Mask Alpha'])


#Function to get the values of a property with handling for both RGBA values and single values

def getProperty(propertyName, properties):
    prop = []
    if propertyName.type == "RGBA":
        if propertyName.name == "Limbal Color":
            for value in properties[nodeProperty.get(propertyName.name)].to_dict().values():
                prop.append(value)
        else:
            for value in properties[nodeProperty.get(propertyName.name)].to_list():
                prop.append(value)

        #Incase an RGBA value only has the RGB in the property
        if len(prop) == 3:
            prop.append(1)

    if propertyName.type == "VALUE":
        prop = float(properties[nodeProperty.get(propertyName.name)])
    return(prop)

    
#mat = bpy.context.active_object.active_material.name

#for key in shaderType.keys():
    #if key in mat:
        #shader = shaderType.get(key)

#materialFixer(mat, shader)

classes = [
    ActiveMatFixOperator,
    AutoMatFixOperator,
    ImportShaderWOLOperator
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)