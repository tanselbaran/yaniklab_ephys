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

#ifndef LFPPLOT_H
#define LFPPLOT_H

#define LFPPLOT_X_SIZE 320
#define LFPPLOT_Y_SIZE 346
#define BUFFER_SIZE 25000
#include <QWidget>

using namespace std;

class SignalProcessor;
class LfpScopeDialog;
class SignalChannel;

class LfpPlot : public QWidget
{
    Q_OBJECT
public:
    explicit LfpPlot(SignalProcessor *inSignalProcessor, SignalChannel *initialChannel,
                       LfpScopeDialog *inSpikeScopeDialog, QWidget *parent = 0);
    void setYScale(int newYScale);
    void setSampleRate(double newSampleRate);
    void updateWaveform(int numBlocks);
    void setMaxNumLfpWaveforms(int num);
    void clearScope();
    void setVoltageTriggerMode(bool voltageMode);
    void setVoltageThreshold(int threshold);
    void setDigitalTriggerChannel(int channel);
    void setDigitalEdgePolarity(bool risingEdge);
    void setNewChannel(SignalChannel* newChannel);

    void setDisplayStateOfAverageLfpInPlot(bool show);
    void setDisplayStateOfEachLfpInPlot(bool show);

    bool getDisplayStateOfAverageLfpInPlot();
    bool getDisplayStateOfEachLfpInPlot();

    QSize minimumSizeHint() const;
    QSize sizeHint() const;

    LfpScopeDialog *lfpScopeDialog;


    //These variables are used in Lfp Analysis Plot
    QVector<QVector<double> > lfpWaveform;
    QVector<double> meanLfpWaveform;
    int numLfpWaveforms;
    int maxNumLfpWaveforms;
    int totalTSteps;
    int lfpWaveformIndex;
    int preTriggerTSteps;
    double tStepMsec;
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
    void updateLfpPlot(double rms);
    void initializeDisplay();

    SignalProcessor *signalProcessor;

    QVector<double> lfpWaveformBuffer;
    QVector<int> digitalInputBuffer;

    bool voltageTriggerMode;
    int voltageThreshold;
    int digitalTriggerChannel;
    bool digitalEdgePolarity;

    int bufferIndex;
    int bufferSizeUsed;
    bool startingNewChannel;
    int rmsDisplayPeriod;

    bool showAverageInPlot;
    bool showEachInPlot;

    SignalChannel *selectedChannel;

    QRect frame;

    int yScale;
    double savedRms;

    QPixmap pixmap;

    QVector<QVector<QColor> > scopeColors;
    
};

#endif // LFPPLOT_H
