"""
    Flowblade Movie Editor is a nonlinear video editor.
    Copyright 2012 Janne Liljeblad.

    This file is part of Flowblade Movie Editor <http://code.google.com/p/flowblade>.

    Flowblade Movie Editor is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Flowblade Movie Editor is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Flowblade Movie Editor.  If not, see <http://www.gnu.org/licenses/>.
"""

import cairoarea

TOP_ROW_LAYOUT_DEFAULT_THREE = 0
TOP_ROW_LAYOUT_MONITOR_CENTER_THREE = 1
TOP_ROW_LAYOUT_TWO_ONLY = 2
BOTTOM_ROW_LAYOUT_TLINE_ONLY = 3
BOTTOM_ROW_LAYOUT_PANEL_LEFT = 4
BOTTOM_ROW_LAYOUT_PANEL_RIGHT = 5

LAYOUT_IMAGES = {   TOP_ROW_LAYOUT_DEFAULT_THREE:"layout_t_default",
                    TOP_ROW_LAYOUT_MONITOR_CENTER_THREE:"layout_t_monitor_center",
                    TOP_ROW_LAYOUT_TWO_ONLY:"layout_t_two_only",
                    BOTTOM_ROW_LAYOUT_TLINE_ONLY:"layout_b_tline_only",
                    BOTTOM_ROW_LAYOUT_PANEL_LEFT:"layout_b_panel_left",
                    BOTTOM_ROW_LAYOUT_PANEL_RIGHT:"layout_b_panel_right"}

LAYOUT_ITEM_WIDTH = 150
LAYOUT_ITEM_HEIGHT = 100

# These are set on dialog launch when required data quaranteed available.
SELECTED_COLOR = None
BG_COLOR = None
            

def preferences_dialog():


    dialog = Gtk.Dialog(_("Editor Preferences"), None,
                    Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    (_("Cancel"), Gtk.ResponseType.REJECT,
                    _("OK"), Gtk.ResponseType.ACCEPT))

    panel = _get_edit_panel()

    dialog.connect('response', _preferences_dialog_callback)
    dialog.vbox.pack_start(panel, True, True, 0)
    dialogutils.set_outer_margins(dialog.vbox)
    dialogutils.default_behaviour(dialog)
    # Jul-2016 - SvdB - The next line is to get rid of the message "GtkDialog mapped without a transient parent. This is discouraged."
    dialog.set_transient_for(gui.editor_window.window)
    dialog.show_all()



def _preferences_dialog_callback(dialog, response_id):

    if response_id == Gtk.ResponseType.ACCEPT:
        editorpersistance.save()
        dialog.destroy()

        return

    dialog.destroy()


def _get_edit_panel():
    vbox = Gtk.VBox(False, 2)
        
    vbox.pack_start(row9, False, False, 0)

    return vbox


class LayoutSelectRow:
    def __init__(self, selection_changed_callback):
        
        self.selection_items = []
        self.selection_changed_callback = selection_changed_callback
        
        self.widget = Gtk.HBox(False, 2)
        
    def add_selection_item(self, item):
        self.selection_items.append(item)
        self.widget.pack_start(item.widget, False, False, 0)
        
        item.set_change_listener(self)
        
    def item_selected(self, layout):
        for item in selection_items:
            if item.layout == layout:
                item.selected = True
            else:
                item.selected = False
            item.widget.queue_draw()
    
        self.selection_changed_callback(layout)

class LayoutSelectItem:

    def __init__(self, layout):
        self.widget = cairoarea.CairoDrawableArea2(LAYOUT_ITEM_WIDTH, LAYOUT_ITEM_HEIGHT, self._draw)
        self.widget.press_func = self._press
        self.layout = layout
        self.layout_image_surface = cairo.ImageSurface.create_from_png(respaths.IMAGE_PATH +  LAYOUT_IMAGES[layout] + ".png")
        self.change_listener = None
        self.selected = False

    def set_change_listener(self, change_listener):
        self.change_listener = change_listener

    def _press(self, event):
         self.change_listener.item_selected(self.layout)

    def _draw(self, event, cr, allocation):
        x, y, w, h = allocation

        # Draw bg
        if self.selected == True:
            color = SELECTED_COLOR
        else:
            color = BG_COLOR

        cr.set_source_rgb(*color)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        # Draw layout img
        cr.set_source_surface(self.layout_image_surface, 0, 0)
        cr.paint()
