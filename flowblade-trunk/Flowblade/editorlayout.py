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
from gi.repository import Gtk, Gdk
import cairo

import appconsts
import cairoarea
import editorpersistance
import editorstate
import guiutils
import dialogutils
import gui
import respaths

SELECTED_BG = (0.1, 0.31, 0.58,1.0)

# Edit panels.
PANEL_MEDIA = 0
PANEL_FILTERS = 1
PANEL_COMPOSITORS = 2
PANEL_RANGE_LOG = 3
PANEL_RENDERING = 4
PANEL_JOBS = 5
PANEL_PROJECT = 6
PANEL_PROJECT_SMALL_SCREEN = 7
PANEL_MEDIA_AND_BINS_SMALL_SCREEN = 8

# Layout containers where panels go as user decides.
CONTAINER_NOT_SET = 0
CONTAINER_T1 = 1
CONTAINER_T2 = 2
CONTAINER_B1 = 3
CONTAINER_L1 = 4
CONTAINER_L2 = 5
SMALL_CONTAINER_T = 6

# General window layouts.
DEFAULT_TWO_ROW = 0
LEFT_COLUMN_ONE_PANEL = 1
LEFT_COLUMN_TWO_PANELS = 2

# Default panel containers general layouts
DEFAULT_CONTAINERS = {  DEFAULT_TWO_ROW: {  PANEL_MEDIA: CONTAINER_T1, PANEL_RANGE_LOG: CONTAINER_T1, 
                                            PANEL_FILTERS: CONTAINER_T1, PANEL_COMPOSITORS: CONTAINER_T1, 
                                            PANEL_JOBS: CONTAINER_T1, PANEL_RENDERING: CONTAINER_T1,
                                            PANEL_PROJECT: SMALL_CONTAINER_T, PANEL_PROJECT_SMALL_SCREEN: None, 
                                            PANEL_MEDIA_AND_BINS_SMALL_SCREEN: CONTAINER_NOT_SET
                                         },
                        LEFT_COLUMN_ONE_PANEL: {    PANEL_MEDIA: CONTAINER_L1, PANEL_FILTERS: CONTAINER_T1,
                                                    PANEL_COMPOSITORS: CONTAINER_T1, PANEL_RANGE_LOG: CONTAINER_T1, 
                                                    PANEL_RENDERING: CONTAINER_T1, PANEL_JOBS: CONTAINER_T1, 
                                                    PANEL_PROJECT: CONTAINER_L1, PANEL_PROJECT_SMALL_SCREEN: CONTAINER_T1, 
                                                    PANEL_MEDIA_AND_BINS_SMALL_SCREEN: CONTAINER_NOT_SET
                                               },
                        LEFT_COLUMN_TWO_PANELS: {   PANEL_MEDIA: CONTAINER_T1, PANEL_FILTERS: CONTAINER_T1,
                                                    PANEL_COMPOSITORS: CONTAINER_T1, PANEL_RANGE_LOG: CONTAINER_T1, 
                                                    PANEL_RENDERING: CONTAINER_T1, PANEL_JOBS: CONTAINER_T1, 
                                                    PANEL_PROJECT: SMALL_CONTAINER_T, PANEL_PROJECT_SMALL_SCREEN: CONTAINER_T1, 
                                                    PANEL_MEDIA_AND_BINS_SMALL_SCREEN: CONTAINER_NOT_SET
                                               },
                    } # end DEFAULT_CONTAINERS

# Layout items
TOP_ROW_LAYOUT_DEFAULT_THREE = 0
TOP_ROW_LAYOUT_MONITOR_CENTER_THREE = 1
TOP_ROW_LAYOUT_TWO_ONLY = 2
BOTTOM_ROW_LAYOUT_TLINE_ONLY = 3
BOTTOM_ROW_LAYOUT_PANEL_LEFT = 4
BOTTOM_ROW_LAYOUT_PANEL_RIGHT = 5
LEFT_COLUMN_TWO_TOP_W1 = 6 # Left column with two panels on top row, editor panel and monitor, single window
LEFT_COLUMN_MONITOR_ONLY_W1 = 7  # Left column with monitor only on top row, single window

