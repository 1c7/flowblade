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

import cairo

from gi.repository import Gtk, GObject

import appconsts
import audiomonitoring
import batchrendering
import dialogutils
import editorpersistance
import editorstate
import glassbuttons
import gmic
import gui
import guicomponents
import guiutils
import respaths
import titler
import tlineaction
import updater
import undo
import workflow


# Middlebar buttons
MB_BUTTON_ZOOM_IN = 0
MB_BUTTON_ZOOM_OUT = 1
MB_BUTTON_ZOOM_FIT = 2
MB_BUTTON_UNDO = 3
MB_BUTTON_REDO = 4
MB_BUTTON_RENDERED_TRANSITION = 5
MB_BUTTON_CUT = 6
MB_BUTTON_RESYNC = 7
MB_BUTTON_SPLIT = 8
MB_BUTTON_SPLICE_OUT = 9
MB_BUTTON_LIFT = 10
MB_BUTTON_RIPPLE_DELETE = 11
MB_BUTTON_RANGE_DELETE = 12
MB_BUTTON_OVERWRITE_RANGE = 13
MB_BUTTON_OVERWRITE_CLIP = 14
MB_BUTTON_INSERT = 15
MB_BUTTON_APPEND = 16
MB_BUTTON_TOOL_MIXER = 17
MB_BUTTON_TOOL_TITLER = 18
MB_BUTTON_TOOL_BATCH = 19
MB_BUTTON_TOOL_GMIC = 20

# Button groups
BUTTON_GROUP_TOOLS = 0
BUTTON_GROUP_UNDO = 1
BUTTON_GROUP_ZOOM = 2
BUTTON_GROUP_EDIT = 3
BUTTON_GROUP_SYNC_SPLIT = 4
BUTTON_GROUP_DELETE = 5
BUTTON_GROUP_MONITOR_ADD = 6

# Button icons
ICONS = {   MB_BUTTON_ZOOM_IN:"zoom_in",
            MB_BUTTON_ZOOM_OUT:"zoom_out",
            MB_BUTTON_ZOOM_FIT:"zoom_length",
            MB_BUTTON_UNDO:"undo",
            MB_BUTTON_REDO:"redo",
            MB_BUTTON_RENDERED_TRANSITION:"dissolve",
            MB_BUTTON_CUT:"cut",
            MB_BUTTON_RESYNC:"resync",
            MB_BUTTON_SPLIT:"split_audio",
            MB_BUTTON_SPLICE_OUT:"splice_out",
            MB_BUTTON_LIFT:"lift",
            MB_BUTTON_RIPPLE_DELETE:"ripple_delete",
            MB_BUTTON_RANGE_DELETE:"delete_range",
            MB_BUTTON_OVERWRITE_RANGE:"overwrite_range",
            MB_BUTTON_OVERWRITE_CLIP:"overwrite_clip",
            MB_BUTTON_INSERT:"insert_clip",
            MB_BUTTON_APPEND:"append_clip",
            MB_BUTTON_TOOL_MIXER:"open_mixer",
            MB_BUTTON_TOOL_TITLER:"open_titler",
            MB_BUTTON_TOOL_BATCH:"open_renderqueue",
            MB_BUTTON_TOOL_GMIC:"open_gmic"}


# Default active values for buttons
DEFAULT_ACTIVE_STATES = {   MB_BUTTON_ZOOM_IN:True,
                            MB_BUTTON_ZOOM_OUT:True,
                            MB_BUTTON_ZOOM_FIT:True,
                            MB_BUTTON_UNDO:True,
                            MB_BUTTON_REDO:True,
                            MB_BUTTON_RENDERED_TRANSITION:True,
                            MB_BUTTON_CUT:True,
                            MB_BUTTON_RESYNC:True,
                            MB_BUTTON_SPLIT:True,
                            MB_BUTTON_SPLICE_OUT:True,
                            MB_BUTTON_LIFT:True,
                            MB_BUTTON_RIPPLE_DELETE:True,
                            MB_BUTTON_RANGE_DELETE:True,
                            MB_BUTTON_OVERWRITE_RANGE:True,
                            MB_BUTTON_OVERWRITE_CLIP:True,
                            MB_BUTTON_INSERT:True,
                            MB_BUTTON_APPEND:True,
                            MB_BUTTON_TOOL_MIXER:True,
                            MB_BUTTON_TOOL_TITLER:True,
                            MB_BUTTON_TOOL_BATCH:True,
                            MB_BUTTON_TOOL_GMIC:True}

