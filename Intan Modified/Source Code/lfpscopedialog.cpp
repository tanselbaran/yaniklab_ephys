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
#include "signalchannel.h"
#include "signalgroup.h"
#include "lfpplot.h"
#include "diginplot.h"
#include "lfpanalysisdialog.h"

// Lfp scope dialog.
// This dialog allows users to view 250-msec snippets of neural lfps triggered
// either from a selectable voltage threshold or a digital input threshold.  Multiple
// lfps are superimposed on the display so that users can compare lfp shapes.

LfpScopeDialog::LfpScopeDialog(SignalProcessor *inSignalProcessor, SignalSources *inSignalSources,
                                   SignalChannel *initialChannel, QWidget *parent) :
    QDialog(parent)
{
    setWindowTitle(tr("LFP Scope"));

    lfpAnalysisDialog = 0;

    signalProcessor = inSignalProcessor;
    signalSources = inSignalSources;

    lfpPlot = new LfpPlot(signalProcessor, initialChannel, this, this);
    digInPlot = new DigInPlot(signalProcessor, initialChannel, this, this);
    currentChannel = initialChannel;

    resetToZeroButton = new QPushButton(tr("Zero"));
    clearScopeButton = new QPushButton(tr("Clear Scope"));
    applyToAllButton = new QPushButton(tr("Apply to Entire Port"));

    enableLfpAnalysisButton = new QPushButton(tr("Enable LFP Analysis"));

    connect(resetToZeroButton, SIGNAL(clicked()),
            this, SLOT(resetThresholdToZero()));
    connect(clearScopeButton, SIGNAL(clicked()),
            this, SLOT(clearScope()));
    connect(applyToAllButton, SIGNAL(clicked()),
            this, SLOT(applyToAll()));
    connect(enableLfpAnalysisButton, SIGNAL(clicked()),
            this,SLOT(enableLfpAnalysis()));

    triggerTypeComboBox = new QComboBox();
    triggerTypeComboBox->addItem(tr("Voltage Threshold"));
    triggerTypeComboBox->addItem(tr("Digital Input"));
    triggerTypeComboBox->setCurrentIndex(1);

    connect(triggerTypeComboBox, SIGNAL(currentIndexChanged(int)),
            this, SLOT(setTriggerType(int)));

    thresholdSpinBox = new QSpinBox();
    thresholdSpinBox->setRange(-5000, 5000);
    thresholdSpinBox->setSingleStep(5);
    thresholdSpinBox->setValue(0);

    connect(thresholdSpinBox, SIGNAL(valueChanged(int)),
            this, SLOT(setVoltageThreshold(int)));

    QHBoxLayout *thresholdSpinBoxLayout = new QHBoxLayout;
    thresholdSpinBoxLayout->addWidget(resetToZeroButton);
    thresholdSpinBoxLayout->addWidget(thresholdSpinBox);
    thresholdSpinBoxLayout->addWidget(new QLabel(QSTRING_MU_SYMBOL + "V"));
    // thresholdSpinBoxLayout->addStretch(1);

    digitalInputComboBox = new QComboBox();
    digitalInputComboBox->addItem(tr("Digital Input 0"));
    digitalInputComboBox->addItem(tr("Digital Input 1"));
    digitalInputComboBox->addItem(tr("Digital Input 2"));
    digitalInputComboBox->addItem(tr("Digital Input 3"));
    digitalInputComboBox->addItem(tr("Digital Input 4"));
    digitalInputComboBox->addItem(tr("Digital Input 5"));
    digitalInputComboBox->addItem(tr("Digital Input 6"));
    digitalInputComboBox->addItem(tr("Digital Input 7"));
    digitalInputComboBox->addItem(tr("Digital Input 8"));
    digitalInputComboBox->addItem(tr("Digital Input 9"));
    digitalInputComboBox->addItem(tr("Digital Input 10"));
    digitalInputComboBox->addItem(tr("Digital Input 11"));
    digitalInputComboBox->addItem(tr("Digital Input 12"));
    digitalInputComboBox->addItem(tr("Digital Input 13"));
    digitalInputComboBox->addItem(tr("Digital Input 14"));
    digitalInputComboBox->addItem(tr("Digital Input 15"));
    digitalInputComboBox->setCurrentIndex(1);

    connect(digitalInputComboBox, SIGNAL(currentIndexChanged(int)),
            this, SLOT(setDigitalInput(int)));

    edgePolarityComboBox = new QComboBox();
    edgePolarityComboBox->addItem(tr("Rising Edge"));
    edgePolarityComboBox->addItem(tr("Falling Edge"));
    edgePolarityComboBox->setCurrentIndex(0);

    connect(edgePolarityComboBox, SIGNAL(currentIndexChanged(int)),
            this, SLOT(setEdgePolarity(int)));

    numLfpsComboBox = new QComboBox();
    numLfpsComboBox->addItem(tr("Show 10 LFPs"));
    numLfpsComboBox->addItem(tr("Show 20 LFPs"));
    numLfpsComboBox->addItem(tr("Show 30 Lfps"));
    numLfpsComboBox->setCurrentIndex(1);

    connect(numLfpsComboBox, SIGNAL(currentIndexChanged(int)),
            this, SLOT(setNumLfps(int)));

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

    QVBoxLayout *triggerLayout = new QVBoxLayout;
    triggerLayout->addWidget(new QLabel(tr("Type:")));
    triggerLayout->addWidget(triggerTypeComboBox);
    triggerLayout->addWidget(new QLabel(tr("Voltage Threshold:")));
    triggerLayout->addLayout(thresholdSpinBoxLayout);
    triggerLayout->addWidget(new QLabel(tr("(or click in scope to set)")));
    triggerLayout->addWidget(new QLabel(tr("Digital Source:")));
    triggerLayout->addWidget(digitalInputComboBox);
    triggerLayout->addWidget(edgePolarityComboBox);

    averageLfpButton = new QPushButton(tr("mean LFP"));
    individualLfpButton = new QPushButton(tr("all LFPs"));

    connect(averageLfpButton, SIGNAL(clicked()),
            this, SLOT(changeDisplaySettingOfAverageLfp()));

    connect(individualLfpButton, SIGNAL(clicked()),
                    this, SLOT(changeDisplaySettingOfEachLfp()));
    QHBoxLayout *lfpButtonsLayout = new QHBoxLayout;
    lfpButtonsLayout->addWidget(averageLfpButton);
    lfpButtonsLayout->addWidget(individualLfpButton);

    QVBoxLayout *displayLayout = new QVBoxLayout;
    displayLayout->addLayout(lfpButtonsLayout);
    displayLayout->addWidget(new QLabel(tr("Voltage Scale:")));
    displayLayout->addWidget(yScaleComboBox);
    displayLayout->addWidget(numLfpsComboBox);
    displayLayout->addWidget(clearScopeButton);

    QGroupBox *triggerGroupBox = new QGroupBox(tr("Trigger Settings"));
    triggerGroupBox->setLayout(triggerLayout);

    QGroupBox *displayGroupBox = new QGroupBox(tr("Display Settings"));
    displayGroupBox->setLayout(displayLayout);

    QVBoxLayout *leftLayout = new QVBoxLayout;
    leftLayout->addWidget(triggerGroupBox);
    leftLayout->addWidget(applyToAllButton);
    leftLayout->addWidget(enableLfpAnalysisButton);
    leftLayout->addWidget(displayGroupBox);
    leftLayout->addStretch(1);

    QVBoxLayout *rightLayout = new QVBoxLayout;
    rightLayout->addWidget(digInPlot);
    rightLayout->addWidget(lfpPlot);
    rightLayout->addStretch(1);

    QHBoxLayout *mainLayout = new QHBoxLayout;
    mainLayout->addLayout(leftLayout);
    mainLayout->addLayout(rightLayout);
    mainLayout->setStretch(0, 0);
    mainLayout->setStretch(1, 1);

    setLayout(mainLayout);

    setTriggerType(triggerTypeComboBox->currentIndex());
    setNumLfps(numLfpsComboBox->currentIndex());
    setVoltageThreshold(thresholdSpinBox->value());
    setDigitalInput(digitalInputComboBox->currentIndex());
    setEdgePolarity(edgePolarityComboBox->currentIndex());

    //set everychannel to default settings of LFP Scope dialog once it is initialized
    for (int i = 0; i < currentChannel->signalGroup->numChannels(); ++i) {
        currentChannel->signalGroup->channel[i].voltageTriggerMode = currentChannel->voltageTriggerMode;
        currentChannel->signalGroup->channel[i].voltageThreshold = currentChannel->voltageThreshold;
        currentChannel->signalGroup->channel[i].digitalTriggerChannel = currentChannel->digitalTriggerChannel;
        currentChannel->signalGroup->channel[i].digitalEdgePolarity = currentChannel->digitalEdgePolarity;
    }
}