# Selection GUI
WINDOW_LAYOUT_SELECTION = 0
TOP_ROW_SELECTION = 1
BOTTOM_ROW_ROW_SELECTION = 2

LAYOUT_IMAGES = {   TOP_ROW_LAYOUT_DEFAULT_THREE:"layout_t_default",
                    TOP_ROW_LAYOUT_MONITOR_CENTER_THREE:"layout_t_monitor_center",
                    TOP_ROW_LAYOUT_TWO_ONLY:"layout_t_two_only",
                    BOTTOM_ROW_LAYOUT_TLINE_ONLY:"layout_b_tline_only",
                    BOTTOM_ROW_LAYOUT_PANEL_LEFT:"layout_b_panel_left",
                    BOTTOM_ROW_LAYOUT_PANEL_RIGHT:"layout_b_panel_right",
                    LEFT_COLUMN_TWO_TOP_W1:"layout_l_w1_two_top",
                    LEFT_COLUMN_MONITOR_ONLY_W1:"layout_l_w1_monitor_only"}

LAYOUT_ITEM_WIDTH = 150
LAYOUT_ITEM_HEIGHT = 100

# These are set on dialog launch when translations quaranteed to be initialized.
PANELS_DATA = None
CONTAINERS_NAMES = None
GENERAL_LAYOUT_NAMES = None

# GUI components
_select_rows = None


# Single and two window modes and different screen sizes have different selection of possible layouts available.
# Available layouts are determined at dialog launch.
_available_general_layouts = None # two row or one or two panel left column
_available_layouts = None

# Main edited data structure
_window_layout_data = None

# Dict panel_id -> (notebook, page_index)
_panels_locations = None

# --------------------------------------------------------------- LAYOUT SAVED DATA
class WindowLayoutData:
    def __init__(self):
        self.window_layout = DEFAULT_TWO_ROW
        
        self.top_row_layout = TOP_ROW_LAYOUT_DEFAULT_THREE
        self.bottom_row_layout = BOTTOM_ROW_LAYOUT_TLINE_ONLY
        
        self.panels_containers = DEFAULT_CONTAINERS[DEFAULT_TWO_ROW]

        
# --------------------------------------------------------------- DIALOG GUI
def show_configuration_dialog():
    global PANELS_DATA, CONTAINERS_NAMES, GENERAL_LAYOUT_NAMES
    
    PANELS_DATA = { PANEL_MEDIA: (True, _("Media Panel")),
                    PANEL_FILTERS: (True,_("Filters Panel")),
                    PANEL_COMPOSITORS: (True,_("Compositors Panel")),
                    PANEL_RANGE_LOG:(True, _("Range Log Panel")),
                    PANEL_RENDERING:(True, _("Render Panel")),
                    PANEL_JOBS: (True,_("Jobs panel")),
                    PANEL_PROJECT: (True, _("Project Panel")),
                    PANEL_PROJECT_SMALL_SCREEN: (True, _("Project Panel Small Screen")),
                    PANEL_MEDIA_AND_BINS_SMALL_SCREEN: (True, _("Media and Binss Panel Small Screen")) }

    CONTAINERS_NAMES = {CONTAINER_T1: _("Top Row 1"),
                        CONTAINER_T2: _("Top Row 2"),
                        CONTAINER_B1: _("Bottom Row 1"),
                        CONTAINER_L1: _("Left Column 1"),
                        CONTAINER_L2: _("Left Column 2"),
                        SMALL_CONTAINER_T: _("Top Small Panel"),
                        CONTAINER_NOT_SET: _("Container Not Set")}

    GENERAL_LAYOUT_NAMES = {DEFAULT_TWO_ROW: _("Default Two Row"),
                            LEFT_COLUMN_ONE_PANEL: _("Left Column - One Panel"),
                            LEFT_COLUMN_TWO_PANELS: _("Left Column - Two Panels")}

    global _available_general_layouts
    _available_general_layouts = [DEFAULT_TWO_ROW, LEFT_COLUMN_ONE_PANEL, LEFT_COLUMN_TWO_PANELS]

    global _window_layout_data
    _window_layout_data = WindowLayoutData() # TODO: From editorpersistance.py

    dialog = Gtk.Dialog(_("Editor Preferences"), None,
                    Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    (_("Cancel"), Gtk.ResponseType.REJECT,
                    _("OK"), Gtk.ResponseType.ACCEPT))

    panel = _get_edit_panel()

    dialog.connect('response', _configuration_dialog_callback)
    dialog.vbox.pack_start(panel, True, True, 0)
    dialogutils.set_outer_margins(dialog.vbox)
    dialogutils.default_behaviour(dialog)
    dialog.set_transient_for(gui.editor_window.window)
    dialog.show_all()

