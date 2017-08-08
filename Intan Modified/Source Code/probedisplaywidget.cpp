



#include <QtGui>
#if QT_VERSION >= QT_VERSION_CHECK(5,0,0)
#include <QtWidgets>
#endif
#include <qmath.h>
#include <iostream>

#include "probedisplaywidget.h"
#include "waveplot.h"
#include "probe.h"
#include "globalconstants.h"
#include "signalchannel.h"

ProbeDisplayWidget::ProbeDisplayWidget(WavePlot *inWavePlot, QWidget *parent) :

    QWidget(parent)
{
    wavePlot = inWavePlot;

    connect( wavePlot, SIGNAL(channelOrderRestored()) , this , SLOT(adjustGroupingOptions()));
    probe = 0;
    updateLayout();
    setUpDefaultProbes();
}

void ProbeDisplayWidget::setUpDefaultProbes(){
    //32 Channel neuronexus to Intan mapping
    QVector<int> neuronexusToIntan = {30,   26, 21, 17, 27, 22, 20, 25, 28, 23, 19, 24, 29, 18, 31, 16,
                                      0,    15, 2,  13, 8,  9,  7,  1,  6,  14, 10, 11, 5,  12, 4,  3};

    //'a2x16_10mm_100_500_177'
    selectProbeComboBox->addItem(tr("a2x16_10mm_100_500_177"));
    probeNameList.append(tr("a2x16_10mm_100_500_177"));
    probeNumberOfShanksList.append(2);
    probeTypeList.append(LINEAR_PROBE_TYPE);

    QVector<int> internalMapping = {0, 15, 1, 14, 2, 13, 3, 12, 4, 11, 5, 10, 6, 9, 7, 8};

    QVector<int> dummyMap;
    dummyMap.resize(32);

    for (int i = 0 ; i < 32 ; ++i){
        dummyMap[i] = neuronexusToIntan[internalMapping[i%16] + 16*(i/16)];
    }
    probeMapList.append(dummyMap);


}

void ProbeDisplayWidget::loadProbeFolder(){
    //Generate a Dummy Map;
    QVector<int> dummyMap;

    QString fileFullName = QFileDialog::getOpenFileName(this, tr("Selecct ProbeFile"), "C://",
                                                       "Probe File(*.dat)" );
    QFile probeFile(fileFullName);
    QFileInfo probeFileInfo(fileFullName);
    QString dummyName(probeFileInfo.fileName());

    probeNameList.append(dummyName.split(".")[0]);

    if(!probeFile.open(QFile::ReadOnly)){return;}

    QDataStream readStream(&probeFile);
    readStream.setVersion(QDataStream::Qt_4_8);
    readStream.setByteOrder(QDataStream::LittleEndian);

    //first 2Bytes is number of electrodes in the probe
    //means the length of map

    quint16 d;
    readStream >>  d ;

    dummyMap;
    dummyMap.resize((int) d);


    //Second 2Bytes for Number of Shanks
    readStream >>  d;
    int numberOfShanks = (int)d;
    probeNumberOfShanksList.append(numberOfShanks);

    //Third 2Bytes are Electrodes per shank NOT NEEDED

    readStream >> d;
    int electrodesPerShank = (int) d;
    //4th stream is the type ==0 for linear ==1 for Tetrote
    readStream >> d;
    int type = (d==0) ? LINEAR_PROBE_TYPE : TETROTE_PROBE_TYPE;
    probeTypeList.append(type);

    //rest is the data itself

    if(type == LINEAR_PROBE_TYPE){

        for(int i = 0 ; i < dummyMap.size() ; ++i){
            readStream >>  d;
            dummyMap[i] = (int) d;
        }
    }else{

        for(int i = 0 ; i < electrodesPerShank; ++i){
            for( int j = 0 ; j < numberOfShanks; ++j){
                int mapIndex = j*(dummyMap.size()/numberOfShanks) + i*4;
                readStream >> d;
                dummyMap[mapIndex] = (int)d; //0

                mapIndex++;
                readStream >> d;
                dummyMap[mapIndex] = (int)d; //1

                mapIndex++;
                readStream >> d;
                dummyMap[mapIndex] = (int)d; //2

                mapIndex++;
                readStream >> d;
                dummyMap[mapIndex] = (int)d; //3
            }
        }
    }

    probeMapList.append(dummyMap);
    //close the file
    probeFile.close();

    selectProbeComboBox->addItem(dummyName.split(".")[0]);

}

