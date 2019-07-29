"""
    Flowblade Movie Editor is a nonlinear video editor.
    Copyright 2014 Janne Liljeblad.

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
    along with Flowblade Movie Editor. If not, see <http://www.gnu.org/licenses/>.
"""

from gi.repository import Gtk, Gdk, Pango

import cairo
import mlt
import os

import appconsts
import cairoarea
import editorstate
import guiutils
import mltfilters
import respaths

OUT_FOLDER = "/home/janne/codes/docs/Flowblade/art/effimgs/"

SOURCE_IMGS = ["/home/janne/codes/docs/Flowblade/art/eff_img_source1.png"]

EFFECT_ITEM = 0

ITEM_WIDTH = appconsts.THUMB_WIDTH
ITEM_HEIGHT = appconsts.THUMB_HEIGHT


# ---------------------------------------------------------- interface
def get_test_panel():
    stack_panel = Gtk.Stack()
    panels = []
    for group in mltfilters.groups:
        name, finfos = group

        group_panel = ItemGroupPanel(finfos)
        group_panel.create_widgets()
        
        panels.append(group_panel)

        stack_panel.add_named(group_panel.widget, name)

    stack_panel.set_visible_child(panels[3].widget)
    
    view = Gtk.Viewport()
    view.add(stack_panel)
    view.set_shadow_type(Gtk.ShadowType.NONE)

    effects_scroll_window = Gtk.ScrolledWindow()
    effects_scroll_window.add(view)
    effects_scroll_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    effects_scroll_window.set_size_request(600, 250)
    effects_scroll_window.show_all()
        
    return effects_scroll_window