def _configuration_dialog_callback(dialog, response_id):

    if response_id == Gtk.ResponseType.ACCEPT:
        #editorpersistance.save()
        dialog.destroy()

        return

    dialog.destroy()

    

def _get_edit_panel():
    layout_select_combo = Gtk.ComboBoxText()
    for layout in _available_general_layouts:
        layout_select_combo.append_text(GENERAL_LAYOUT_NAMES[layout])
    layout_select_combo.set_active(0)
    layout_select_combo.connect('changed', lambda w: _general_layout_changed(w))
    
    global layout_selection_stack
    layout_selection_stack = Gtk.Stack.new()
    
    if DEFAULT_TWO_ROW in _available_general_layouts:
        top_row = LayoutSelectRow(TOP_ROW_SELECTION, selection_changed_callback)
        top_row.add_selection_item(LayoutSelectItem(TOP_ROW_LAYOUT_DEFAULT_THREE))
        top_row.add_selection_item(LayoutSelectItem(TOP_ROW_LAYOUT_MONITOR_CENTER_THREE))
        top_row.add_selection_item(LayoutSelectItem(TOP_ROW_LAYOUT_TWO_ONLY))
        top_row.set_default_selection(LayoutSelectItem(TOP_ROW_LAYOUT_DEFAULT_THREE))
        
        bottom_row = LayoutSelectRow(BOTTOM_ROW_ROW_SELECTION, selection_changed_callback)
        bottom_row.add_selection_item(LayoutSelectItem(BOTTOM_ROW_LAYOUT_TLINE_ONLY))
        bottom_row.add_selection_item(LayoutSelectItem(BOTTOM_ROW_LAYOUT_PANEL_LEFT))
        bottom_row.add_selection_item(LayoutSelectItem(BOTTOM_ROW_LAYOUT_PANEL_RIGHT))
        bottom_row.set_default_selection(LayoutSelectItem(BOTTOM_ROW_LAYOUT_TLINE_ONLY))
    
        stack_panel = Gtk.VBox(False, 2)

        stack_panel.pack_start(guiutils.bold_label(_("Top Row Layout")), False, False, 0)
        stack_panel.pack_start(top_row.widget, False, False, 0)
        stack_panel.pack_start(guiutils.bold_label(_("Bottom Row Layout")), False, False, 0)
        stack_panel.pack_start(bottom_row.widget, False, False, 0)

        layout_selection_stack.add_named(stack_panel, str(DEFAULT_TWO_ROW))

    if LEFT_COLUMN_ONE_PANEL in _available_general_layouts:
        middle_row = LayoutSelectRow(WINDOW_LAYOUT_SELECTION, selection_changed_callback)
        middle_row.add_selection_item(LayoutSelectItem(LEFT_COLUMN_TWO_TOP_W1))
        middle_row.add_selection_item(LayoutSelectItem(LEFT_COLUMN_MONITOR_ONLY_W1))
        middle_row.set_default_selection(LayoutSelectItem(LEFT_COLUMN_TWO_TOP_W1))
        
        stack_panel = Gtk.VBox(False, 2)
        stack_panel.pack_start(Gtk.Label(), True, True, 0)
        stack_panel.pack_start(middle_row.widget, False, False, 0)
        stack_panel.pack_start(Gtk.Label(), True, True, 0)
        
        layout_selection_stack.add_named(stack_panel, str(LEFT_COLUMN_ONE_PANEL))
        
    layout_selection_stack.set_visible_child_name(str(DEFAULT_TWO_ROW))

    available_containers = [CONTAINER_T1, CONTAINER_T2, CONTAINER_B1, CONTAINER_L1, CONTAINER_L2, SMALL_CONTAINER_T, CONTAINER_NOT_SET]

    global _select_rows
    _select_rows = {}
    
    container_select_panel = Gtk.VBox(False, 2)
    for panel in PANELS_DATA:
        select_row = PanelContainerSelect(panel, available_containers)
        container_select_panel.pack_start(select_row.widget, False, False, 0)
        _select_rows[panel] = select_row # These need to be available for setting default containers when changing general layout.
        
    pane = Gtk.VBox(False, 2)
    pane.pack_start(layout_select_combo, False, False, 0)
    pane.pack_start(layout_selection_stack, False, False, 0)
    pane.pack_start(container_select_panel, False, False, 0)

    return pane