# Button anf button group names
NAMES = None # This has to be filled after initial import cascade.
GROUP_NAMES = None

# glassbuttons.GlassButtonsGroup objects used to show buttons.
# Updated after button prefs changed.
GLASS_BUTTON_GROUPS = {}


# editorwindow.EditorWindow object.
# This needs to be set here because gui.py module ref is not available at init time
w = None

m_pixbufs = None

MIDDLE_ROW_HEIGHT = 30 # height of middle row gets set here

BUTTON_HEIGHT = 28 # middle edit buttons row
BUTTON_WIDTH = 48 # middle edit buttons row

NORMAL_WIDTH = 1420


def _init_names():
    global NAMES, GROUP_NAMES 

    if NAMES != None:
        return
    
    NAMES = {   MB_BUTTON_ZOOM_IN:_("Zoom In"),
                MB_BUTTON_ZOOM_OUT:_("Zoom Out"),
                MB_BUTTON_ZOOM_FIT:_("Zoom Length"),
                MB_BUTTON_UNDO:_("Undo"),
                MB_BUTTON_REDO:_("Redo"),
                MB_BUTTON_RENDERED_TRANSITION:_("Add Rendered Transition/Fade"),
                MB_BUTTON_CUT:_("Cut Active Tracks"),
                MB_BUTTON_RESYNC:_("Resync Selected"),
                MB_BUTTON_SPLIT:_("Split Audio"),
                MB_BUTTON_SPLICE_OUT:_("Splice Out"),
                MB_BUTTON_LIFT: _("Lift"),
                MB_BUTTON_RIPPLE_DELETE:_("Ripple Delete"),
                MB_BUTTON_RANGE_DELETE:_("Range Delete"),
                MB_BUTTON_OVERWRITE_RANGE:_("Overwrite Range"),
                MB_BUTTON_OVERWRITE_CLIP:_("Overwrite Clip"),
                MB_BUTTON_INSERT:_("Insert Clip"),
                MB_BUTTON_APPEND:_("Append Clip"),
                MB_BUTTON_TOOL_MIXER:_("Audio Mixer"),
                MB_BUTTON_TOOL_TITLER:_("Titler"),
                MB_BUTTON_TOOL_BATCH:_("Batch Render Queue"),
                MB_BUTTON_TOOL_GMIC:_("G'Mic Effects") }

    GROUP_NAMES = { BUTTON_GROUP_TOOLS:_("Tools Group"),
                    BUTTON_GROUP_UNDO:_("Undo Group"),
                    BUTTON_GROUP_ZOOM:_("Zoom Group"),
                    BUTTON_GROUP_EDIT:_("Edit Group"),
                    BUTTON_GROUP_SYNC_SPLIT:_("Sync Split Group"),
                    BUTTON_GROUP_DELETE:_("Delete Group"),
                    BUTTON_GROUP_MONITOR_ADD:_("Monitor Add Group") }
    """
    tooltips = [_("Undo - Ctrl + Z"), _("Redo - Ctrl + Y")]
    tooltips = [_("Audio Mixer"), _("Titler"), _("G'Mic Effects"), _("Batch Render Queue")]

    tooltips = [_("Zoom In - Mouse Middle Scroll"), _("Zoom Out - Mouse Middle Scroll"), _("Zoom Length - Mouse Middle Click")]

    tooltips = [_("Resync Selected"), _("Split Audio")]

    tooltips = [_("Add Rendered Transition - 2 clips selected\nAdd Rendered Fade - 1 clip selected"), _("Cut Active Tracks - X\nCut All Tracks - Shift + X")]

    tooltips = [_("Overwrite Range"), _("Overwrite Clip - T"), _("Insert Clip - Y"), _("Append Clip - U")]
    tooltips = [_("Splice Out - Delete"), _("Lift - Control + Delete"), _("Ripple Delete"), _("Range Delete")]
    """

