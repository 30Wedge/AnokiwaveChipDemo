#-------------------------------------------------------------------------------
# Name:        hello.py
# Purpose:
#
# Author:      Grayson Colwell
#
# Created:     05/02/2018
# Copyright:   (c) Grayson Colwell 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------



from __future__ import print_function

SHOW = True # Show test in GUI-based test launcher

import tempfile, atexit, shutil
import numpy as np

from guidata.dataset.datatypes import (DataSet, BeginTabGroup, EndTabGroup,
                                       BeginGroup, EndGroup, ObjectItem)
from guidata.dataset.dataitems import (FloatItem, IntItem, BoolItem, ChoiceItem,
                             MultipleChoiceItem, ImageChoiceItem, FilesOpenItem,
                             StringItem, TextItem, ColorItem, FileSaveItem,
                             FileOpenItem, DirectoryItem, FloatArrayItem)

from guidata.dataset.qtwidgets import DataSetEditLayout, DataSetShowLayout
from guidata.dataset.qtitemwidgets import DataSetWidget


# Creating temporary files and registering cleanup functions
TEMPDIR = tempfile.mkdtemp(prefix="test_")
atexit.register(shutil.rmtree, TEMPDIR)
FILE_ETA = tempfile.NamedTemporaryFile(suffix=".eta", dir=TEMPDIR)
atexit.register(FILE_ETA.close)
FILE_CSV = tempfile.NamedTemporaryFile(suffix=".csv", dir=TEMPDIR)
atexit.register(FILE_CSV.close)

class SubDataSet(DataSet):
    dir = DirectoryItem("Directory", TEMPDIR)
    fname = FileOpenItem("Single file (open)", ("csv", "eta"), FILE_CSV.name)
    fnames = FilesOpenItem("Multiple files", "csv", FILE_CSV.name)
    fname_s = FileSaveItem("Single file (save)", "eta", FILE_ETA.name)

class SubDataSetWidget(DataSetWidget):
    klass = SubDataSet

class SubDataSetItem(ObjectItem):
    klass = SubDataSet

DataSetEditLayout.register(SubDataSetItem, SubDataSetWidget)
DataSetShowLayout.register(SubDataSetItem, SubDataSetWidget)


class TestParameters(DataSet):
    """
    Anokiwave GUI Test
    This is not a drill,

    North Korea has launched nuclear missiles
    Find shelter
    """
    _bg = BeginGroup("Amplitude and Phase Modulation")
    NW_RA = IntItem("NW Receive & phase",
                             default=0.0, min=0, max=31, slider=False).set_pos(col=0)
    NW_PhaseR = IntItem("",default=0.0, min = 0, max =31, slider=False).set_pos(col=1)

    NE_RA = IntItem("NE Receive & phase",
                             default=0.0, min=0, max=31, slider=False).set_pos(col=2, )
    NE_PhaseR = IntItem("",default=0.0, min = 0, max =31, slider=False).set_pos(col=3)

    NW_TA = IntItem("NW Transmit & phase",
                    default=0.0, min = 0, max =31, slider=False).set_pos(col=0)
    NW_PhaseT = IntItem("",
                    default=0.0, min = 0, max =31, slider=False).set_pos(col=1)

    NE_TA = IntItem("NE Transmit & phase",
                    default=0.0, min = 0, max =31, slider=False).set_pos(col=2)
    NE_PhaseT = IntItem("",
                    default=0.0, min = 0, max =31, slider=False).set_pos(col=3)

    SW_RA = IntItem("SW Receive & phase",
                             default=0.0, min=0, max=31, slider=False).set_pos(col=0)
    SW_PhaseR = IntItem("",default=0.0, min = 0, max=31, slider=False).set_pos(col=1)

    SE_RA = IntItem("SE Receive & phase",
                             default=0.0, min=0, max=31, slider=False).set_pos(col=2)
    SE_PhaseR = IntItem("",default=0.0, min = 0, max =31, slider=False).set_pos(col=3)

    SW_TA = IntItem("SW Transmit & phase",
                    default=0.0, min = 0, max =31, slider=False).set_pos(col=0)
    SW_PhaseT = IntItem("",
                    default=0.0, min = 0, max =31, slider=False).set_pos(col=1)

    SE_TA = IntItem("SE Transmit & phase",
                    default=0.0, min = 0, max =31, slider=False).set_pos(col=2)
    SE_PhaseT = IntItem("",
                    default=0.0, min = 0, max =31, slider=False).set_pos(col=3)
    _eg = EndGroup("Amplitude and Phase Modulation")



if __name__ == "__main__":
    # Create QApplication
    import guidata
    _app = guidata.qapplication()

    e = TestParameters()

    print(e)
    if e.edit():
        print(e)
    e.view()