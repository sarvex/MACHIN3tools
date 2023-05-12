import bpy
from bpy.props import StringProperty
import subprocess


class OpenLibraryBlend(bpy.types.Operator):
    bl_idname = "machin3.open_library_blend"
    bl_label = "MACHIN3: Open Library Blend"
    bl_description = "Open new Blender instance, loading the library sourced in the selected object or collection instance."
    bl_options = {'REGISTER'}

    blendpath: StringProperty()
    library: StringProperty()

    def execute(self, context):
        blenderbinpath = bpy.app.binary_path

        cmd = [blenderbinpath, self.blendpath]
        blender = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # it it loeaded successfullly reload the library to update any changes that were done
        if blender and self.library:
            if lib := bpy.data.libraries.get(self.library):
                lib.reload()

        return {'FINISHED'}
