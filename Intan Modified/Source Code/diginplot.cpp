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
#include <qmath.h>
#include <iostream>

#include "globalconstants.h"
#include "signalprocessor.h"
#include "signalchannel.h"
#include "lfpscopedialog.h"
#include  "diginplot.h"

// The LfpPlot widget displays a triggered neural lfp plot in the
// Lfp Scope dialog.  Multiple lfps are plotted on top of one another
// so users may compare their shapes.  The RMS value of the waveform is
// displayed in the plot.  Users may select a new threshold value by clicking
// on the plot.  Keypresses are used to change the voltage scale of the plot.

DigInPlot::DigInPlot(SignalProcessor *inSignalProcessor, SignalChannel *initialChannel,
                     LfpScopeDialog *inLfpScopeDialog, QWidget *parent) :
    QWidget(parent)
{
    signalProcessor = inSignalProcessor;
    lfpScopeDialog = inLfpScopeDialog;

    selectedChannel = initialChannel;
    startingNewChannel = true;
    rmsDisplayPeriod = 0;
    savedRms = 0.0;

    digInWaveformIndex = 0;
    numDigInWaveforms = 0;
    maxNumDigInWaveforms = 20;
    voltageTriggerMode = true;
    voltageThreshold = 0;
    digitalTriggerChannel = 0;
    digitalEdgePolarity = true;

    setBackgroundRole(QPalette::Window);
    setAutoFillBackground(true);
    setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);
    setFocusPolicy(Qt::StrongFocus);

    showAverageInPlot = true;
    showEachInPlot = false;

    int i;

    // We can plot up to 30 superimposed digIn waveforms on the scope.
    digInWaveform.resize(30);

    for (i = 0; i < digInWaveform.size(); ++i) {
        // Each waveform is 250 ms in duration.  We need 91 time steps for a 3 ms
        // waveform with the sample rate is set to its maximum value of 30 kS/s.
        digInWaveform[i].resize(BUFFER_SIZE);
        digInWaveform[i].fill(0.0);
    }

    // Buffers to hold recent history of digIn waveform and digital input,
    // used to find trigger events.
    digitalInputBuffer.resize(BUFFER_SIZE);
    digitalInputBuffer.fill(0);

    meanDigInWaveform.resize(BUFFER_SIZE);
    meanDigInWaveform.fill(0.0);

    // Set up vectors of varying plot colors so that older waveforms
    // are plotted in low-contrast gray and new waveforms are plotted
    // in high-contrast blue.  Older signals fade away, like phosphor
    // traces on old-school CRT oscilloscopes.
    scopeColors.resize(3);
    scopeColors[0].resize(10);
    scopeColors[1].resize(20);
    scopeColors[2].resize(30);

    for (i = 6; i < 10; ++i) scopeColors[0][i] = Qt::blue;
    for (i = 3; i < 6; ++i) scopeColors[0][i] = Qt::darkGray;
    for (i = 0; i < 3; ++i) scopeColors[0][i] = Qt::lightGray;

    for (i = 12; i < 20; ++i) scopeColors[1][i] = Qt::blue;
    for (i = 6; i < 12; ++i) scopeColors[1][i] = Qt::darkGray;
    for (i = 0; i < 6; ++i) scopeColors[1][i] = Qt::lightGray;

    for (i = 18; i < 30; ++i) scopeColors[2][i] = Qt::blue;
    for (i = 9; i < 18; ++i) scopeColors[2][i] = Qt::darkGray;
    for (i = 0; i < 9; ++i) scopeColors[2][i] = Qt::lightGray;

    // Default values that may be overwritten.
    yScale = 5000;
    setSampleRate(30000.0);
}

// Set voltage scale.
void DigInPlot::setYScale(int newYScale)
{
    yScale = newYScale;
    initializeDisplay();
}

// Set waveform sample rate.
void DigInPlot::setSampleRate(double newSampleRate)
{
    // Calculate time step, in msec.
    tStepMsec = 1000.0 / newSampleRate;

    // Calculate number of time steps in 3 msec sample.
    totalTSteps = qCeil(250.0 / tStepMsec) + 1;

    // Calculate number of time steps in the 1 msec pre-trigger
    // display interval.
    preTriggerTSteps = qCeil(50.0 / tStepMsec);

    // Clear old waveforms since the sample rate has changed.
    numDigInWaveforms = 0;
    startingNewChannel = true;

    bufferIndex = 0; // reset the index in the buffers
}

