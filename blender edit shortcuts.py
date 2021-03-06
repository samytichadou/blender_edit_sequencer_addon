import bpy
import os

def kmi_props_setattr(kmi_props, attr, value):
    try:
        setattr(kmi_props, attr, value)
    except AttributeError:
        print("Warning: property '%s' not found in keymap item '%s'" %
              (attr, kmi_props.__class__.__name__))
    except Exception as e:
        print("Warning: %r" % e)

wm = bpy.context.window_manager
kc = wm.keyconfigs.new(os.path.splitext(os.path.basename(__file__))[0])

# Map SequencerCommon
km = kc.keymaps.new('SequencerCommon', space_type='SEQUENCE_EDITOR', region_type='WINDOW', modal=False)

kmi = km.keymap_items.new('sequencer.properties', 'N', 'PRESS')
kmi = km.keymap_items.new('wm.context_toggle', 'O', 'PRESS', shift=True)
kmi_props_setattr(kmi.properties, 'data_path', 'scene.sequence_editor.show_overlay')
kmi.active = False
kmi = km.keymap_items.new('sequencer.view_toggle', 'TAB', 'PRESS', ctrl=True)

# Map Sequencer
km = kc.keymaps.new('Sequencer', space_type='SEQUENCE_EDITOR', region_type='WINDOW', modal=False)