void ProbeDisplayWidget::groupWavePlots(int index){

//index 0 means no grouping
//index 1 means grouping by shank starting from botton to top

    if(index == 0){
        wavePlot->sortChannelsByNumber();
        wavePlot->refreshScreen();
    }else{
        wavePlot->arrengeDisplayOrder(probe->getMapArray());
    }

}

void ProbeDisplayWidget::updateLayout(){
    displayProbeNameLabel = new QLabel(tr("No Probe Selected"));

    loadProbeFolderButton = new QPushButton(tr("Load Probe"));

    selectProbeComboBox = new QComboBox();
    selectProbeComboBox->addItem(tr("NO PROBE SELECTED"));
    selectProbeComboBox->setCurrentIndex(0);
    probeNameList.append(tr("No Probe Selected"));
    probeTypeList.append(INVALID_PROBE_TYPE);
    QVector<int> dummy;
    probeMapList.append(dummy);
    probeNumberOfShanksList.append(0);

    connect(loadProbeFolderButton, SIGNAL(clicked()),
            this, SLOT(loadProbeFolder()));

    connect(selectProbeComboBox, SIGNAL(currentIndexChanged(int)),
                    this, SLOT(selectProbe(int)));


    QHBoxLayout *loadLayout = new QHBoxLayout;
    loadLayout->addWidget(loadProbeFolderButton);
    loadLayout->addWidget(selectProbeComboBox);
    loadLayout->addStretch(1);


    groupWavePlotsComboBox = new QComboBox();
    groupWavePlotsComboBox->addItem("DO NOT GROUP");
    groupWavePlotsComboBox->addItem("GROUP BY SHANK");
    groupWavePlotsComboBox->setCurrentIndex(0);
    groupWavePlotsComboBox->setEnabled(false);

    connect(groupWavePlotsComboBox, SIGNAL(currentIndexChanged(int)),
                    this, SLOT(groupWavePlots(int)));

    QVBoxLayout *settingsLayout = new QVBoxLayout;
    settingsLayout->addWidget(new QLabel(tr("Please Select Folder to Load Probes From: ")));
    settingsLayout->addLayout(loadLayout);
    settingsLayout->addWidget(groupWavePlotsComboBox);
    settingsLayout->addWidget(displayProbeNameLabel);
    settingsLayout->addStretch(1);

    mainLayout = new QVBoxLayout;
    mainLayout->addLayout(settingsLayout);
    if(probe) { mainLayout->addWidget(probe); }
    mainLayout->setStretch(0,0);
    mainLayout->setStretch(1,1);

    setLayout( mainLayout);
}

void ProbeDisplayWidget::selectProbe(int index){
    if(probe){
        mainLayout->removeWidget(probe);
        probe->~Probe();
        probe = 0;
        groupWavePlotsComboBox->setEnabled(false);
    }
    if(index != 0){
    probe = new Probe(probeNameList.at(index), probeTypeList.at(index),probeNumberOfShanksList.at(index),
                      probeMapList.at(index), wavePlot->selectedChannel(), wavePlot->getSignalSources(),this);

    connect(probe, SIGNAL(channelChanged(SignalChannel*)), this, SLOT(echoChannelChange(SignalChannel* )));

    mainLayout->addWidget(probe);
    groupWavePlotsComboBox->setEnabled(true);
    }
    displayProbeNameLabel->setText( probeNameList.at(index) );

}

void ProbeDisplayWidget::setNewChannel(SignalChannel *newChannel){
    if(probe) {probe->setNewChannel(newChannel);}
}

void ProbeDisplayWidget::echoChannelChange(SignalChannel *newChannel){
    wavePlot->setNewSelectedChannel(newChannel);
    //emit selectedChannelChanged(newChannel);
}

void ProbeDisplayWidget::adjustGroupingOptions(){
    groupWavePlotsComboBox->setCurrentIndex(0);
}