# -------------------------------------------- media select panel
class ItemGroupPanel():

    def __init__(self, group):
        self.widget = Gtk.VBox()
        self.group = group
        self.row_widgets = []
        self.selected_object = None
        self.columns = 4
        #self.double_click_cb = double_click_cb

    def get_selected_media_object(self):
        return self.selected_object

    def item_selected(self, item, widget, event):
        print "item selected"

    """
    def media_object_selected(self, media_object, widget, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            self.double_click_release = True
            self.clear_selection()
            media_object.widget.override_background_color(Gtk.StateType.NORMAL, gui.get_selected_bg_color())
            self.selected_objects.append(media_object)
            self.widget.queue_draw()
            gui.pos_bar.widget.grab_focus()
            GLib.idle_add(self.double_click_cb, media_object.media_file)
            return

        # HACK! We're using event times to exclude double events when icon is pressed
        now = time.time()
        if (now - self.last_event_time) < 0.05:
            self.last_event_time = now
            return
        self.last_event_time = now

        widget.grab_focus()

        if event.button == 1:
            if (event.get_state() & Gdk.ModifierType.CONTROL_MASK):
                
                # add to selected if not there
                try:
                    index = self.selected_objects.index(media_object)
                except:
                    self.selected_objects.append(media_object)
                    media_object.widget.override_background_color(Gtk.StateType.NORMAL, gui.get_selected_bg_color())
                    self.last_ctrl_selected_media_object = media_object
                    return
            elif (event.get_state() & Gdk.ModifierType.SHIFT_MASK) and len(self.selected_objects) > 0:
                # Get data on current selection and pressed media object
                first_selected = -1
                last_selected = -1
                pressed_widget = -1
                for i in range(0, len(current_bin().file_ids)):
                    file_id = current_bin().file_ids[i]
                    m_file = PROJECT().media_files[file_id]
                    m_obj = self.widget_for_mediafile[m_file]
                    if m_obj in self.selected_objects:
                        selected = True
                    else:
                        selected = False
                    
                    if selected and first_selected == -1:
                        first_selected = i
                    if selected:
                        last_selected = i
                    if media_object == m_obj:
                        pressed_widget = i
                
                # Get new selection range
                if pressed_widget < first_selected:
                    sel_range = (pressed_widget, first_selected)
                elif pressed_widget > last_selected:
                    sel_range = (last_selected, pressed_widget)
                else:
                    sel_range = (pressed_widget, pressed_widget)
                    
                self.clear_selection()
                
                # Select new range
                start, end = sel_range
                for i in range(start, end + 1):
                    file_id = current_bin().file_ids[i]
                    m_file = PROJECT().media_files[file_id]
                    m_obj = self.widget_for_mediafile[m_file]
                    
                    self.selected_objects.append(m_obj)
                    m_obj.widget.override_background_color(Gtk.StateType.NORMAL, gui.get_selected_bg_color())
            else:
                self.clear_selection()
                media_object.widget.override_background_color(Gtk.StateType.NORMAL, gui.get_selected_bg_color())
                self.selected_objects.append(media_object)


        self.widget.queue_draw()
        """
    
    """
    def release_on_media_object(self, media_object, widget, event):
        if self.last_ctrl_selected_media_object == media_object:
            self.last_ctrl_selected_media_object = None
            return
        
        if not self.double_click_release:
            widget.grab_focus()
        else:
            self.double_click_release = False # after double click we want bos bar to have focus
            
        if event.button == 1:
            if (event.get_state() & Gdk.ModifierType.CONTROL_MASK):
                # remove from selected if already there
                try:
                    index = self.selected_objects.index(media_object)
                    self.selected_objects.remove(media_object)
                    media_object.widget.override_background_color(Gtk.StateType.NORMAL, gui.get_bg_color())
                except:
                    pass
    """

    def select_media_file(self, media_file):
        self.clear_selection()
        self.selected_objects.append(self.widget_for_mediafile[media_file])

    def update_selected_bg_colors(self):
        bg_color = gui.get_selected_bg_color()
        for media_object in self.selected_objects:
            media_object.widget.override_background_color(Gtk.StateType.NORMAL, bg_color)




    def clear_selection(self):
        self.selected_object.widget.override_background_color(Gtk.StateType.NORMAL, bg_color)
        self.selected_object = None


    def create_widgets(self):
        for w in self.row_widgets:
            self.widget.remove(w)
        self.row_widgets = []
        self.widget_for_effect = {}
        self.selected_objects = None

        column = 0

        row_box = Gtk.HBox()
        #dnd.connect_media_drop_widget(row_box)
        row_box.set_size_request(ITEM_WIDTH * self.columns, ITEM_HEIGHT)
        for filter_info in self.group:
            
            item_widget = ItemDNDWidget(filter_info, EFFECT_ITEM, self.item_selected)
            #dnd.connect_media_files_object_widget(effect_widget.widget)
            #dnd.connect_media_files_object_cairo_widget(effect_widget.img)
            
            #self.widget_for_mediafile[media_file] = media_object
            row_box.pack_start(item_widget.widget, False, False, 0)
            column += 1
            if column == self.columns:
                filler = self._get_empty_filler()
                row_box.pack_start(filler, True, True, 0)
                self.widget.pack_start(row_box, False, False, 0)
                self.row_widgets.append(row_box)
                row_box = Gtk.HBox()
                column = 0

        if column != 0:
            filler = self._get_empty_filler()
            #dnd.connect_media_drop_widget(filler)
            row_box.pack_start(filler, True, True, 0)
            self.widget.pack_start(row_box, False, False, 0)
            self.row_widgets.append(row_box)

        filler = self._get_empty_filler()
        # dnd.connect_media_drop_widget(filler)
        self.row_widgets.append(filler)
        self.widget.pack_start(filler, True, True, 0)

        self.widget.show_all()

    def _get_empty_filler(self):
        return Gtk.Label()
        """
        filler = Gtk.EventBox()
        filler.connect("button-press-event", lambda w,e: self.empty_pressed(w,e))
        if widget == None:
            filler.add(Gtk.Label())
        else:
            filler.add(widget)
        return filler
        """
    
    
