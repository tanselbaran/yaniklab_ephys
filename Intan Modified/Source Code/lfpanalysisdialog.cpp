//  ------------------------------------------------------------------------
//
//  This file is part of the Intan Technologies RHD2000 Interface
//  Version 1.5.1
//  Copyright (C) 2013-2017 Intan Technologies
//
//  ------------------------------------------------------------------------
//
//  This program is free software: you can redistribute it and/or modify
//  it under the terms of the GNU Lesser General Public License as published
//  by the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU Lesser General Public License for more details.
//
//  You should have received a copy of the GNU Lesser General Public License
//  along with this program.  If not, see <http://www.gnu.org/licenses/>.

#include <QtGui>

#if QT_VERSION >= QT_VERSION_CHECK(5,0,0)
#include <QtWidgets>
#endif
#include <iostream>

#include "globalconstants.h"
#include "lfpscopedialog.h"
#include "lfpanalysisdialog.h"
#include "signalchannel.h"
#include "signalgroup.h"
#include "lfpplot.h"
#include "diginplot.h"
#include "lfpanalysisplot.h"



LfpAnalysisDialog::LfpAnalysisDialog(LfpPlot *inLfpPlot, SignalProcessor *inSignalProcessor,
                                     SignalChannel *initialChannel, QWidget *parent) :
    QDialog(parent)
{

    errorbarState = false;
    setWindowTitle(tr("LFP Analysis Scope"));

    currentChannel = initialChannel;
    signalProcessor = inSignalProcessor;
    lfpPlot = inLfpPlot;

    analysisPlot = new LfpAnalysisPlot(lfpPlot,signalProcessor,currentChannel,this,this);

    // Y Scale adjustment;
    yScaleList.append(50);
    yScaleList.append(100);
    yScaleList.append(200);
    yScaleList.append(500);
    yScaleList.append(1000);
    yScaleList.append(2000);
    yScaleList.append(5000);

    yScaleComboBox = new QComboBox();
    for (int i = 0; i < yScaleList.size(); ++i) {
        yScaleComboBox->addItem("+/-" + QString::number(yScaleList[i]) +
                                " " + QSTRING_MU_SYMBOL + "V");
    }
    yScaleComboBox->setCurrentIndex(4);


    connect(yScaleComboBox, SIGNAL(currentIndexChanged(int)),
            this, SLOT(changeYScale(int)));

    //total time scale


    tScaleList.append(10*60);
    tScaleList.append(20*60);
    tScaleList.append(30*60);
    tScaleList.append(45*60);
    tScaleList.append(60*60);

    tScaleComboBox = new QComboBox();
    tScaleComboBox->addItem(tr("10 minutes"));
    tScaleComboBox->addItem(tr("20 minutes"));
    tScaleComboBox->addItem(tr("30 minutes"));
    tScaleComboBox->addItem(tr("45 minutes"));
    tScaleComboBox->addItem(tr("60 minutes"));
    tScaleComboBox->setCurrentIndex(0);
    changeTScale(0);

    connect(tScaleComboBox, SIGNAL(currentIndexChanged(int)),
            this, SLOT(changeTScale(int)));

    //Initialize and connect timer
    tStepTimer = new QTimer(this);

    connect(tStepTimer, SIGNAL(timeout()),
            this, SLOT(updateAnalysisPlot()));



    //Step Size of measurements
    tStepList.append(10);
    tStepList.append(30);
    tStepList.append(60);
    tStepList.append(90);
    tStepList.append(120);
    tStepList.append(1);

    tStepComboBox = new QComboBox();
    tStepComboBox->addItem(tr("10 seconds"));
    tStepComboBox->addItem(tr("30 seconds"));
    tStepComboBox->addItem(tr("60 seconds"));
    tStepComboBox->addItem(tr("90 seconds"));
    tStepComboBox->addItem(tr("120 seconds"));
    tStepComboBox->addItem(tr("1 seconds FOR DEBUG"));

    tStepComboBox->setCurrentIndex(0);
    changeTStepScale(0);

    connect(tStepComboBox, SIGNAL(currentIndexChanged(int)),
            this, SLOT(changeTStepScale(int)));


    //Start Stop Button Adjustments
    startButton = new QPushButton(tr("Start"));
    stopButton = new QPushButton(tr("Stop"));

    stopButton->setEnabled(false);

    connect(startButton, SIGNAL(clicked()),
            this, SLOT(startLfpAnalysis()));
    connect(stopButton, SIGNAL(clicked()),
            this, SLOT(stopLfpAnalysis()));



    //Errorbar Options
    QCheckBox *errorbarDisplayChackBox = new QCheckBox(tr("Display Errorbar"));

    connect(errorbarDisplayChackBox, SIGNAL(clicked(bool)),
            this, SLOT(changeErrorbarState(bool)));
    errorbarState = false;


    QHBoxLayout *startStopLayout = new QHBoxLayout;
    startStopLayout->addWidget(startButton);
    startStopLayout->addWidget(stopButton);
    startStopLayout->addStretch(1);


    QVBoxLayout *leftLayout = new QVBoxLayout;
    leftLayout->addWidget(new QLabel(tr("Plot Scalings:")));
    leftLayout->addWidget(yScaleComboBox);
    leftLayout->addWidget(tScaleComboBox);
    leftLayout->addWidget(new QLabel(tr("Acquiring Frequency")));
    leftLayout->addWidget(tStepComboBox);
    leftLayout->addWidget(new QLabel(tr("Start/Stop the Analysis")));
    leftLayout->addLayout(startStopLayout);
    leftLayout->addWidget(new QLabel(tr("Display Settings")));
    leftLayout->addWidget(errorbarDisplayChackBox);
    leftLayout->addStretch(1);

    QHBoxLayout *mainLayout = new QHBoxLayout;
    mainLayout->addLayout(leftLayout);
    mainLayout->addWidget(analysisPlot);
    mainLayout->setStretch(0, 0);
    mainLayout->setStretch(1, 1);

    setLayout(mainLayout);

}