void LfpScopeDialog::changeYScale(int index)
{
    lfpPlot->setYScale(yScaleList[index]);
}

void LfpScopeDialog::setYScale(int index)
{
    yScaleComboBox->setCurrentIndex(index);
    lfpPlot->setYScale(yScaleList[index]);
}

void LfpScopeDialog::setSampleRate(double newSampleRate)
{
    lfpPlot->setSampleRate(newSampleRate);
    digInPlot->setSampleRate(newSampleRate);

    if (lfpAnalysisDialog){
        lfpAnalysisDialog->setSampleRate(newSampleRate);
    }

}

// Select a voltage trigger if index == 0.
// Select a digital input trigger if index == 1.
void LfpScopeDialog::setTriggerType(int index)
{
    thresholdSpinBox->setEnabled(index == 0);
    resetToZeroButton->setEnabled(index == 0);
    digitalInputComboBox->setEnabled(index == 1);
    edgePolarityComboBox->setEnabled(index == 1);
    lfpPlot->setVoltageTriggerMode(index == 0);
}

void LfpScopeDialog::resetThresholdToZero()
{
    thresholdSpinBox->setValue(0);
}

void LfpScopeDialog::updateWaveform(int numBlocks)
{
    lfpPlot->updateWaveform(numBlocks);
    digInPlot->updateWaveform(numBlocks);

}

