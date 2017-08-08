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

#ifndef LFPANALYSISDIALOG_H
#define LFPANALYSISDIALOG_H

#include <QDialog>
#include <QtGui>

using namespace std;

class QPushButton;
class QComboBox;
class QSpinBox;
class LfpPlot;
class DigInPlot;
class LfpScopeDialog;
class SignalProcessor;
class SignalSources;
class SignalChannel;
class LfpAnalysisPlot;

class LfpAnalysisDialog : public QDialog
{
    Q_OBJECT
public:
    explicit LfpAnalysisDialog(LfpPlot *inLfpPlot,
                              SignalProcessor *inSignalProcessor,
                              SignalChannel *initialChannel, QWidget *parent = 0);
    void setYScale(int index);
    void setSampleRate(double newSampleRate);
    void updateWaveform(int numBlocks);
    void setNewChannel(SignalChannel* newChannel);
    void expandYScale();
    void contractYScale();
signals:
    
public slots: 

private slots:
    void changeYScale(int index);
    void changeTScale(int index);
    void changeErrorbarState(bool state);
    void startLfpAnalysis();
    void stopLfpAnalysis();
    void updateAnalysisPlot();
    void changeTStepScale(int index);
private:


    QVector<int> yScaleList;
    QVector<int> tScaleList;
    QVector<int> tStepList;

    double sampleRate;
    double tStepInSeconds;
    double tScaleInSeconds;

    bool errorbarState;

    QComboBox *yScaleComboBox;
    QComboBox *tScaleComboBox;
    QComboBox *tStepComboBox;

    QPushButton *startButton;
    QPushButton *stopButton;

    QTimer *tStepTimer; //timer for analysis to run as frequent as defined in tStepComboBox

    SignalProcessor *signalProcessor;
    SignalChannel *currentChannel;
    LfpPlot *lfpPlot;

    LfpAnalysisPlot *analysisPlot;
};

#endif // LFPANALYSISDIALOG_H