class LayoutSelectRow:
    def __init__(self, selection_target, selection_changed_callback):
        self.selection_target = selection_target
        self.selection_items = []
        self.selection_changed_callback = selection_changed_callback
        
        self.widget = Gtk.HBox(False, 2)
        
    def add_selection_item(self, item):
        self.selection_items.append(item)
        self.widget.pack_start(item.widget, False, False, 0)
        
        item.set_change_listener(self)

    def set_default_selection(self, item):
        for test_item in self.selection_items:
            if test_item.layout == item.layout:
                test_item.selected = True

    def item_selected(self, layout):
        for item in self.selection_items:
            if item.layout == layout:
                item.selected = True
            else:
                item.selected = False
            item.widget.queue_draw()
    
        self.selection_changed_callback(self.selection_target, layout)


class LayoutSelectItem:

    def __init__(self, layout):
        self.widget = cairoarea.CairoDrawableArea2(LAYOUT_ITEM_WIDTH, LAYOUT_ITEM_HEIGHT, self._draw)
        self.widget.press_func = self._press
        self.layout = layout
        image_path = respaths.IMAGE_PATH + LAYOUT_IMAGES[layout] + ".png"
        self.layout_image_surface = cairo.ImageSurface.create_from_png(image_path)
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
            color = SELECTED_BG
        else:
            color = gui.get_bg_color()

        cr.set_source_rgba(*color)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        # Draw layout img
        cr.set_source_surface(self.layout_image_surface, 0, 0)
        cr.paint()


class PanelContainerSelect:
    
    def __init__(self, panel, available_containers):
        self.panel = panel
        available_containers = available_containers
        
        always_visible, name = PANELS_DATA[panel]
        
        self.container_select_combo = Gtk.ComboBoxText()
        self.selection_values = []
        # dis needs changing ???
        #if always_visible == False:
        #    self.container_select_combo.append_text(_("Not shown"))
        #    self.selection_values.append(None)

        for container in available_containers:
            self.selection_values.append(container)
            self.container_select_combo.append_text(CONTAINERS_NAMES[container])

        self.container_select_combo.set_active(0)
        
        self.widget = Gtk.HBox(False, 2)
        self.widget.pack_start(guiutils.get_right_justified_box([Gtk.Label(label=name)]), False, False, 0)
        self.widget.pack_start(self.container_select_combo, False, False, 0)
        
    def set_container(self, container):
        selection = self.selection_values.index(container)
        self.container_select_combo.set_active(selection)
        

# ----------------------------------------------------------------------- CHANGING LAYOUT DATA
def _general_layout_changed(combo):
    general_layout = _available_general_layouts[combo.get_active()]
    layout_selection_stack.set_visible_child_name(str(general_layout))
    
    default_containers = DEFAULT_CONTAINERS[general_layout]
    
    for panel in default_containers:
        container = default_containers[panel]
        select_row = _select_rows[panel]
        select_row.set_container(container)

def selection_changed_callback(selection_target, layout):
    print(selection_target, layout)