// Set number of Lfps plotted superimposed.
void LfpScopeDialog::setNumLfps(int index)
{
    int num;

    switch (index) {
    case 0: num = 10; break;
    case 1: num = 20; break;
    case 2: num = 30; break;
    }

    lfpPlot->setMaxNumLfpWaveforms(num);
    digInPlot->setMaxNumDigInWaveforms(num);
}

void LfpScopeDialog::clearScope()
{
    lfpPlot->clearScope();
    digInPlot->clearScope();
}

void LfpScopeDialog::setDigitalInput(int index)
{
    lfpPlot->setDigitalTriggerChannel(index);
    digInPlot->setDigitalTriggerChannel(index);
}

void LfpScopeDialog::setVoltageThreshold(int value)
{
    lfpPlot->setVoltageThreshold(value);

}

void LfpScopeDialog::setVoltageThresholdDisplay(int value)
{
    thresholdSpinBox->setValue(value);
}

void LfpScopeDialog::setEdgePolarity(int index)
{
    lfpPlot->setDigitalEdgePolarity(index == 0);
    digInPlot->setDigitalEdgePolarity(index == 0);
}

// Set Lfp Scope to a new signal channel source.
void LfpScopeDialog::setNewChannel(SignalChannel* newChannel)
{
    lfpPlot->setNewChannel(newChannel);
    digInPlot->setNewChannel(newChannel);

    if(lfpAnalysisDialog){

        lfpAnalysisDialog->setNewChannel(newChannel);

    }

    currentChannel = newChannel;
    if (newChannel->voltageTriggerMode) {
        triggerTypeComboBox->setCurrentIndex(0);
    } else {
        triggerTypeComboBox->setCurrentIndex(1);
    }

    thresholdSpinBox->setValue(newChannel->voltageThreshold);
    digitalInputComboBox->setCurrentIndex(newChannel->digitalTriggerChannel);
    if (newChannel->digitalEdgePolarity) {
        edgePolarityComboBox->setCurrentIndex(0);
    } else {
        edgePolarityComboBox->setCurrentIndex(1);
    }
}

void LfpScopeDialog::expandYScale()
{
    if (yScaleComboBox->currentIndex() > 0) {
        yScaleComboBox->setCurrentIndex(yScaleComboBox->currentIndex() - 1);
        changeYScale(yScaleComboBox->currentIndex());
    }
}

void LfpScopeDialog::contractYScale()
{
    if (yScaleComboBox->currentIndex() < yScaleList.size() - 1) {
        yScaleComboBox->setCurrentIndex(yScaleComboBox->currentIndex() + 1);
        changeYScale(yScaleComboBox->currentIndex());
    }
}

// Apply trigger settings to all channels on selected port.
void LfpScopeDialog::applyToAll()
{
    QMessageBox::StandardButton r;
    r = QMessageBox::question(this, tr("Trigger Settings"),
                                 tr("Do you really want to copy the current channel's trigger "
                                    "settings to <b>all</b> amplifier channels on this port?"),
                                 QMessageBox::Yes | QMessageBox::No);
    if (r == QMessageBox::Yes) {
        for (int i = 0; i < currentChannel->signalGroup->numChannels(); ++i) {
            currentChannel->signalGroup->channel[i].voltageTriggerMode = currentChannel->voltageTriggerMode;
            currentChannel->signalGroup->channel[i].voltageThreshold = currentChannel->voltageThreshold;
            currentChannel->signalGroup->channel[i].digitalTriggerChannel = currentChannel->digitalTriggerChannel;
            currentChannel->signalGroup->channel[i].digitalEdgePolarity = currentChannel->digitalEdgePolarity;
        }
    }
}

void LfpScopeDialog::changeDisplaySettingOfAverageLfp()
{
    bool state = lfpPlot->getDisplayStateOfAverageLfpInPlot();
    lfpPlot->setDisplayStateOfAverageLfpInPlot(!state);
    digInPlot->showAverageDigInInPlot(!state);

}
void LfpScopeDialog::changeDisplaySettingOfEachLfp()
{
    bool state = lfpPlot->getDisplayStateOfEachLfpInPlot();
    lfpPlot->setDisplayStateOfEachLfpInPlot(!state);
    digInPlot->showEachDigInInPlot(!state);
}

void LfpScopeDialog::enableLfpAnalysis()
{
    if (!lfpAnalysisDialog) {
        lfpAnalysisDialog = new LfpAnalysisDialog( lfpPlot, signalProcessor, currentChannel, this);
        // add any 'connect' statements here
    }

    lfpAnalysisDialog->show();
    lfpAnalysisDialog->raise();
    lfpAnalysisDialog->activateWindow();
    lfpAnalysisDialog->setYScale(yScaleComboBox->currentIndex());

}