def _show_buttons_TC_LEFT_layout(widget):
    global w
    w = gui.editor_window
    if w == None:
        return
    if widget.get_active() == False:
        return

    _clear_container(w.edit_buttons_row)
    _create_buttons(w)
    fill_with_TC_LEFT_pattern(w.edit_buttons_row, w)
    w.window.show_all()

    editorpersistance.prefs.midbar_layout = appconsts.MIDBAR_TC_LEFT
    editorpersistance.save()
    
def _show_buttons_TC_MIDDLE_layout(widget):
    global w
    w = gui.editor_window
    if w == None:
        return
    if widget.get_active() == False:
        return

    _clear_container(w.edit_buttons_row)
    _create_buttons(w)
    fill_with_TC_MIDDLE_pattern(w.edit_buttons_row, w)
    w.window.show_all()

    editorpersistance.prefs.midbar_layout = appconsts.MIDBAR_TC_CENTER
    editorpersistance.save()

def _show_buttons_COMPONENTS_CENTERED_layout(widget):
    global w
    w = gui.editor_window
    if w == None:
        return
    if widget.get_active() == False:
        return

    _clear_container(w.edit_buttons_row)
    _create_buttons(w)
    fill_with_COMPONENTS_CENTERED_pattern(w.edit_buttons_row, w)
    w.window.show_all()

    editorpersistance.prefs.midbar_layout = appconsts.MIDBAR_COMPONENTS_CENTERED
    editorpersistance.save()

def create_edit_buttons_row_buttons(editor_window, modes_pixbufs):
    global m_pixbufs
    m_pixbufs = modes_pixbufs
    _create_buttons(editor_window)