# ------------------------------------------------------------------ APPLYING LAYOUT
# @self -- editorwindow.EditorWindow
def do_window_layout(self):

    global _window_layout_data
    _window_layout_data = WindowLayoutData() # TODO: From editorpersistance.py
    
    # Dict panel_id -> panel_object
    panels = {  PANEL_MEDIA: self.mm_panel,
                PANEL_FILTERS: self.effects_panel,
                PANEL_COMPOSITORS: self.compositors_panel,
                PANEL_RANGE_LOG: self.media_log_panel,
                PANEL_RENDERING: self.render_panel,
                PANEL_JOBS: self.jobs_pane,
                PANEL_PROJECT: self.top_project_panel,
                PANEL_PROJECT_SMALL_SCREEN: None,
                PANEL_MEDIA_AND_BINS_SMALL_SCREEN: None}

    if top_level_project_panel() == False:
        panels[PANEL_PROJECT_SMALL_SCREEN] = self.small_screen_project_panel

    # Dict panel_id -> panel_name
    panel_names = { PANEL_MEDIA: _("Media"),
                    PANEL_FILTERS: _("Filters"),
                    PANEL_COMPOSITORS: _("Compositors"),
                    PANEL_RANGE_LOG: _("Range Log"),
                    PANEL_RENDERING : _("Project"),
                    PANEL_JOBS: _("Jobs"),
                    PANEL_PROJECT: None,
                    PANEL_PROJECT_SMALL_SCREEN: None,
                    PANEL_MEDIA_AND_BINS_SMALL_SCREEN: None}

    # Notebook a.k.a CONTAINER_T1. TODO: Make this work like all other containers
    self.notebook = Gtk.Notebook()
    self.notebook.set_size_request(appconsts.NOTEBOOK_WIDTH, appconsts.TOP_ROW_HEIGHT)

    notebook_vbox = Gtk.VBox(False, 1)
    notebook_vbox.pack_start(self.notebook, True, True, 0)
    
    # Create dict container_id -> list of panels in that container
    all_containers = {CONTAINER_T1, CONTAINER_T2, CONTAINER_B1, CONTAINER_L1, CONTAINER_L2}
    container_panels = {}
    for cont in all_containers:
        panels_list = []
        for panel in _window_layout_data.panels_containers:
            set_cont = _window_layout_data.panels_containers[panel]
            if set_cont == cont:
                panels_list.append(panel)
        container_panels[cont] = panels_list
    
    print(container_panels)

    # Create dicts:
    #             container_id -> container_gui_object
    #             container_id -> container_notebook
    gui_containers = {}
    gui_notebooks = {}
    for cont in all_containers:
        panels_list = container_panels[cont]
        if len(panels_list) == 0:
            gui_container = None
            gui_notebook = None
        else:
            notebook = Gtk.Notebook()
            notebook.set_size_request(appconsts.NOTEBOOK_WIDTH, appconsts.TOP_ROW_HEIGHT)

            container_notebook_vbox = Gtk.VBox(False, 1)
            container_notebook_vbox.pack_start(notebook, True, True, 0)

            gui_container = container_notebook_vbox
            gui_notebook = notebook
            
        gui_containers[cont] = gui_container
        gui_notebooks[cont] = gui_notebook


    # Temp fix for hardcoded notebook
    gui_containers[CONTAINER_T1] = notebook_vbox
    gui_notebooks[CONTAINER_T1] = self.notebook


    # Fill containers
    global _panels_locations
    _panels_locations = {}
    for cont in gui_notebooks:
        notebook = gui_notebooks[cont]
        if notebook == None:
            continue
        panels_list = container_panels[cont]
        page_index = 0
        for panel in panels_list:
            panel_object = panels[panel]
            panel_name = panel_names[panel]

            notebook.append_page(panel_object, Gtk.Label(label=panel_name))
            _panels_locations[panel] = (notebook, page_index)
            page_index += 1
        
    """
    media_label = Gtk.Label(label=_("Media"))
    if editorpersistance.prefs.global_layout == appconsts.SINGLE_WINDOW:
        self.notebook.append_page(self.mm_panel, media_label)
    self.notebook.append_page(self.media_log_panel, Gtk.Label(label=_("Range Log")))
    self.notebook.append_page(self.effects_panel, Gtk.Label(label=_("Filters")))
    self.notebook.append_page(self.compositors_panel, Gtk.Label(label=_("Compositors")))
    if top_level_project_panel() == False:
        self.notebook.append_page(self.small_screen_project_panel, Gtk.Label(label=_("Project")))

    self.notebook.append_page(self.jobs_pane, Gtk.Label(label=_("Jobs")))
    self.notebook.append_page(self.render_panel, Gtk.Label(label=_("Render")))
    self.notebook.set_tab_pos(Gtk.PositionType.BOTTOM)
    """
    

    
    # Top row paned
    self.top_paned = Gtk.HPaned()
    if editorpersistance.prefs.global_layout == appconsts.SINGLE_WINDOW:
        self.top_paned.pack1(notebook_vbox, resize=False, shrink=False)
        self.top_paned.pack2(self.monitor_frame, resize=True, shrink=False)
    else:
        self.top_paned.pack1(self.mm_panel, resize=False, shrink=False)
        self.top_paned.pack2(notebook_vbox, resize=True, shrink=False)

    # Top row
    self.top_row_hbox = Gtk.HBox(False, 0)
    if top_level_project_panel() == True:
        self.top_row_hbox.pack_start(self.top_project_panel, False, False, 0)
    self.top_row_hbox.pack_start(self.top_paned, True, True, 0)
    self._update_top_row()
    
    # Timeline bottom row
    tline_hbox_3 = Gtk.HBox()
    tline_hbox_3.pack_start(self.left_corner.widget, False, False, 0)
    tline_hbox_3.pack_start(self.tline_scroller, True, True, 0)

    # Timeline hbox
    tline_vbox = Gtk.VBox()
    tline_vbox.pack_start(self.tline_hbox_1, False, False, 0)
    tline_vbox.pack_start(self.tline_hbox_2, True, True, 0)
    tline_vbox.pack_start(self.tline_renderer_hbox, False, False, 0)
    tline_vbox.pack_start(tline_hbox_3, False, False, 0)

    # Timeline box
    self.tline_box = Gtk.HBox()
    self.tline_box.pack_start(tline_vbox, True, True, 0)

    # Timeline pane
    tline_pane = Gtk.VBox(False, 1)
    tline_pane.pack_start(self.edit_buttons_frame, False, True, 0)
    tline_pane.pack_start(self.tline_box, True, True, 0)
    self.tline_pane = tline_pane

    # VPaned top row / timeline
    self.app_v_paned = Gtk.VPaned()
    self.app_v_paned.pack1(self.top_row_hbox, resize=False, shrink=False)
    self.app_v_paned.pack2(tline_pane, resize=True, shrink=False)
    self.app_v_paned.no_dark_bg = True
    
    # Pane
    self.pane.pack_start(self.menu_vbox, False, True, 0)
    self.pane.pack_start(self.app_v_paned, True, True, 0)

    # Show Monitor Window in two window mode
    if editorpersistance.prefs.global_layout != appconsts.SINGLE_WINDOW:
        pane2 = Gtk.VBox(False, 1)
        pane2.pack_start(top_row_window_2, False, False, 0)
        pane2.pack_start(monitor_frame, True, True, 0)

        # Set pane and show window
        self.window2.add(pane2)
        self.window2.set_title("Flowblade")

        # Maximize if it seems that we exited maximized, else set size
        w, h, x, y = editorpersistance.prefs.exit_allocation_window_2

        if w != 0: # non-existing prefs file causes w and h to be 0
            if (float(w) / editorstate.SCREEN_WIDTH > 0.95) and (float(h) / editorstate.SCREEN_HEIGHT > 0.95):
                self.window2.maximize()
            else:
                self.window2.resize(w, h)

        self.window2.move(x, y)
        self.window2.show_all()

def top_level_project_panel():
    if editorpersistance.prefs.top_row_layout == appconsts.ALWAYS_TWO_PANELS:
        return False
    if editorpersistance.prefs.top_level_project_panel == True and editorstate.SCREEN_WIDTH > 1440 and editorstate.SCREEN_HEIGHT > 898:
        return True

    return False


# ----------------------------------------------------------------- showing panels programmatically 
def show_compositor_editor():
    _show_panel(PANEL_COMPOSITORS) 

def show_filter_editor():
    _show_panel(PANEL_FILTERS) 

def show_jobs_panel():
    _show_panel(PANEL_JOBS) 

def show_range_log():
    _show_panel(PANEL_FILTERS) 

def show_first_panels():
    # TODO
    gui.middle_notebook.set_current_page(0)

def _show_panel(panel):
    notebook, page_index = _panels_locations[panel]
    notebook.set_current_page(page_index)
