import bpy
from bpy.props import BoolProperty, EnumProperty
from .. import M3utils as m3


applyorshow = [("APPLY", "Apply", ""),
               ("REMOVE", "Remove", ""),
               ("SHOW", "Show", ""),
               ("HIDE", "Hide", "")]


class ModMachine(bpy.types.Operator):
    bl_idname = "machin3.mod_machine"
    bl_label = "MACHIN3: Mod Machine"
    bl_options = {'REGISTER', 'UNDO'}

    applyorshow = EnumProperty(name="Apply or Show", items=applyorshow, default="APPLY")

    applyall = BoolProperty(name="All (Overwrite)", default=False)
    applymirror = BoolProperty(name="Mirror", default=False)
    applybevel = BoolProperty(name="Bevel", default=False)
    applydisplace = BoolProperty(name="Displace", default=False)
    applyboolean = BoolProperty(name="Boolean", default=False)
    applydatatransfer = BoolProperty(name="Data Transfer", default=False)
    applyshrinkwrap = BoolProperty(name="Shrink Wrap", default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()
        row.prop(self, "applyorshow", expand=True)

        column.prop(self, "applyall", toggle=True)
        column.separator()

        row = column.row(align=True)
        row.prop(self, "applymirror", toggle=True)
        row.prop(self, "applybevel", toggle=True)
        row.prop(self, "applydisplace", toggle=True)

        row = column.row(align=True)
        row.prop(self, "applyboolean", toggle=True)
        row.prop(self, "applydatatransfer", toggle=True)
        row.prop(self, "applyshrinkwrap", toggle=True)

    def execute(self, context):
        bpy.ops.ed.undo_push(message="MACHIN3: Pre-Mod-Machine-State")  # without pushing the state, there you might loose the selections, when redoing the op and switching the type of mod

        self.selection = m3.selected_objects()
        active = m3.get_active()

        applylist = []

        if self.applymirror:
            applylist.append("MIRROR")
        if self.applybevel:
            applylist.append("BEVEL")
        if self.applydisplace:
            applylist.append("DISPLACE")
        if self.applyboolean:
            applylist.append("BOOLEAN")
        if self.applydatatransfer:
            applylist.append("DATA_TRANSFER")
        if self.applyshrinkwrap:
            applylist.append("SHRINKWRAP")

        for obj in self.selection:
            if obj.type == "MESH":
                m3.make_active(obj)

                for mod in obj.modifiers:
                    if (
                        not self.applyall
                        and mod.type in applylist
                        or self.applyall
                    ):
                        try:
                            if self.applyorshow == "APPLY":
                                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                                print(f"Applied '{obj.name}'s '{mod.name}' modifier")
                            elif self.applyorshow == "REMOVE":
                                bpy.ops.object.modifier_remove(modifier=mod.name)
                                print(f"Removed '{obj.name}'s '{mod.name}' modifier")
                            elif self.applyorshow == "SHOW":
                                mod.show_viewport = True
                                print(f"'{obj.name}'s '{mod.name}' modifier is now visible")
                            elif self.applyorshow == "HIDE":
                                mod.show_viewport = False
                                print(f"'{obj.name}'s '{mod.name}' modifier is now hidden")
                        except:
                            # print(m3.red("Failed to apply modifier") % (obj.name, mod.name))
                            pass
        m3.make_active(active)

        return {'FINISHED'}
