TEMPLATE      = app

QT            += widgets multimedia

CONFIG        += static

macx:{
QMAKE_RPATHDIR += /users/intan/qt/5.7/clang_64/lib
QMAKE_RPATHDIR += /users/intan/downloads/
}

HEADERS       = \
    okFrontPanelDLL.h \
    rhd2000evalboard.h \
    rhd2000registers.h \
    rhd2000datablock.h \
    waveplot.h \
    mainwindow.h \
    signalprocessor.h \
    bandwidthdialog.h \
    renamechanneldialog.h \
    signalchannel.h \
    signalgroup.h \
    signalsources.h \
    spikescopedialog.h \
    spikeplot.h \
    keyboardshortcutdialog.h \
    randomnumber.h \
    impedancefreqdialog.h \
    globalconstants.h \
    triggerrecorddialog.h \
    setsaveformatdialog.h \
    helpdialoghighpassfilter.h \
    helpdialognotchfilter.h \
    helpdialogdacs.h \
    helpdialogcomparators.h \
    helpdialogchipfilters.h \
    auxdigoutconfigdialog.h \
    cabledelaydialog.h \
    helpdialogfastsettle.h \
    lfpscopedialog.h \
    lfpplot.h \
    diginplot.h \
    lfpanalysisdialog.h \
    lfpanalysisplot.h \
    probedisplaywidget.h \
    probe.h

SOURCES       = main.cpp \
    okFrontPanelDLL.cpp \
    rhd2000evalboard.cpp \
    rhd2000registers.cpp \
    rhd2000datablock.cpp \
    waveplot.cpp \
    mainwindow.cpp \
    signalprocessor.cpp \
    bandwidthdialog.cpp \
    renamechanneldialog.cpp \
    signalchannel.cpp \
    signalgroup.cpp \
    signalsources.cpp \
    spikescopedialog.cpp \
    spikeplot.cpp \
    keyboardshortcutdialog.cpp \
    randomnumber.cpp \
    impedancefreqdialog.cpp \
    triggerrecorddialog.cpp \
    setsaveformatdialog.cpp \
    helpdialoghighpassfilter.cpp \
    helpdialognotchfilter.cpp \
    helpdialogdacs.cpp \
    helpdialogcomparators.cpp \
    helpdialogchipfilters.cpp \
    auxdigoutconfigdialog.cpp \
    cabledelaydialog.cpp \
    helpdialogfastsettle.cpp \
    lfpscopedialog.cpp \
    lfpplot.cpp \
    diginplot.cpp \
    lfpanalysisdialog.cpp \
    lfpanalysisplot.cpp \
    probedisplaywidget.cpp \
    probe.cpp
    
RESOURCES     = RHD2000interface.qrc

macx:{
LIBS += -L$$PWD/../../Downloads/ -lokFrontPanel
INCLUDEPATH += $$PWD/../../Downloads
DEPENDPATH += $$PWD/../../Downloads
}
