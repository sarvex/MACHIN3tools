import bpy
from bpy.props import IntProperty, BoolProperty
import bmesh
from math import radians


# TODO: update descriptions


class ShadeSmooth(bpy.types.Operator):
    bl_idname = "machin3.shade_smooth"
    bl_label = "Shade Smooth"
    bl_description = "Set smooth shading in object and edit mode\nALT: Mark edges sharp if face angle > auto smooth angle"
    bl_options = {'REGISTER', 'UNDO'}

    sharpen: BoolProperty(name="Set Sharps", default=False)

    include_children: BoolProperty(name="Include Children", default=False)
    include_boolean_objs: BoolProperty(name="Include Boolean Objects", default=False)

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)

        column.prop(self, 'sharpen', toggle=True)

        if context.mode == 'OBJECT':
            row = column.row(align=True)
            row.prop(self, 'include_children', toggle=True)
            row.prop(self, 'include_boolean_objs', toggle=True)

    def invoke(self, context, event):
        self.sharpen = event.alt
        self.include_boolean_objs = event.ctrl
        self.include_children = event.shift
        return self.execute(context)

    def execute(self, context):
        if context.mode == "OBJECT":

            selected = [obj for obj in context.selected_objects]

            children = [(ob, ob.visible_get()) for obj in selected for ob in obj.children_recursive if ob.name in context.view_layer.objects] if self.include_children else []
            boolean_objs = [(mod.object, mod.object.visible_get()) for obj in selected for mod in obj.modifiers if mod.type == 'BOOLEAN' and mod.object and mod.object.name in context.view_layer.objects] if self.include_boolean_objs else []
            more_objects = set(children + boolean_objs)

            # print()
            # print("selected:", [obj.name for obj in selected])
            # print("children:", [obj.name for obj, _ in children])
            # print("boolean objs:", [obj.name for obj, _ in boolean_objs])
            # print("more objs:", [obj.name for obj, _ in more_objects])

            # ensure children/boolean objects are visible and selected
            for obj, state in more_objects:
                if not state:
                    obj.hide_set(False)
                obj.select_set(True)

            # shade everything smooth
            bpy.ops.object.shade_smooth()

            # restore child/boolean object visibility states
            for obj, state in more_objects:
                obj.hide_set(not state)

            # restore original selection
            bpy.ops.object.select_all(action='DESELECT')
            
            for obj in selected:
                obj.select_set(True)

            # set sharps based on face angles + activate auto smooth + enable sharp overlays
            if self.sharpen:
                for obj in selected:
                    self.set_sharps(context.mode, obj)

                for obj, _ in more_objects:
                    self.set_sharps(context.mode, obj)

                context.space_data.overlay.show_edge_sharp = True

        elif context.mode == "EDIT_MESH":
            if self.set_sharps:
                self.set_sharps(context.mode, context.active_object)

                context.space_data.overlay.show_edge_sharp = True
            else:
                bpy.ops.mesh.faces_shade_smooth()

        return {'FINISHED'}

    def set_sharps(self, mode, obj):
        obj.data.use_auto_smooth = True
        angle = obj.data.auto_smooth_angle

        if mode == 'OBJECT':
            bm = bmesh.new()
            bm.from_mesh(obj.data)

        elif mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(obj.data)

            # smooth all faces like in object mode
            for f in bm.faces:
                f.smooth = True

        bm.normal_update()

        sharpen = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle() > angle]

        for e in sharpen:
            e.smooth = False

        if mode == 'OBJECT':
            bm.to_mesh(obj.data)
            bm.clear()

        elif mode == 'EDIT_MESH':
            bmesh.update_edit_mesh(obj.data)

        # obj.data.auto_smooth_angle = radians(180)