// Draw axis lines on display.
void DigInPlot::drawAxisLines()
{
    QPainter painter(&pixmap);
    painter.initFrom(this);

    painter.eraseRect(frame);

    painter.setPen(Qt::darkGray);

    // Draw box outline.
    painter.drawRect(frame);

    // Draw horizonal zero voltage line.
    painter.drawLine(frame.left(), frame.center().y(), frame.right(), frame.center().y());

    // Draw vertical lines at 0 ms and 1 ms.
    painter.drawLine(frame.left() + (1.0/5.0) * (frame.right() - frame.left()) + 1, frame.top(),
                      frame.left() + (1.0/5.0) * (frame.right() - frame.left()) + 1, frame.bottom());
    painter.drawLine(frame.left() + (2.0/5.0) * (frame.right() - frame.left()) + 1, frame.top(),
                      frame.left() + (2.0/5.0) * (frame.right() - frame.left()) + 1, frame.bottom());
    painter.drawLine(frame.left() + (3.0/5.0) * (frame.right() - frame.left()) + 1, frame.top(),
                      frame.left() + (3.0/5.0) * (frame.right() - frame.left()) + 1, frame.bottom());
    painter.drawLine(frame.left() + (4.0/5.0) * (frame.right() - frame.left()) + 1, frame.top(),
                      frame.left() + (4.0/5.0) * (frame.right() - frame.left()) + 1, frame.bottom());
    update();
}

// Draw text around axes.
void DigInPlot::drawAxisText()
{
    QPainter painter(&pixmap);
    painter.initFrom(this);
    const int textBoxWidth = painter.fontMetrics().width("+" + QString::number(yScale) + " " + QSTRING_MU_SYMBOL + "V");
    const int textBoxHeight = painter.fontMetrics().height();

    // Clear entire Widget display area.
    painter.eraseRect(rect());

    // Draw border around Widget display area.
    painter.setPen(Qt::darkGray);
    QRect rect(0, 0, width() - 1, height() - 1);
    painter.drawRect(rect);

    // If the selected channel is an amplifier channel, then write the channel name and number,
    // otherwise remind the user than non-amplifier channels cannot be displayed in DigIn Scope.
    if (selectedChannel) {
        if (selectedChannel->signalType == AmplifierSignal) {
            painter.drawText(frame.right() - textBoxWidth - 1, frame.top() - textBoxHeight - 1,
                              textBoxWidth, textBoxHeight,
                              Qt::AlignRight | Qt::AlignBottom, selectedChannel->nativeChannelName);
            painter.drawText(frame.left() + 3, frame.top() - textBoxHeight - 1,
                              textBoxWidth, textBoxHeight,
                              Qt::AlignLeft | Qt::AlignBottom, selectedChannel->customChannelName);
        } else {
            painter.drawText(frame.right() - 2 * textBoxWidth - 1, frame.top() - textBoxHeight - 1,
                              2 * textBoxWidth, textBoxHeight,
                              Qt::AlignRight | Qt::AlignBottom, tr("ONLY AMPLIFIER CHANNELS CAN BE DISPLAYED"));
        }
    }

    // Label the voltage axis.
    painter.drawText(frame.left() - textBoxWidth - 2, frame.top() - 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignRight | Qt::AlignTop,
                      "+1 LOGIC" ); //+ QString::number(yScale) + " " + QSTRING_MU_SYMBOL + "V");
    painter.drawText(frame.left() - textBoxWidth - 2, frame.center().y() - textBoxHeight / 2,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignRight | Qt::AlignVCenter, "0");
    painter.drawText(frame.left() - textBoxWidth - 2, frame.bottom() - textBoxHeight + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignRight | Qt::AlignBottom,
                      "-1 LOGIC" );//+ QString::number(yScale) + " " + QSTRING_MU_SYMBOL + "V");

    // Label the time axis.
    painter.drawText(frame.left() - textBoxWidth / 2, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignHCenter | Qt::AlignTop, "-50");
    painter.drawText(frame.left() + (1.0/5.0) * (frame.right() - frame.left()) + 1 - textBoxWidth / 2, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignHCenter | Qt::AlignTop, "0");
    painter.drawText(frame.left() + (2.0/5.0) * (frame.right() - frame.left()) + 1 - textBoxWidth / 2, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignHCenter | Qt::AlignTop, "50");
    painter.drawText(frame.left() + (3.0/5.0) * (frame.right() - frame.left()) + 1 - textBoxWidth / 2, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignHCenter | Qt::AlignTop, "100");
    painter.drawText(frame.left() + (4.0/5.0) * (frame.right() - frame.left()) + 1 - textBoxWidth / 2, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignHCenter | Qt::AlignTop, "150");
    painter.drawText(frame.right() - textBoxWidth + 1, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignRight | Qt::AlignTop, "200 ms");

    update();
}