def _create_buttons(editor_window):

    _init_names()

    # Aug-2019 - SvdB - BB
    prefs = editorpersistance.prefs
    size_adj = 1
    if prefs.double_track_hights:
       size_adj = 2

    editor_window.big_TC = Gtk.Stack()
    tc_disp = guicomponents.BigTCDisplay()
    tc_entry = guicomponents.BigTCEntry()
    tc_disp.widget.show()
    tc_entry.widget.show()
    editor_window.big_TC.add_named(tc_disp.widget, "BigTCDisplay")
    editor_window.big_TC.add_named(tc_entry.widget, "BigTCEntry")
    editor_window.big_TC.set_visible_child_name("BigTCDisplay")
    gui.big_tc = editor_window.big_TC 

    surface = guiutils.get_cairo_image("workflow")
    editor_window.worflow_launch = guicomponents.PressLaunch(workflow.workflow_menu_launched, surface, w=22*size_adj, h=22*size_adj)

    editor_window.tool_selector = guicomponents.ToolSelector(editor_window.mode_selector_pressed, m_pixbufs, 40*size_adj, 22*size_adj)

    if editorpersistance.prefs.buttons_style == 2: # NO_DECORATIONS
        no_decorations = True
    else:
        no_decorations = False

    # Zoom group buttons
    editor_window.zoom_buttons = glassbuttons.GlassButtonsGroup(38*size_adj, 23*size_adj, 2*size_adj, 8*size_adj, 5*size_adj)
    tooltips = []
    _add_active_button(editor_window.zoom_buttons, MB_BUTTON_ZOOM_IN, tooltips, updater.zoom_in)
    _add_active_button(editor_window.zoom_buttons, MB_BUTTON_ZOOM_OUT, tooltips, updater.zoom_out)
    _add_active_button(editor_window.zoom_buttons, MB_BUTTON_ZOOM_FIT, tooltips, updater.zoom_project_length)
    if editor_window.zoom_buttons.num_buttons() > 0:
        tooltip_runner = glassbuttons.TooltipRunner(editor_window.zoom_buttons, tooltips)
    editor_window.zoom_buttons.no_decorations = no_decorations
    
    # Edit group
    editor_window.edit_buttons = glassbuttons.GlassButtonsGroup(32*size_adj, 23*size_adj, 2*size_adj, 5*size_adj, 5*size_adj)
    tooltips = []
    _add_active_button(editor_window.edit_buttons, MB_BUTTON_RENDERED_TRANSITION, tooltips, tlineaction.add_transition_pressed)
    _add_active_button(editor_window.edit_buttons, MB_BUTTON_CUT, tooltips, tlineaction.cut_pressed)
    if editor_window.edit_buttons.num_buttons() > 0:
        tooltip_runner = glassbuttons.TooltipRunner(editor_window.edit_buttons, tooltips)
    editor_window.edit_buttons.no_decorations = no_decorations

    # Delete group
    editor_window.edit_buttons_3 = glassbuttons.GlassButtonsGroup(46*size_adj, 23*size_adj, 2*size_adj, 3*size_adj, 5*size_adj)
    tooltips = []
    _add_active_button(editor_window.edit_buttons_3, MB_BUTTON_SPLICE_OUT, tooltips, tlineaction.splice_out_button_pressed)
    _add_active_button(editor_window.edit_buttons_3, MB_BUTTON_LIFT, tooltips, tlineaction.lift_button_pressed)
    _add_active_button(editor_window.edit_buttons_3, MB_BUTTON_RIPPLE_DELETE, tooltips, tlineaction.ripple_delete_button_pressed)
    _add_active_button(editor_window.edit_buttons_3, MB_BUTTON_RANGE_DELETE, tooltips, tlineaction.delete_range_button_pressed)
    if editor_window.edit_buttons_3.num_buttons() > 0:
        tooltip_runner = glassbuttons.TooltipRunner(editor_window.edit_buttons_3, tooltips)
    editor_window.edit_buttons_3.no_decorations = no_decorations

    # Sync Split Group
    editor_window.edit_buttons_2 = glassbuttons.GlassButtonsGroup(44*size_adj, 23*size_adj, 2*size_adj, 3*size_adj, 5*size_adj)
    tooltips = []
    _add_active_button(editor_window.edit_buttons_2, MB_BUTTON_RESYNC, tooltips, tlineaction.resync_button_pressed)
    _add_active_button(editor_window.edit_buttons_2, MB_BUTTON_SPLIT, tooltips, tlineaction.split_audio_button_pressed)
    if editor_window.edit_buttons_2.num_buttons() > 0:
        tooltip_runner = glassbuttons.TooltipRunner(editor_window.edit_buttons_2, tooltips)
    editor_window.edit_buttons_2.no_decorations = no_decorations
    
    # Monitor add group   
    editor_window.monitor_insert_buttons = glassbuttons.GlassButtonsGroup(44*size_adj, 23*size_adj, 2*size_adj, 3*size_adj, 5*size_adj)
    tooltips = []
    _add_active_button(editor_window.monitor_insert_buttons, MB_BUTTON_OVERWRITE_RANGE, tooltips, tlineaction.range_overwrite_pressed)
    _add_active_button(editor_window.monitor_insert_buttons, MB_BUTTON_OVERWRITE_CLIP, tooltips, tlineaction.three_point_overwrite_pressed)
    _add_active_button(editor_window.monitor_insert_buttons, MB_BUTTON_INSERT, tooltips, tlineaction.insert_button_pressed)
    _add_active_button(editor_window.monitor_insert_buttons, MB_BUTTON_APPEND, tooltips, tlineaction.append_button_pressed)
    if editor_window.monitor_insert_buttons.num_buttons() > 0:
        tooltip_runner = glassbuttons.TooltipRunner(editor_window.monitor_insert_buttons, tooltips)
    editor_window.monitor_insert_buttons.no_decorations = no_decorations
    
    # Undo group
    editor_window.undo_redo = glassbuttons.GlassButtonsGroup(28*size_adj, 23*size_adj, 2*size_adj, 2*size_adj, 7*size_adj)
    tooltips = []
    _add_active_button(editor_window.undo_redo, MB_BUTTON_UNDO, tooltips, undo.do_undo_and_repaint)
    _add_active_button(editor_window.undo_redo, MB_BUTTON_REDO, tooltips, undo.do_redo_and_repaint)
    if editor_window.undo_redo.num_buttons() > 0:
        tooltip_runner = glassbuttons.TooltipRunner(editor_window.undo_redo, tooltips)
    editor_window.undo_redo.no_decorations = no_decorations

    # Tool button group
    editor_window.tools_buttons = glassbuttons.GlassButtonsGroup(30*size_adj, 23*size_adj, 2*size_adj, 14*size_adj, 7*size_adj)
    tooltips = []
    _add_active_button(editor_window.tools_buttons, MB_BUTTON_TOOL_TITLER, tooltips, titler.show_titler)
    _add_active_button(editor_window.tools_buttons, MB_BUTTON_TOOL_MIXER, tooltips, audiomonitoring.show_audio_monitor)
    _add_active_button(editor_window.tools_buttons, MB_BUTTON_TOOL_BATCH, tooltips, lambda :batchrendering.launch_batch_rendering())
    _add_active_button(editor_window.tools_buttons, MB_BUTTON_TOOL_GMIC, tooltips, gmic.launch_gmic)
    if editor_window.tools_buttons.num_buttons() > 0:
        tooltip_runner = glassbuttons.TooltipRunner(editor_window.tools_buttons, tooltips)
    editor_window.tools_buttons.no_decorations = True
    
    """ this needs some other thing since index is not necesserily 0 for mixer button
    if editorstate.audio_monitoring_available == False:
        editor_window.tools_buttons.sensitive[0] = False
        editor_window.tools_buttons.widget.set_tooltip_text(_("Audio Mixer(not available)\nTitler"))
    """