class ShadeFlat(bpy.types.Operator):
    bl_idname = "machin3.shade_flat"
    bl_label = "Shade Flat"
    bl_description = "Set flat shading in object and edit mode\nALT: Clear all sharps, bweights, creases and seams."
    bl_options = {'REGISTER', 'UNDO'}

    clear: BoolProperty(name="Clear Sharps, BWeights, etc", default=False)

    include_children: BoolProperty(name="Include Children", default=False)
    include_boolean_objs: BoolProperty(name="Include Boolean Objects", default=False)

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)

        column.prop(self, 'clear', toggle=True)

        if context.mode == 'OBJECT':
            row = column.row(align=True)
            row.prop(self, 'include_children', toggle=True)
            row.prop(self, 'include_boolean_objs', toggle=True)

    def invoke(self, context, event):
        self.clear = event.alt
        self.include_boolean_objs = event.ctrl
        self.include_children = event.shift
        return self.execute(context)

    def execute(self, context):
        if context.mode == "OBJECT":
            selected = [obj for obj in context.selected_objects]

            children = [(ob, ob.visible_get()) for obj in selected for ob in obj.children_recursive if ob.name in context.view_layer.objects] if self.include_children else []
            boolean_objs = [(mod.object, mod.object.visible_get()) for obj in selected for mod in obj.modifiers if mod.type == 'BOOLEAN' and mod.object and mod.object.name in context.view_layer.objects] if self.include_boolean_objs else []
            more_objects = set(children + boolean_objs)

            # print()
            # print("selected:", [obj.name for obj in selected])
            # print("children:", [obj.name for obj, _ in children])
            # print("boolean objs:", [obj.name for obj, _ in boolean_objs])
            # print("more objs:", [obj.name for obj, _ in more_objects])

            # # ensure children/boolean objects are visible and selected
            for obj, state in more_objects:
                if not state:
                    obj.hide_set(False)
                obj.select_set(True)

            # shade everything flat
            bpy.ops.object.shade_flat()

            # restore child/boolean object visibility states
            for obj, state in more_objects:
                obj.hide_set(not state)

            # restore original selection
            bpy.ops.object.select_all(action='DESELECT')
            
            for obj in selected:
                obj.select_set(True)

            # clear all sharps, bweights, seams and creases
            if self.clear:
                for obj in selected:
                    self.clear_obj_sharps(obj)

                for obj, _ in more_objects:
                    self.clear_obj_sharps(obj)

        elif context.mode == "EDIT_MESH":
            if self.clear:
                self.clear_mesh_sharps(context.active_object.data)

            else:
                bpy.ops.mesh.faces_shade_flat()

        return {'FINISHED'}

    def clear_obj_sharps(self, obj):
        obj.data.use_auto_smooth = False

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.normal_update()

        bw = bm.edges.layers.bevel_weight.verify()
        cr = bm.edges.layers.crease.verify()

        for e in bm.edges:
            e[bw] = 0
            e[cr] = 0
            e.smooth = True
            e.seam = False

        bm.to_mesh(obj.data)
        bm.clear()

    def clear_mesh_sharps(self, mesh):
        mesh.use_auto_smooth = False

        bm = bmesh.from_edit_mesh(mesh)
        bm.normal_update()

        bw = bm.edges.layers.bevel_weight.verify()
        cr = bm.edges.layers.crease.verify()

        # faltten all faces like in object mode
        for f in bm.faces:
            f.smooth = False

        for e in bm.edges:
            e[bw] = 0
            e[cr] = 0
            e.smooth = True
            e.seam = False

        bmesh.update_edit_mesh(mesh)


class ToggleAutoSmooth(bpy.types.Operator):
    bl_idname = "machin3.toggle_auto_smooth"
    bl_label = "Toggle Auto Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    angle: IntProperty(name="Auto Smooth Angle")

    @classmethod
    def description(cls, context, properties):
        if properties.angle == 0:
            return "Toggle Auto Smooth"
        else:
            return "Auto Smooth Angle Preset: %d" % (properties.angle)

    def execute(self, context):
        active = context.active_object

        if active:
            sel = context.selected_objects

            if active not in sel:
                sel.append(active)

            autosmooth = not active.data.use_auto_smooth if self.angle == 0 else True

            for obj in [obj for obj in sel if obj.type == 'MESH']:
                obj.data.use_auto_smooth = autosmooth

                if self.angle:
                    obj.data.auto_smooth_angle = radians(self.angle)

        return {'FINISHED'}
