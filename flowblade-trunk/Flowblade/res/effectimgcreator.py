
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
    along with Flowblade Movie Editor. If not, see <http://www.gnu.org/licenses/>.
"""

import editorstate
import mltfilters
import mlt

OUT_FOLDER = "/home/janne/codes/docs/Flowblade/art/effimgs/"

SOURCE_IMGS = ["/home/janne/codes/docs/Flowblade/art/eff_img_source1.png"]


def write_out_eff_imgs():
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

def write_image(profile, source_path, filter_info):

    # Create consumer
    print "writing " + filter_info.name + "..."
    out_img_path = OUT_FOLDER + filter_info.name + ".png"
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