def _add_active_button(group, button, tooltips, callback):
    active_states = DEFAULT_ACTIVE_STATES
    if active_states[button] == False:
        return
    
    group.add_button(guiutils.get_cairo_image(ICONS[button]), callback)
    tooltips.append(NAMES[button])
    
def fill_with_TC_LEFT_pattern(buttons_row, window):
    buttons_row.set_homogeneous(False)
    global w
    w = window

    buttons_row.pack_start(w.worflow_launch.widget, False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(7, MIDDLE_ROW_HEIGHT), False, True, 0) 
    buttons_row.pack_start(w.big_TC, False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(7, MIDDLE_ROW_HEIGHT), False, True, 0) #### NOTE!!!!!! THIS DETERMINES THE HEIGHT OF MIDDLE ROW
    buttons_row.pack_start(w.tool_selector.widget, False, True, 0)

    if editorstate.SCREEN_WIDTH > NORMAL_WIDTH:
        buttons_row.pack_start(guiutils.get_pad_label(24, 10), False, True, 0)
        buttons_row.pack_start(_get_tools_buttons(), False, True, 0)
        buttons_row.pack_start(guiutils.get_pad_label(170, 10), False, True, 0)
    else:
        buttons_row.pack_start(guiutils.get_pad_label(30, 10), False, True, 0)
    
    
    buttons_row.pack_start(_get_undo_buttons_panel(), False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(30, 10), False, True, 0)
        
    buttons_row.pack_start(_get_zoom_buttons_panel(),False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(30, 10), False, True, 0)
    
    buttons_row.pack_start(_get_edit_buttons_panel(),False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(30, 10), False, True, 0)
    
    buttons_row.pack_start(_get_edit_buttons_2_panel(),False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(20, 10), False, True, 0)
    
    buttons_row.pack_start(_get_edit_buttons_3_panel(),False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(30, 10), False, True, 0)
    
    buttons_row.pack_start(_get_monitor_insert_buttons(), False, True, 0)
    buttons_row.pack_start(Gtk.Label(), True, True, 0)
    
