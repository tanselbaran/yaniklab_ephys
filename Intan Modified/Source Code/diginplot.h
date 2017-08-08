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

#ifndef DIGINPLOT_H
#define DIGINPLOT_H

#define LFPPLOT_X_SIZE 320
#define LFPPLOT_Y_SIZE 346
#define BUFFER_SIZE 25000
#include <QWidget>

using namespace std;

class SignalProcessor;
class LfpScopeDialog;
class SignalChannel;

class DigInPlot : public QWidget
{
    Q_OBJECT
public:
    explicit DigInPlot(SignalProcessor *inSignalProcessor, SignalChannel *initialChannel,
                       LfpScopeDialog *inSpikeScopeDialog, QWidget *parent = 0);
    void setYScale(int newYScale);
    void setSampleRate(double newSampleRate);
    void updateWaveform(int numBlocks);
    void setMaxNumDigInWaveforms(int num);
    void clearScope();
    void setVoltageTriggerMode(bool voltageMode);
    void setVoltageThreshold(int threshold);
    void setDigitalTriggerChannel(int channel);
    void setDigitalEdgePolarity(bool risingEdge);
    void setNewChannel(SignalChannel* newChannel);

    void showAverageDigInInPlot(bool show);
    void showEachDigInInPlot(bool show);

    QSize minimumSizeHint() const;
    QSize sizeHint() const;

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
    void updateDigInPlot(double rms);
    void initializeDisplay();

    SignalProcessor *signalProcessor;
    LfpScopeDialog *lfpScopeDialog;

    QVector<QVector<double> > digInWaveform;
    QVector<double> meanDigInWaveform;
    QVector<int> digitalInputBuffer;
    int digInWaveformIndex;
    int numDigInWaveforms;
    int maxNumDigInWaveforms;
    bool voltageTriggerMode;
    int voltageThreshold;
    int digitalTriggerChannel;
    bool digitalEdgePolarity;

    int preTriggerTSteps;
    int totalTSteps;
    int bufferIndex;
    int bufferSizeUsed;
    bool startingNewChannel;
    int rmsDisplayPeriod;

    bool showAverageInPlot;
    bool showEachInPlot;

    SignalChannel *selectedChannel;

    QRect frame;

    double tStepMsec;
    int yScale;
    double savedRms;

    QPixmap pixmap;

    QVector<QVector<QColor> > scopeColors;
    
};

#endif // DIGINPLOT_H