// This function loads waveform data for the selected channel from the signal processor object,
// looks for trigger events, captures 3-ms snippets of the waveform after trigger events,
// measures the rms level of the waveform, and updates the display.
void DigInPlot::updateWaveform(int numBlocks)
{
    int i, index, index2;
    bool triggered;
    double rms;

    bufferSizeUsed = 20*SAMPLES_PER_DATA_BLOCK * numBlocks;
    // Make sure the selected channel is a valid amplifier channel
    if (!selectedChannel) return;
    if (selectedChannel->signalType != AmplifierSignal) return;

    int stream = selectedChannel->boardStream;
    int channel = selectedChannel->chipChannel;

    // Load recent waveform data and digital input data into our buffers.  Also, calculate
    // waveform RMS value.
    rms = 0.0;

    for (i = 0; i < SAMPLES_PER_DATA_BLOCK * numBlocks; ++i) {
        int dummyIndex = 1 + (i + bufferIndex- 1) % bufferSizeUsed;
        //if (dummyIndex == bufferSizeUsed || dummyIndex == 0) dummyIndex = 1;
        rms += (signalProcessor->amplifierPostFilter.at(stream).at(channel).at(i) *
                signalProcessor->amplifierPostFilter.at(stream).at(channel).at(i));
        digitalInputBuffer[dummyIndex] =  signalProcessor->boardDigIn.at(digitalTriggerChannel).at(i);
    }
    rms = qSqrt(rms / (SAMPLES_PER_DATA_BLOCK * numBlocks));

    // Find trigger events, and then copy waveform snippets to digInWaveform vector.
    //index = startingNewChannel ? (preTriggerTSteps + totalTSteps) : preTriggerTSteps;
    index =  bufferIndex-totalTSteps;
    while (index <= bufferIndex-totalTSteps + SAMPLES_PER_DATA_BLOCK * numBlocks - 1){
        triggered = false;
        int dIndex1 = (index - 1 < 0) ? bufferSizeUsed + index -1 : index - 1;
        int dIndex = (index < 0) ? bufferSizeUsed + index : index ;
            dIndex = dIndex % bufferSizeUsed;

        if (digitalEdgePolarity) {
                // Digital rising edge trigger
                if (digitalInputBuffer.at(dIndex1) == 0 &&
                        digitalInputBuffer.at(dIndex) == 1) {
                    triggered = true;
                }
        } else {
                // Digital falling edge trigger
                if (digitalInputBuffer.at(dIndex1) == 1 &&
                        digitalInputBuffer.at(dIndex) == 0) {
                    triggered = true;
                }
        }

        // If we found a trigger event, grab waveform snippet.
        if (triggered) {
            index2 = 0;
            for (i = index - preTriggerTSteps;
                 i < index + totalTSteps - preTriggerTSteps; ++i) {
                int dummyIndex = i;
                if(i < 0) dummyIndex = i + bufferSizeUsed;
                else    dummyIndex = i % bufferSizeUsed;
                digInWaveform[digInWaveformIndex][index2++] = digitalInputBuffer.at(dummyIndex);
            }
            if (++digInWaveformIndex == digInWaveform.size()) {
                digInWaveformIndex = 0;
            }
            if (++numDigInWaveforms > maxNumDigInWaveforms) {
                numDigInWaveforms = maxNumDigInWaveforms;
            }
            index += totalTSteps - preTriggerTSteps;
        } else {
            ++index;
        }
    }


    if (startingNewChannel) startingNewChannel = false;
    if (numDigInWaveforms == 0){
        meanDigInWaveform.fill(0.0);
    }else{
        for(i = 0 ; i < digInWaveform[1].size(); ++i){

            int N = numDigInWaveforms;
            double sum = 0.0;
            for(int j = digInWaveformIndex - numDigInWaveforms; j < digInWaveformIndex; ++j){
                sum += digInWaveform.at((j+30)%digInWaveform.size()).at(i);
            }
            meanDigInWaveform[i] = sum / N;

        }
    }

    // Taking the average for displaying in the LFP plot


    // Update plot.
    bufferIndex = (bufferIndex + SAMPLES_PER_DATA_BLOCK * numBlocks) % bufferSizeUsed;
    updateDigInPlot(rms);
}