class ItemDNDWidget:

    def __init__(self, item_data, item_type, selected_callback):
        self.item_data = item_data
        self.selected_callback = selected_callback

        self.widget = Gtk.EventBox()
        #self.widget.connect("button-press-event", lambda w,e: selected_callback(self, w, e))
        #self.widget.connect("button-release-event", lambda w,e: release_callback(self, w, e))
        #self.widget.dnd_media_widget_attr = True # this is used to identify widget at dnd drop
        self.widget.set_can_focus(True)
        self.widget.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.vbox = Gtk.VBox()

        if item_type == EFFECT_ITEM:
            try:
                self.icon = cairo.ImageSurface.create_from_png(respaths.EFFECTS_ICONS_PATH + item_data.mlt_service_id + ".png")
            except:
                icon_path = respaths.IMAGE_PATH + "audio_file.png"
                self.icon = cairo.ImageSurface.create_from_png(icon_path)
                
            txt = Gtk.Label(label=item_data.name)

        # more cases here later
        
        self.img = cairoarea.CairoDrawableArea2(ITEM_WIDTH, ITEM_HEIGHT, self._draw_icon)
        self.img.press_func = self._press

        txt.modify_font(Pango.FontDescription("sans 9"))
        txt.set_max_width_chars(13)
        txt.set_ellipsize(Pango.EllipsizeMode.END)

        self.vbox.pack_start(self.img, True, True, 0)
        self.vbox.pack_start(txt, False, False, 0)

        self.align = guiutils.set_margins(self.vbox, 6, 6, 6, 6)

        self.widget.add(self.align)


    def _press(self, event):
        self.selected_callback(self, self.widget, event)

    def _draw_icon(self, event, cr, allocation):
        x, y, w, h = allocation
        cr.set_source_surface(self.icon, 0, 0)
        cr.paint()

        cr.select_font_face ("sans-serif",
                 cairo.FONT_SLANT_NORMAL,
                 cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(9)


        #cr.set_source_rgba(0,0,0,0.5)
        #cr.rectangle(28,75,62,12)
        #cr.fill()
            
        #cr.move_to(30, 84)
        ##cr.set_source_rgb(1, 1, 1)
        #media_length = utils.get_tc_string(self.media_file.length)
        #cr.show_text(str(media_length))
            

            
# -------------------------------------------------------------------------- image creation helpers    
def write_out_eff_imgs():
    create_effect_icons(OUT_FOLDER)
    """
    profile = editorstate.PROJECT().profile
    print profile
    for src_img in SOURCE_IMGS:
        print src_img
        for group_tuple in mltfilters.groups:
            gkey, effect_group = group_tuple
            if gkey == "Audio" or gkey == "Audio Filter":
                continue
                
            for filter_info in effect_group:
                 write_image(profile, src_img, filter_info)
    """
    
def write_image(profile, source_path, filter_info):

    # Create consumer
    print "writing " + filter_info.mlt_service_id + "..."
    out_img_path = OUT_FOLDER + filter_info.mlt_service_id + ".png"
    out_img_path_stripped = out_img_path.replace(" ", "")
    print out_img_path_stripped
    consumer = mlt.Consumer(profile, "avformat", str(out_img_path_stripped))
    consumer.set("real_time", 0)
    consumer.set("vcodec", "png")

    # Create one frame producer with filter
    producer = mlt.Producer(profile, str(source_path))
    length = producer.get_length()
    frame = length / 2
    producer = producer.cut(frame, frame)

    fobj = mltfilters.FilterObject(filter_info)
    fobj.create_mlt_filter(profile)
    producer.attach(fobj.mlt_filter)

    # Connect and write image
    consumer.connect(producer)
    consumer.run()
    
def create_effect_icons(folder):
    for f in os.listdir(folder):
        large_img_path = folder + f
        icon = _create_image_surface(large_img_path)
        icon_file_path = respaths.EFFECTS_ICONS_PATH + f
        icon.write_to_png(icon_file_path)

def _create_image_surface(icon_path):
    icon = cairo.ImageSurface.create_from_png(icon_path)
    scaled_icon = cairo.ImageSurface(cairo.FORMAT_ARGB32, appconsts.THUMB_WIDTH, appconsts.THUMB_HEIGHT)
    cr = cairo.Context(scaled_icon)
    cr.scale(float(appconsts.THUMB_WIDTH) / float(icon.get_width()), float(appconsts.THUMB_HEIGHT) / float(icon.get_height()))
    cr.set_source_surface(icon, 0, 0)
    cr.paint()
    
    return scaled_icon
    