void LfpAnalysisDialog::changeYScale(int index)
{
    analysisPlot->setYScale(yScaleList[index]);
}

void LfpAnalysisDialog::setYScale(int index)
{
    yScaleComboBox->setCurrentIndex(index);
    analysisPlot->setYScale(yScaleList[index]);
}

void LfpAnalysisDialog::setSampleRate(double newSampleRate)
{
    analysisPlot->setSampleRate(newSampleRate);
}

void LfpAnalysisDialog::updateWaveform(int numBlocks)
{
    //analysisPlot->updateWaveform(numBlocks);
}

void LfpAnalysisDialog::setNewChannel(SignalChannel *newSignalChannel)
{
    currentChannel = newSignalChannel;
    analysisPlot->setNewChannel(newSignalChannel);
}

void LfpAnalysisDialog::changeErrorbarState(bool state)
{
    errorbarState = state;
    analysisPlot->setErrorbarDisplayState(state);
}

void LfpAnalysisDialog::startLfpAnalysis(){
    stopButton->setEnabled(true);
    startButton->setEnabled(false);
    tStepTimer->start();
    analysisPlot->applyStartProcess();
    tStepComboBox->setEnabled(false); //prevent any changes during running
}

void LfpAnalysisDialog::stopLfpAnalysis(){
    stopButton->setEnabled(false);
    startButton->setEnabled(true);
    tStepTimer->stop();
    analysisPlot->applyStopProcess();
    tStepComboBox->setEnabled(true); //enable modifications in the step size
}

void LfpAnalysisDialog::changeTStepScale(int index){

    tStepInSeconds = tStepList[index];
    tStepTimer->setInterval(tStepList[index]*1000);
    //Inform AnalysisPlot from this change ....
    analysisPlot->setTStepValue(tStepList[index]);
}

void LfpAnalysisDialog::updateAnalysisPlot(){

     analysisPlot->updateWaveform();
}

void LfpAnalysisDialog::expandYScale(){
    if (yScaleComboBox->currentIndex() > 0) {
        yScaleComboBox->setCurrentIndex(yScaleComboBox->currentIndex() - 1);
        changeYScale(yScaleComboBox->currentIndex());
    }
}

void LfpAnalysisDialog::contractYScale(){
    if (yScaleComboBox->currentIndex() < yScaleList.size() - 1) {
        yScaleComboBox->setCurrentIndex(yScaleComboBox->currentIndex() + 1);
        changeYScale(yScaleComboBox->currentIndex());
    }
}

void LfpAnalysisDialog::changeTScale(int index){

    analysisPlot->setTScale(tScaleList[index]);

}