def fill_with_TC_MIDDLE_pattern(buttons_row, window):
    buttons_row.set_homogeneous(True)
    global w
    w = window
    left_panel = Gtk.HBox(False, 0)    
    left_panel.pack_start(_get_undo_buttons_panel(), False, True, 0)
    left_panel.pack_start(guiutils.get_pad_label(10, MIDDLE_ROW_HEIGHT), False, True, 0) #### NOTE!!!!!! THIS DETERMINES THE HEIGHT OF MIDDLE ROW
    left_panel.pack_start(_get_zoom_buttons_panel(), False, True, 0)
    if editorstate.SCREEN_WIDTH > NORMAL_WIDTH:
        left_panel.pack_start(guiutils.get_pad_label(10, 10), False, True, 0)
        left_panel.pack_start(_get_tools_buttons(), False, True, 0)
        left_panel.pack_start(guiutils.get_pad_label(50, 10), False, True, 10) # to left and right panel same size for centering
    else:
        left_panel.pack_start(guiutils.get_pad_label(60, 10), False, True, 10) # to left and right panel same size for centering
    left_panel.pack_start(Gtk.Label(), True, True, 0)

    middle_panel = Gtk.HBox(False, 0)
    middle_panel.pack_start(w.worflow_launch.widget, False, True, 0)
    middle_panel.pack_start(guiutils.get_pad_label(7, MIDDLE_ROW_HEIGHT), False, True, 0) 
    middle_panel.pack_start(w.big_TC, False, True, 0)
    middle_panel.pack_start(guiutils.get_pad_label(10, 10), False, True, 0)
    middle_panel.pack_start(w.tool_selector.widget, False, True, 0)
    
    right_panel = Gtk.HBox(False, 0) 
    right_panel.pack_start(Gtk.Label(), True, True, 0)
    right_panel.pack_start(_get_edit_buttons_panel(), False, True, 0)
    right_panel.pack_start(guiutils.get_pad_label(10, 10), False, True, 0)
    right_panel.pack_start(_get_edit_buttons_3_panel(),False, True, 0)
    right_panel.pack_start(guiutils.get_pad_label(10, 10), False, True, 0)
    right_panel.pack_start(_get_edit_buttons_2_panel(),False, True, 0)
    right_panel.pack_start(guiutils.get_pad_label(10, 10), False, True, 0)
    right_panel.pack_start(_get_monitor_insert_buttons(), False, True, 0)

    buttons_row.pack_start(left_panel, True, True, 0)
    buttons_row.pack_start(middle_panel, False, False, 0)
    buttons_row.pack_start(right_panel, True, True, 0)