// Plots digIn waveforms and writes RMS value to display.
void DigInPlot::updateDigInPlot(double rms)
{
    int i, j, xOffset, yOffset, index;
    double yAxisLength, tAxisLength;
    QRect adjustedFrame;
    double xScaleFactor, yScaleFactor;
    const double tScale = 250.0;  // time scale = 3.0 ms

    int colorIndex = 2;
    switch (maxNumDigInWaveforms) {
    case 10: colorIndex = 0; break;
    case 20: colorIndex = 1; break;
    case 30: colorIndex = 2; break;
    }

    drawAxisLines();

    QPainter painter(&pixmap);
    painter.initFrom(this);

    // Vector for waveform plot points
    QPointF *polyline = new QPointF[totalTSteps];

    yAxisLength = (frame.height() - 2) / 2.0;
    tAxisLength = frame.width() - 1;

    xOffset = frame.left() + 1;

    // Set clipping region for plotting.
    adjustedFrame = frame;
    adjustedFrame.adjust(0, 1, 0, 0);
    painter.setClipRect(adjustedFrame);

    xScaleFactor = tAxisLength * tStepMsec / tScale;
    yScaleFactor = -(2.0 * yAxisLength) / 2.0;
    yOffset = frame.center().y();

    if(showEachInPlot){
        index = maxNumDigInWaveforms - numDigInWaveforms;
        for (j = digInWaveformIndex - numDigInWaveforms; j < digInWaveformIndex; ++j) {
            // Build waveform
            for (i = 0; i < totalTSteps; ++i) {
                polyline[i] = QPointF(xScaleFactor * i + xOffset, yScaleFactor * digInWaveform.at((j + 30) % digInWaveform.size()).at(i) + yOffset);
            }

            // Draw waveform
            painter.setPen(scopeColors.at(colorIndex).at(index++));
            painter.drawPolyline(polyline, totalTSteps);
        }
    }

    // Display average value;
    if(showAverageInPlot){
        // Build waveform
        for (i = 0; i < totalTSteps; ++i) {
            polyline[i] = QPointF(xScaleFactor * i + xOffset, yScaleFactor * meanDigInWaveform.at(i) + yOffset);
        }

        // Draw
        painter.setPen(Qt::black);
        painter.drawPolyline(polyline, totalTSteps);
    }
    painter.setClipping(false);

    // Don't update the RMS value display every time, or it will change so fast that it
    // will be hard to read.  Only update once every few times we execute this function.
    if (rmsDisplayPeriod == 0) {
        rmsDisplayPeriod = 5;
        savedRms = rms;
    } else {
        --rmsDisplayPeriod;
    }

    // Write RMS value to display.
    const int textBoxWidth = 180;
    const int textBoxHeight = painter.fontMetrics().height();
    painter.setPen(Qt::darkGreen);
    painter.drawText(frame.left() + 6, frame.top() + 5,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignLeft | Qt::AlignTop,
                      "RMS:" + QString::number(savedRms, 'f', (savedRms < 10.0) ? 1 : 0) +
                      " " + QSTRING_MU_SYMBOL + "V");

    delete [] polyline;
    update();
}

// If user clicks inside display, set voltage threshold to that level.
void DigInPlot::mousePressEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton) {
        if (frame.contains(event->pos())) {
            int yMouse = event->pos().y();
            double newThreshold = yScale * (frame.center().y() - yMouse) / (frame.height() / 2);
            updateDigInPlot(0.0);
        }
    } else {
        QWidget::mousePressEvent(event);
    }
}

