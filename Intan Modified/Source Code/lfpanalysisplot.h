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

#ifndef LFPANALYSISPLOT_H
#define LFPANALYSISPLOT_H

#define LFPANALYSISPLOT_X_SIZE 320
#define LFPANALYSISPLOT_Y_SIZE 346
#define BUFFER_SIZE 25000
#include <QWidget>

using namespace std;

class SignalProcessor;
class LfpAnalysisDialog;
class LfpScopeDialog;
class SignalChannel;
class LfpPlot;

class LfpAnalysisPlot : public QWidget
{
    Q_OBJECT
public:
    explicit LfpAnalysisPlot(LfpPlot *inlfpPlot, SignalProcessor *inSignalProcessor, SignalChannel *initialChannel,
                       LfpAnalysisDialog *inLfpAnalysisDialog, QWidget *parent = 0);

    void setYScale(int newYScale);
    void setSampleRate(double newSampleRate);
    void updateWaveform();
    void setMaxNumLfpWaveforms();
    void clearScope();
    void setNewChannel(SignalChannel* newChannel);

    void setTScale(int t);
    void setTStepValue(int t);
    void setErrorbarDisplayState(bool);

    void applyStartProcess();
    void applyStopProcess();


    QSize minimumSizeHint() const;
    QSize sizeHint() const;

    LfpAnalysisDialog *lfpAnalysisDialog;
signals:
    
public slots:

protected:
    void paintEvent(QPaintEvent *event);
    void closeEvent(QCloseEvent *event);
    void mousePressEvent(QMouseEvent *event);
    void wheelEvent(QWheelEvent *event);
    void keyPressEvent(QKeyEvent *event);
    void resizeEvent(QResizeEvent* event);

private:
    void drawAxisLines();
    void drawAxisText();
    void updateLfpAnalysisPlot();
    void initializeDisplay();

    SignalProcessor *signalProcessor;
    LfpPlot *lfpPlot;

    // Necessary components for Analysis based on each LFP waveform stored
    QVector<QVector<double> > lfpWaveform; //For one instance retrieved from LfpPlot class
    QVector<QVector<double> > lfpAnalysisData; //Analysis results is stored here-- Min, Max, Max-Min etc.
    QVector<double> mLfpAnalysisData;
    QVector<double> stdLfpAnalysisData;

    //Necessary components for analysis based on overall LFP average
    QVector<double> meanLfpWaveform;
    QVector<double> meanLfpAnalysisData;
    QVector<double> stdOfmeanLfpAnalysisData;

    int numLfpWaveforms;
    int maxNumLfpWaveforms;
    int totalTSteps;

    bool startingNewChannel;
    bool errorbarDisplayState;

    int tScaleInSec;
    SignalChannel *selectedChannel;

    QRect frame;

    int tStepSec;
    int yScale;


    QPixmap pixmap;

    QVector<QVector<QColor> > scopeColors;

};

#endif // LFPANALYSISPLOT_H