def fill_with_COMPONENTS_CENTERED_pattern(buttons_row, window):
    buttons_row.set_homogeneous(False)
    global w
    w = window
    buttons_row.pack_start(Gtk.Label(), True, True, 0)
    buttons_row.pack_start(w.worflow_launch.widget, False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(7, MIDDLE_ROW_HEIGHT), False, True, 0) 
    buttons_row.pack_start(w.big_TC, False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(7, MIDDLE_ROW_HEIGHT), False, True, 0) #### NOTE!!!!!! THIS DETERMINES THE HEIGHT OF MIDDLE ROW
    buttons_row.pack_start(w.tool_selector.widget, False, True, 0)
    if editorstate.SCREEN_WIDTH > NORMAL_WIDTH:
        buttons_row.pack_start(guiutils.get_pad_label(10, 10), False, True, 0)
        buttons_row.pack_start(_get_tools_buttons(), False, True, 0)
        #buttons_row.pack_start(guiutils.get_pad_label(120, 10), False, True, 0)
        buttons_row.pack_start(guiutils.get_pad_label(20, 10), False, True, 0)
    else:
        buttons_row.pack_start(guiutils.get_pad_label(20, 10), False, True, 0)
        
    buttons_row.pack_start(_get_undo_buttons_panel(), False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(20, 10), False, True, 0)
        
    buttons_row.pack_start(_get_zoom_buttons_panel(),False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(20, 10), False, True, 0)
    
    buttons_row.pack_start(_get_edit_buttons_panel(),False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(20, 10), False, True, 0)
    
    buttons_row.pack_start(_get_edit_buttons_2_panel(),False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(20, 10), False, True, 0)
    
    buttons_row.pack_start(_get_edit_buttons_3_panel(),False, True, 0)
    buttons_row.pack_start(guiutils.get_pad_label(20, 10), False, True, 0)
    
    buttons_row.pack_start(_get_monitor_insert_buttons(), False, True, 0)
    buttons_row.pack_start(Gtk.Label(), True, True, 0)
    
def _get_zoom_buttons_panel():    
    return w.zoom_buttons.widget

def _get_undo_buttons_panel():
    return w.undo_redo.widget

def _get_edit_buttons_panel():
    return w.edit_buttons.widget

def _get_edit_buttons_2_panel():
    return w.edit_buttons_2.widget

def _get_edit_buttons_3_panel():
    return w.edit_buttons_3.widget
    
def _get_monitor_insert_buttons():
    return w.monitor_insert_buttons.widget

def _get_tools_buttons():
    return w.tools_buttons.widget

def _b(button, icon, remove_relief=False):
    button.set_image(icon)
    button.set_property("can-focus",  False)
    if remove_relief:
        button.set_relief(Gtk.ReliefStyle.NONE)

def _clear_container(cont):
    children = cont.get_children()
    for child in children:
        cont.remove(child)


# ----------------------------------------------------------------------- buttons prefs GUI
def show_button_preferences_dialog():


    dialog = Gtk.Dialog(_("Set Active Middlebar Buttons"), None,
                    Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    (_("Cancel"), Gtk.ResponseType.REJECT,
                    _("OK"), Gtk.ResponseType.ACCEPT))

    prefs_panel = _get_prefs_panel()
    
    dialog.connect('response', _buttons_preferences_dialog_callback, DEFAULT_ACTIVE_STATES)
    dialog.vbox.pack_start(prefs_panel, True, True, 0)
    dialogutils.set_outer_margins(dialog.vbox)
    dialogutils.default_behaviour(dialog)
    dialog.set_transient_for(gui.editor_window.window)
    dialog.show_all()


def _buttons_preferences_dialog_callback(dialog, response_id, orig_prefs):
    if response_id == Gtk.ResponseType.ACCEPT:
        editorpersistance.update_prefs_from_widgets(all_widgets)
        editorpersistance.save()
        dialog.destroy()
    else:
        # orig_prefs
        dialog.destroy()