kmi = km.keymap_items.new('sequencer.select_all', 'A', 'PRESS')
kmi_props_setattr(kmi.properties, 'action', 'TOGGLE')
kmi = km.keymap_items.new('sequencer.select_all', 'I', 'PRESS', ctrl=True)
kmi_props_setattr(kmi.properties, 'action', 'INVERT')
kmi.active = False
kmi = km.keymap_items.new('sequencer.cut', 'K', 'PRESS')
kmi_props_setattr(kmi.properties, 'type', 'SOFT')
kmi = km.keymap_items.new('sequencer.cut', 'K', 'PRESS', shift=True)
kmi_props_setattr(kmi.properties, 'type', 'HARD')
kmi = km.keymap_items.new('sequencer.mute', 'H', 'PRESS')
kmi_props_setattr(kmi.properties, 'unselected', False)
kmi = km.keymap_items.new('sequencer.mute', 'H', 'PRESS', shift=True)
kmi_props_setattr(kmi.properties, 'unselected', True)
kmi = km.keymap_items.new('sequencer.unmute', 'H', 'PRESS', alt=True)
kmi_props_setattr(kmi.properties, 'unselected', False)
kmi = km.keymap_items.new('sequencer.unmute', 'H', 'PRESS', shift=True, alt=True)
kmi_props_setattr(kmi.properties, 'unselected', True)
kmi = km.keymap_items.new('sequencer.lock', 'L', 'PRESS', shift=True)
kmi = km.keymap_items.new('sequencer.unlock', 'L', 'PRESS', shift=True, alt=True)
kmi = km.keymap_items.new('sequencer.reassign_inputs', 'R', 'PRESS')
kmi = km.keymap_items.new('sequencer.reload', 'R', 'PRESS', alt=True)
kmi = km.keymap_items.new('sequencer.reload', 'R', 'PRESS', shift=True, alt=True)
kmi_props_setattr(kmi.properties, 'adjust_length', True)
kmi = km.keymap_items.new('sequencer.offset_clear', 'O', 'PRESS', alt=True)
kmi = km.keymap_items.new('sequencer.duplicate_move', 'D', 'PRESS', shift=True)
kmi = km.keymap_items.new('sequencer.delete', 'X', 'PRESS')
kmi = km.keymap_items.new('sequencer.delete', 'DEL', 'PRESS')
kmi = km.keymap_items.new('sequencer.copy', 'C', 'PRESS', ctrl=True)
kmi = km.keymap_items.new('sequencer.paste', 'V', 'PRESS', ctrl=True)
kmi = km.keymap_items.new('sequencer.images_separate', 'Y', 'PRESS')
kmi = km.keymap_items.new('sequencer.meta_toggle', 'TAB', 'PRESS')
kmi = km.keymap_items.new('sequencer.meta_make', 'G', 'PRESS', ctrl=True)
kmi = km.keymap_items.new('sequencer.meta_separate', 'G', 'PRESS', alt=True)
kmi = km.keymap_items.new('sequencer.view_all', 'HOME', 'PRESS')
kmi = km.keymap_items.new('sequencer.view_all', 'NDOF_BUTTON_FIT', 'PRESS')
kmi = km.keymap_items.new('sequencer.view_selected', 'NUMPAD_PERIOD', 'PRESS')
kmi = km.keymap_items.new('sequencer.view_frame', 'NUMPAD_0', 'PRESS')
kmi = km.keymap_items.new('sequencer.strip_jump', 'PAGE_UP', 'PRESS')
kmi_props_setattr(kmi.properties, 'next', True)
kmi_props_setattr(kmi.properties, 'center', False)
kmi = km.keymap_items.new('sequencer.strip_jump', 'PAGE_DOWN', 'PRESS')
kmi_props_setattr(kmi.properties, 'next', False)
kmi_props_setattr(kmi.properties, 'center', False)
kmi = km.keymap_items.new('sequencer.strip_jump', 'PAGE_UP', 'PRESS', alt=True)
kmi_props_setattr(kmi.properties, 'next', True)
kmi_props_setattr(kmi.properties, 'center', True)
kmi = km.keymap_items.new('sequencer.strip_jump', 'PAGE_DOWN', 'PRESS', alt=True)
kmi_props_setattr(kmi.properties, 'next', False)
kmi_props_setattr(kmi.properties, 'center', True)
kmi = km.keymap_items.new('sequencer.swap', 'LEFT_ARROW', 'PRESS', alt=True)
kmi_props_setattr(kmi.properties, 'side', 'LEFT')
kmi = km.keymap_items.new('sequencer.swap', 'RIGHT_ARROW', 'PRESS', alt=True)
kmi_props_setattr(kmi.properties, 'side', 'RIGHT')
kmi = km.keymap_items.new('sequencer.gap_remove', 'BACK_SPACE', 'PRESS')
kmi_props_setattr(kmi.properties, 'all', False)
kmi = km.keymap_items.new('sequencer.gap_remove', 'BACK_SPACE', 'PRESS', shift=True)
kmi_props_setattr(kmi.properties, 'all', True)
kmi = km.keymap_items.new('sequencer.gap_insert', 'EQUAL', 'PRESS', shift=True)
kmi = km.keymap_items.new('sequencer.snap', 'S', 'PRESS', shift=True)
kmi = km.keymap_items.new('sequencer.swap_inputs', 'S', 'PRESS', alt=True)
kmi = km.keymap_items.new('sequencer.cut_multicam', 'ONE', 'PRESS')
kmi_props_setattr(kmi.properties, 'camera', 1)
kmi = km.keymap_items.new('sequencer.cut_multicam', 'TWO', 'PRESS')
kmi_props_setattr(kmi.properties, 'camera', 2)
kmi = km.keymap_items.new('sequencer.cut_multicam', 'THREE', 'PRESS')
kmi_props_setattr(kmi.properties, 'camera', 3)
kmi = km.keymap_items.new('sequencer.cut_multicam', 'FOUR', 'PRESS')
kmi_props_setattr(kmi.properties, 'camera', 4)
kmi = km.keymap_items.new('sequencer.cut_multicam', 'FIVE', 'PRESS')
kmi_props_setattr(kmi.properties, 'camera', 5)
kmi = km.keymap_items.new('sequencer.cut_multicam', 'SIX', 'PRESS')
kmi_props_setattr(kmi.properties, 'camera', 6)
kmi = km.keymap_items.new('sequencer.cut_multicam', 'SEVEN', 'PRESS')
kmi_props_setattr(kmi.properties, 'camera', 7)
kmi = km.keymap_items.new('sequencer.cut_multicam', 'EIGHT', 'PRESS')
kmi_props_setattr(kmi.properties, 'camera', 8)
kmi = km.keymap_items.new('sequencer.cut_multicam', 'NINE', 'PRESS')
kmi_props_setattr(kmi.properties, 'camera', 9)
kmi = km.keymap_items.new('sequencer.cut_multicam', 'ZERO', 'PRESS')
kmi_props_setattr(kmi.properties, 'camera', 10)
kmi = km.keymap_items.new('sequencer.select', 'SELECTMOUSE', 'PRESS')
kmi_props_setattr(kmi.properties, 'extend', False)
kmi_props_setattr(kmi.properties, 'linked_handle', False)
kmi_props_setattr(kmi.properties, 'left_right', 'NONE')
kmi_props_setattr(kmi.properties, 'linked_time', False)
kmi = km.keymap_items.new('sequencer.select', 'SELECTMOUSE', 'PRESS', shift=True)
kmi_props_setattr(kmi.properties, 'extend', True)
kmi_props_setattr(kmi.properties, 'linked_handle', False)
kmi_props_setattr(kmi.properties, 'left_right', 'NONE')
kmi_props_setattr(kmi.properties, 'linked_time', False)
kmi = km.keymap_items.new('sequencer.select', 'SELECTMOUSE', 'PRESS', alt=True)
kmi_props_setattr(kmi.properties, 'extend', False)
kmi_props_setattr(kmi.properties, 'linked_handle', True)
kmi_props_setattr(kmi.properties, 'left_right', 'NONE')
kmi_props_setattr(kmi.properties, 'linked_time', False)
kmi = km.keymap_items.new('sequencer.select', 'SELECTMOUSE', 'PRESS', shift=True, alt=True)
kmi_props_setattr(kmi.properties, 'extend', True)
kmi_props_setattr(kmi.properties, 'linked_handle', True)
kmi_props_setattr(kmi.properties, 'left_right', 'NONE')
kmi_props_setattr(kmi.properties, 'linked_time', False)
kmi = km.keymap_items.new('sequencer.select', 'SELECTMOUSE', 'PRESS', ctrl=True)
kmi_props_setattr(kmi.properties, 'extend', False)
kmi_props_setattr(kmi.properties, 'linked_handle', False)
kmi_props_setattr(kmi.properties, 'left_right', 'MOUSE')
kmi_props_setattr(kmi.properties, 'linked_time', True)
kmi = km.keymap_items.new('sequencer.select', 'SELECTMOUSE', 'PRESS', shift=True, ctrl=True)
kmi_props_setattr(kmi.properties, 'extend', True)
kmi_props_setattr(kmi.properties, 'linked_handle', False)
kmi_props_setattr(kmi.properties, 'left_right', 'NONE')
kmi_props_setattr(kmi.properties, 'linked_time', True)
kmi = km.keymap_items.new('sequencer.select_more', 'NUMPAD_PLUS', 'PRESS', ctrl=True)
kmi = km.keymap_items.new('sequencer.select_less', 'NUMPAD_MINUS', 'PRESS', ctrl=True)
kmi = km.keymap_items.new('sequencer.select_linked_pick', 'L', 'PRESS')
kmi_props_setattr(kmi.properties, 'extend', False)
kmi = km.keymap_items.new('sequencer.select_linked_pick', 'L', 'PRESS', shift=True)
kmi_props_setattr(kmi.properties, 'extend', True)
kmi = km.keymap_items.new('sequencer.select_linked', 'L', 'PRESS', ctrl=True)
kmi = km.keymap_items.new('sequencer.select_border', 'B', 'PRESS')
kmi = km.keymap_items.new('sequencer.select_grouped', 'G', 'PRESS', shift=True)
kmi = km.keymap_items.new('wm.call_menu', 'A', 'PRESS', shift=True)
kmi_props_setattr(kmi.properties, 'name', 'SEQUENCER_MT_add')
kmi = km.keymap_items.new('wm.call_menu', 'C', 'PRESS')
kmi_props_setattr(kmi.properties, 'name', 'SEQUENCER_MT_change')
kmi = km.keymap_items.new('sequencer.slip', 'S', 'PRESS')
kmi = km.keymap_items.new('transform.seq_slide', 'G', 'PRESS')
kmi = km.keymap_items.new('transform.seq_slide', 'EVT_TWEAK_S', 'ANY')
kmi = km.keymap_items.new('transform.transform', 'E', 'PRESS')
kmi_props_setattr(kmi.properties, 'mode', 'TIME_EXTEND')
kmi = km.keymap_items.new('marker.add', 'M', 'PRESS')
kmi = km.keymap_items.new('marker.rename', 'M', 'PRESS', ctrl=True)
kmi = km.keymap_items.new('bledit.set_in', 'I', 'PRESS')
kmi = km.keymap_items.new('bledit.set_out', 'O', 'PRESS')
kmi = km.keymap_items.new('bledit.clear_in', 'I', 'PRESS', ctrl=True)
kmi = km.keymap_items.new('bledit.clear_out', 'O', 'PRESS', ctrl=True)
kmi = km.keymap_items.new('bledit.goto_in', 'I', 'PRESS', shift=True)
kmi = km.keymap_items.new('bledit.goto_out', 'O', 'PRESS', shift=True)
kmi = km.keymap_items.new('bledit.overwrite_on_timeline', 'PERIOD', 'PRESS')
kmi = km.keymap_items.new('bledit.splice_on_timeline', 'COMMA', 'PRESS')
kmi = km.keymap_items.new('bledit.next_video_channel', 'NUMPAD_PLUS', 'PRESS', shift=True)
kmi = km.keymap_items.new('bledit.previous_video_channel', 'NUMPAD_MINUS', 'PRESS', shift=True)
kmi = km.keymap_items.new('bledit.next_audio_channel', 'NUMPAD_PLUS', 'PRESS', ctrl=True)
kmi = km.keymap_items.new('bledit.previous_audio_channel', 'NUMPAD_MINUS', 'PRESS', ctrl=True)