// If user spins mouse wheel, change voltage scale.
void DigInPlot::wheelEvent(QWheelEvent *event)
{
    if (event->delta() > 0) {
        lfpScopeDialog->contractYScale();
    } else {
        lfpScopeDialog->expandYScale();
    }
}

// Keypresses to change voltage scale.
void DigInPlot::keyPressEvent(QKeyEvent *event)
{
    switch (event->key()) {
    case Qt::Key_Minus:
    case Qt::Key_Underscore:
        lfpScopeDialog->contractYScale();
        break;
    case Qt::Key_Plus:
    case Qt::Key_Equal:
        lfpScopeDialog->expandYScale();
        break;
    default:
        QWidget::keyPressEvent(event);
    }
}

QSize DigInPlot::minimumSizeHint() const
{
    return QSize(LFPPLOT_X_SIZE, LFPPLOT_Y_SIZE);
}

QSize DigInPlot::sizeHint() const
{
    return QSize(LFPPLOT_X_SIZE, LFPPLOT_Y_SIZE);
}

void DigInPlot::paintEvent(QPaintEvent * /* event */)
{
    QStylePainter stylePainter(this);
    stylePainter.drawPixmap(0, 0, pixmap);
}

void DigInPlot::closeEvent(QCloseEvent *event)
{
    // Perform any clean-up here before application closes.
    event->accept();
}

// Set the number of digIns that are plotted, superimposed, on the
// display.
void DigInPlot::setMaxNumDigInWaveforms(int num)
{
    maxNumDigInWaveforms = num;
    numDigInWaveforms = 0;
}

// Clear digIn display.
void DigInPlot::clearScope()
{
    numDigInWaveforms = 0;
    drawAxisLines();
}

// Select voltage threshold trigger mode if voltageMode == true, otherwise
// select digital input trigger mode.

// Set voltage threshold trigger level.  We use integer threshold
// levels (in microvolts) since there is no point going to fractional
// microvolt accuracy.

void DigInPlot::showAverageDigInInPlot(bool show)
{
    showAverageInPlot = show;
    if (selectedChannel->signalType == AmplifierSignal) {
        selectedChannel->showAverageInPlot = show;
    }
}

void DigInPlot::showEachDigInInPlot(bool show)
{
    showEachInPlot = show;
    if (selectedChannel->signalType == AmplifierSignal) {
        selectedChannel->showEachInPlot = show;
    }
}

// Select digital input channel for digital input trigger.
void DigInPlot::setDigitalTriggerChannel(int channel)
{
    digitalTriggerChannel = channel;
    if (selectedChannel->signalType == AmplifierSignal) {
        selectedChannel->digitalTriggerChannel = channel;
    }
}

// Set digitial trigger edge polarity to rising or falling edge.
void DigInPlot::setDigitalEdgePolarity(bool risingEdge)
{
    digitalEdgePolarity = risingEdge;
    if (selectedChannel->signalType == AmplifierSignal) {
        selectedChannel->digitalEdgePolarity = risingEdge;
    }
}


// Change to a new signal channel.
void DigInPlot::setNewChannel(SignalChannel* newChannel)
{
    selectedChannel = newChannel;
    numDigInWaveforms = 0;
    startingNewChannel = true;
    rmsDisplayPeriod = 0;

    digitalTriggerChannel = selectedChannel->digitalTriggerChannel;
    digitalEdgePolarity = selectedChannel->digitalEdgePolarity;

    initializeDisplay();
}

void DigInPlot::resizeEvent(QResizeEvent*) {
    // Pixel map used for double buffering.
    pixmap = QPixmap(size());
    pixmap.fill();
    initializeDisplay();
}

void DigInPlot::initializeDisplay() {
    const int textBoxWidth = fontMetrics().width("+" + QString::number(yScale) + " " + QSTRING_MU_SYMBOL + "V");
    const int textBoxHeight = fontMetrics().height();
    frame = rect();
    frame.adjust(textBoxWidth + 5, textBoxHeight + 10, -8, -textBoxHeight - 10);

    // Initialize display.
    drawAxisText();
    drawAxisLines();
}