def _get_prefs_panel():
    column_1 = Gtk.VBox()
    
    buttons = [MB_BUTTON_ZOOM_IN, MB_BUTTON_ZOOM_OUT, MB_BUTTON_ZOOM_FIT]
    group_panel = ButtonGroupPanel(GROUP_NAMES[BUTTON_GROUP_ZOOM], buttons, DEFAULT_ACTIVE_STATES)
    column_1.pack_start(group_panel.widget, False, False, 0)

    buttons = [MB_BUTTON_UNDO, MB_BUTTON_REDO]
    group_panel = ButtonGroupPanel(GROUP_NAMES[BUTTON_GROUP_UNDO], buttons, DEFAULT_ACTIVE_STATES)
    column_1.pack_start(group_panel.widget, False, False, 0)

    buttons = [MB_BUTTON_RENDERED_TRANSITION, MB_BUTTON_CUT]
    group_panel = ButtonGroupPanel(GROUP_NAMES[BUTTON_GROUP_EDIT], buttons, DEFAULT_ACTIVE_STATES)
    column_1.pack_start(group_panel.widget, False, False, 0)

    buttons = [MB_BUTTON_RESYNC, MB_BUTTON_SPLIT]
    group_panel = ButtonGroupPanel(GROUP_NAMES[BUTTON_GROUP_SYNC_SPLIT], buttons, DEFAULT_ACTIVE_STATES)
    column_1.pack_start(group_panel.widget, False, False, 0)

    buttons = [MB_BUTTON_RESYNC, MB_BUTTON_SPLIT]
    group_panel = ButtonGroupPanel(GROUP_NAMES[BUTTON_GROUP_SYNC_SPLIT], buttons, DEFAULT_ACTIVE_STATES)
    column_1.pack_start(group_panel.widget, False, False, 0)


    column_2 = Gtk.VBox()
    
    buttons = [MB_BUTTON_SPLICE_OUT, MB_BUTTON_LIFT, MB_BUTTON_RIPPLE_DELETE, MB_BUTTON_RANGE_DELETE]
    group_panel = ButtonGroupPanel(GROUP_NAMES[BUTTON_GROUP_DELETE], buttons, DEFAULT_ACTIVE_STATES)
    column_2.pack_start(group_panel.widget, False, False, 0)

    buttons = [MB_BUTTON_OVERWRITE_RANGE, MB_BUTTON_OVERWRITE_CLIP, MB_BUTTON_INSERT, MB_BUTTON_APPEND]
    group_panel = ButtonGroupPanel(GROUP_NAMES[BUTTON_GROUP_MONITOR_ADD], buttons, DEFAULT_ACTIVE_STATES)
    column_2.pack_start(group_panel.widget, False, False, 0) 

    buttons = [MB_BUTTON_TOOL_MIXER, MB_BUTTON_TOOL_TITLER, MB_BUTTON_TOOL_BATCH, MB_BUTTON_TOOL_GMIC]
    group_panel = ButtonGroupPanel(GROUP_NAMES[BUTTON_GROUP_TOOLS], buttons, DEFAULT_ACTIVE_STATES)
    column_2.pack_start(group_panel.widget, False, False, 0) 
    
    pane = Gtk.HBox()
    pane.pack_start(column_1, False, False, 0)
    pane.pack_start(guiutils.pad_label(24,12), False, False, 0)
    pane.pack_start(column_2, False, False, 0)
    
    return dialogutils.get_alignment2(pane)


class ButtonGroupPanel:
    def __init__(self, button_group_name, buttons, active_states):
        vbox = Gtk.VBox(True, 0)
        
        for button in buttons:
            row = ButtonPrefRow(button, active_states)
            vbox.pack_start(row, False, False, 0)

        self.widget = guiutils.get_named_frame(button_group_name, vbox)


class ButtonPrefRow(Gtk.HBox):
    def __init__(self, button, active_states):
        GObject.GObject.__init__(self)

        self.button = button
        self.active_states = active_states
    
        name = NAMES[button]
        label = Gtk.Label(name)
        label_box = guiutils.get_left_justified_box([label])
        icon = guiutils.get_image(ICONS[button])
        icon_box = guiutils.get_left_justified_box([icon])
        active = active_states[button]
        active_check = Gtk.CheckButton()
        active_check.set_active(active)
        
        label_box.set_size_request(260, 24)
        icon_box.set_size_request(96, 24)
        active_check.set_size_request(24, 24)

        self.pack_start(icon_box, False, False, 0)
        self.pack_start(label_box, False, False, 0)
        self.pack_start(active_check, False, False, 0)

