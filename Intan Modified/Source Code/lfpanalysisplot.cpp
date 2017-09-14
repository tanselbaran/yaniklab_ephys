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
#include <sstream>

#include "globalconstants.h"
#include "signalprocessor.h"
#include "signalchannel.h"
#include "lfpanalysisdialog.h"
#include "lfpanalysisplot.h"
#include "lfpplot.h"

// The LfpPlot widget displays a triggered neural lfp plot in the
// Lfp Scope dialog.  Multiple lfps are plotted on top of one another
// so users may compare their shapes.  The RMS value of the waveform is
// displayed in the plot.  Users may select a new threshold value by clicking
// on the plot.  Keypresses are used to change the voltage scale of the plot.

LfpAnalysisPlot::LfpAnalysisPlot(LfpPlot *inLfpPlot, SignalProcessor *inSignalProcessor, SignalChannel *initialChannel,
                     LfpAnalysisDialog *inLfpAnalysisDialog, QWidget *parent) :
    QWidget(parent)
{
    lfpPlot = inLfpPlot;
    signalProcessor = inSignalProcessor;
    lfpAnalysisDialog = inLfpAnalysisDialog;

    selectedChannel = initialChannel;
    startingNewChannel = true;

    setBackgroundRole(QPalette::Window);
    setAutoFillBackground(true);
    setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);
    setFocusPolicy(Qt::StrongFocus);

    yScale = 500;
    tScaleInSec = 10*60;
    tStepSec = 1;
    analysisType = MIN_ANALYSIS;
    tLfpStepMsec = 1;
    setAnalysisWindow(0 , 50);
}

// Set voltage scale.
void LfpAnalysisPlot::setYScale(int newYScale)
{
    yScale = newYScale;
    initializeDisplay();
}

// Set waveform sample rate.
void LfpAnalysisPlot::setSampleRate(double newSampleRate)
{
    totalTSteps = lfpPlot->totalTSteps;
    tLfpStepMsec = lfpPlot->tStepMsec;

    double initialTimePoint = - (lfpPlot->preTriggerTSteps) * tLfpStepMsec;

    windowStartTimeIndex = qCeil((windowStartTimeInMs - initialTimePoint) / tLfpStepMsec);
    windowEndTimeIndex = qCeil((windowEndTimeInMs - initialTimePoint) /tLfpStepMsec) + 1 ;

    windowStartTimeIndex = (windowStartTimeIndex < 0) ? 0 : windowStartTimeIndex;
    windowEndTimeIndex = (windowEndTimeIndex > totalTSteps) ? totalTSteps : windowEndTimeIndex;

    qDebug() << "index: "<< QString::number( windowStartTimeIndex) << " , " << QString::number(windowEndTimeIndex);

    //Send Message and Stop the Run Reset the stuff
}

// Draw axis lines on display.
void LfpAnalysisPlot::drawAxisLines()
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
void LfpAnalysisPlot::drawAxisText()
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
    // otherwise remind the user than non-amplifier channels cannot be displayed in Lfp Scope.
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
                      "+" + QString::number(yScale) + " " + QSTRING_MU_SYMBOL + "V");
    painter.drawText(frame.left() - textBoxWidth - 2, frame.center().y() - textBoxHeight / 2,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignRight | Qt::AlignVCenter, "0");
    painter.drawText(frame.left() - textBoxWidth - 2, frame.bottom() - textBoxHeight + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignRight | Qt::AlignBottom,
                      "-" + QString::number(yScale) + " " + QSTRING_MU_SYMBOL + "V");

    // Label the time axis.
    painter.drawText(frame.left() - textBoxWidth / 2, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignHCenter | Qt::AlignTop, "0");
    painter.drawText(frame.left() + (1.0/5.0) * (frame.right() - frame.left()) + 1 - textBoxWidth / 2, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignHCenter | Qt::AlignTop, QString::number(tScaleInSec*1/300)+ " mins");
    painter.drawText(frame.left() + (2.0/5.0) * (frame.right() - frame.left()) + 1 - textBoxWidth / 2, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignHCenter | Qt::AlignTop, QString::number(tScaleInSec*2/300)+ " mins");
    painter.drawText(frame.left() + (3.0/5.0) * (frame.right() - frame.left()) + 1 - textBoxWidth / 2, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignHCenter | Qt::AlignTop, QString::number(tScaleInSec*3/300)+ " mins");
    painter.drawText(frame.left() + (4.0/5.0) * (frame.right() - frame.left()) + 1 - textBoxWidth / 2, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignHCenter | Qt::AlignTop, QString::number(tScaleInSec*4/300)+ " mins");
    painter.drawText(frame.right() - textBoxWidth + 1, frame.bottom() + 1,
                      textBoxWidth, textBoxHeight,
                      Qt::AlignRight | Qt::AlignTop, QString::number(tScaleInSec*5/300)+ " mins");

    update();
}

// This function loads waveform data for the selected channel from the signal processor object,
// looks for trigger events, captures 3-ms snippets of the waveform after trigger events,
// measures the rms level of the waveform, and updates the display.
void LfpAnalysisPlot::updateWaveform()
{
    meanLfpWaveform = lfpPlot->meanLfpWaveform;
    numLfpWaveforms = lfpPlot->numLfpWaveforms;
    totalTSteps = lfpPlot->totalTSteps;

    QVector<double> singleShotLfpData;
    singleShotLfpData.resize(30); // max number needed;
    singleShotLfpData.fill(0.0);
    double temp_av = 0.0;
    double temp_std = 0.0;

    double meanSingleShotLfpData = 0.0;
    double stdFromMeanResp = 0.0;


    if(analysisType == MIN_ANALYSIS ){
        if(numLfpWaveforms==0){

        }else{
            for (int i = 0; i < numLfpWaveforms; ++i) {
                //find min for each LFP Waveform recorded and register to singleShotLfpData
                int offsetVal = lfpPlot->lfpWaveformIndex - numLfpWaveforms;
                double temp_min = lfpPlot->lfpWaveform.at(i).at(windowStartTimeIndex);

                //search minimum as adjusted in the comboBox
                for(int j=windowStartTimeIndex ; j < windowEndTimeIndex; ++j){
                    temp_min = (temp_min > lfpPlot->lfpWaveform.at((i+offsetVal+30) % 30 ).at(j)) ? lfpPlot->lfpWaveform.at((i+offsetVal+30) % 30 ).at(j) : temp_min;
                }
                singleShotLfpData[i] = temp_min;
                temp_av +=singleShotLfpData[i];
            }
            temp_av = temp_av/numLfpWaveforms;

            meanSingleShotLfpData = lfpPlot->meanLfpWaveform.at(windowStartTimeIndex);
            int minPointIndex = 0;
            //search minimum as adjusted in the comboBox
            for(int j=windowStartTimeIndex; j < windowEndTimeIndex; ++j){
                minPointIndex = (meanSingleShotLfpData > lfpPlot->meanLfpWaveform.at(j)) ? j : minPointIndex;
                meanSingleShotLfpData = (meanSingleShotLfpData > lfpPlot->meanLfpWaveform.at(j)) ? lfpPlot->meanLfpWaveform.at(j) : meanSingleShotLfpData;
            }

            //Calculate the Standard Deviation for the ErrorBar

            //From the minimum of each LFP response;
            if (numLfpWaveforms >1){
                int offsetVal = lfpPlot->lfpWaveformIndex - numLfpWaveforms;
                //From the minimum of mean LFP response;
                for (int i = 0; i < numLfpWaveforms; ++i) {
                    stdFromMeanResp += (meanSingleShotLfpData - lfpPlot->lfpWaveform.at((i+offsetVal+30) % 30).at(minPointIndex))*(meanSingleShotLfpData - lfpPlot->lfpWaveform.at((i+offsetVal+30) % 30).at(minPointIndex));
                }
                stdFromMeanResp = sqrt(stdFromMeanResp/(numLfpWaveforms-1));
            }


        }
    }else if(analysisType==MAX_MIN_DIFFERENCE_ANALYSIS){
        if(numLfpWaveforms==0){

        }else{
            for (int i = 0; i < numLfpWaveforms; ++i) {
                //find min and max for each LFP Waveform recorded and register to singleShotLfpData
                int offsetVal = lfpPlot->lfpWaveformIndex - numLfpWaveforms;
                double temp_min = lfpPlot->lfpWaveform.at(i).at(windowStartTimeIndex);
                double temp_max = lfpPlot->lfpWaveform.at(i).at(windowStartTimeIndex);
                //search minimum as adjusted in the comboBox
                for(int j=windowStartTimeIndex ; j < windowEndTimeIndex; ++j){
                    temp_min = (temp_min > lfpPlot->lfpWaveform.at((i+offsetVal+30) % 30 ).at(j)) ? lfpPlot->lfpWaveform.at((i+offsetVal+30) % 30 ).at(j) : temp_min;
                    temp_max = (temp_max > lfpPlot->lfpWaveform.at((i+offsetVal+30) % 30 ).at(j)) ?  temp_max : lfpPlot->lfpWaveform.at((i+offsetVal+30) % 30 ).at(j);
                }
                singleShotLfpData[i] = temp_max - temp_min;
                temp_av +=singleShotLfpData[i];
            }
            temp_av = temp_av/numLfpWaveforms;

            int minSingleShotLfpData = lfpPlot->meanLfpWaveform.at(windowStartTimeIndex);
            int maxSingleShotLfpData = lfpPlot->meanLfpWaveform.at(windowStartTimeIndex);
            int minPointIndex = 0;
            int maxPointIndex = 0;

            //search minimum as adjusted in the comboBox
            for(int j=windowStartTimeIndex; j < windowEndTimeIndex; ++j){
                minPointIndex = (minSingleShotLfpData > lfpPlot->meanLfpWaveform.at(j)) ? j : minPointIndex;
                maxPointIndex = (maxSingleShotLfpData > lfpPlot->meanLfpWaveform.at(j)) ? maxPointIndex : j ;
                minSingleShotLfpData = (minSingleShotLfpData > lfpPlot->meanLfpWaveform.at(j)) ? lfpPlot->meanLfpWaveform.at(j) : minSingleShotLfpData;
                maxSingleShotLfpData = (maxSingleShotLfpData > lfpPlot->meanLfpWaveform.at(j)) ?  maxSingleShotLfpData: lfpPlot->meanLfpWaveform.at(j) ;
            }
            meanSingleShotLfpData = maxSingleShotLfpData - minSingleShotLfpData;
            //Calculate the Standard Deviation for the ErrorBar

            //From the minimum of each LFP response;
            if (numLfpWaveforms >1){
                int offsetVal = lfpPlot->lfpWaveformIndex - numLfpWaveforms;
                //From the minimum of mean LFP response;
                for (int i = 0; i < numLfpWaveforms; ++i) {
                    int diff_value = lfpPlot->lfpWaveform.at((i+offsetVal+30) % 30).at(maxPointIndex)-lfpPlot->lfpWaveform.at((i+offsetVal+30) % 30).at(minPointIndex);
                    stdFromMeanResp += (meanSingleShotLfpData - diff_value)*(meanSingleShotLfpData - diff_value);
                }
                stdFromMeanResp = sqrt(stdFromMeanResp/(numLfpWaveforms-1));
            }

        }
    }
    lfpAnalysisData.append(singleShotLfpData);

    /*mLfpAnalysisData.append(temp_av);
    stdLfpAnalysisData.append(temp_std);*/


    meanLfpAnalysisData.append(meanSingleShotLfpData);
    stdOfmeanLfpAnalysisData.append(stdFromMeanResp);

    updateLfpAnalysisPlot();
}



// Plots lfp waveforms and writes RMS value to display.
void LfpAnalysisPlot::updateLfpAnalysisPlot()
{
    int i, j, xOffset, yOffset, index;
    double yAxisLength, tAxisLength;
    QRect adjustedFrame;
    double xScaleFactor, yScaleFactor;


    drawAxisLines();

    QPainter painter(&pixmap);
    painter.initFrom(this);

    // Vector for waveform plot points


    yAxisLength = (frame.height() - 2) / 2.0;
    tAxisLength = frame.width() - 1;

    xOffset = frame.left() + 1;

    // Set clipping region for plotting.
    adjustedFrame = frame;
    adjustedFrame.adjust(0, 1, 0, 0);
    painter.setClipRect(adjustedFrame);

    xScaleFactor = tAxisLength * tStepSec / tScaleInSec;
    yScaleFactor = -yAxisLength / yScale;
    yOffset = frame.center().y();


    // Error Bar display calculated from Overall average LFP and std from same index
    QPointF *polyline = new QPointF[tScaleInSec];
    for (i = 0; i < meanLfpAnalysisData.size(); ++i) {
        polyline[i] = QPointF(xScaleFactor * i + xOffset, yScaleFactor * meanLfpAnalysisData.at(i) + yOffset);

        if(errorbarDisplayState){
        painter.setPen(Qt::red);
        painter.drawLine(QPointF(xScaleFactor * i + xOffset,yScaleFactor * (meanLfpAnalysisData.at(i) - stdOfmeanLfpAnalysisData.at(i)) + yOffset),
                         QPointF(xScaleFactor * i + xOffset,yScaleFactor * (meanLfpAnalysisData.at(i) + stdOfmeanLfpAnalysisData.at(i)) + yOffset));
        }
    }

    painter.setPen(Qt::blue);
    painter.drawPolyline(polyline, meanLfpAnalysisData.size());
    delete [] polyline;

    //Error Bar display calculated from Each LFP minumum
    /*QPointF *polyline2 = new QPointF[tScaleInSec];
    for (i = 0; i < mLfpAnalysisData.size(); ++i) {
        polyline2[i] = QPointF(xScaleFactor * i + xOffset, yScaleFactor * mLfpAnalysisData.at(i) + yOffset);

        if(errorbarDisplayState){
        painter.setPen(Qt::cyan);
        painter.drawLine(QPointF(xScaleFactor * i + xOffset,yScaleFactor * (mLfpAnalysisData.at(i) - stdLfpAnalysisData.at(i)) + yOffset),
                         QPointF(xScaleFactor * i + xOffset,yScaleFactor * (mLfpAnalysisData.at(i) + stdLfpAnalysisData.at(i)) + yOffset));
        }
    }

    painter.setPen(Qt::blue);
    painter.drawPolyline(polyline2, mLfpAnalysisData.size());
    delete [] polyline2; */

    update();
}

// If user clicks inside display, set voltage threshold to that level.
void LfpAnalysisPlot::mousePressEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton) {
        if (frame.contains(event->pos())) {
        }
    } else {
        QWidget::mousePressEvent(event);
    }
}

// If user spins mouse wheel, change voltage scale.
void LfpAnalysisPlot::wheelEvent(QWheelEvent *event)
{
    if (event->delta() > 0) {
        lfpAnalysisDialog->contractYScale();
    } else {
        lfpAnalysisDialog->expandYScale();
    }
}

// Keypresses to change voltage scale.
void LfpAnalysisPlot::keyPressEvent(QKeyEvent *event)
{
    switch (event->key()) {
    case Qt::Key_Minus:
    case Qt::Key_Underscore:
        lfpAnalysisDialog->contractYScale();
        break;
    case Qt::Key_Plus:
    case Qt::Key_Equal:
        lfpAnalysisDialog->expandYScale();
        break;
    default:
        QWidget::keyPressEvent(event);
    }
}

QSize LfpAnalysisPlot::minimumSizeHint() const
{
    return QSize(LFPPLOT_X_SIZE, LFPPLOT_Y_SIZE);
}

QSize LfpAnalysisPlot::sizeHint() const
{
    return QSize(LFPANALYSISPLOT_X_SIZE, LFPANALYSISPLOT_Y_SIZE);
}

void LfpAnalysisPlot::paintEvent(QPaintEvent * /* event */)
{
    QStylePainter stylePainter(this);
    stylePainter.drawPixmap(0, 0, pixmap);
}

void LfpAnalysisPlot::closeEvent(QCloseEvent *event)
{
    // Perform any clean-up here before application closes.
    event->accept();
}

// Set the number of lfps that are plotted, superimposed, on the
// display.
void LfpAnalysisPlot::setMaxNumLfpWaveforms()
{
    maxNumLfpWaveforms = lfpPlot->maxNumLfpWaveforms;
    numLfpWaveforms = lfpPlot->numLfpWaveforms;
    //Add code for clearing the Buffer used for analysis
}

// Clear lfp display.
void LfpAnalysisPlot::clearScope()
{
    //Fill here with something else
    numLfpWaveforms = 0;
    drawAxisLines();
}

// Change to a new signal channel.
void LfpAnalysisPlot::setNewChannel(SignalChannel* newChannel)
{
    selectedChannel = newChannel;
    startingNewChannel = true;
    initializeDisplay();
}

void LfpAnalysisPlot::resizeEvent(QResizeEvent*) {
    // Pixel map used for double buffering.
    pixmap = QPixmap(size());
    pixmap.fill();
    initializeDisplay();
}

void LfpAnalysisPlot::initializeDisplay() {
    const int textBoxWidth = fontMetrics().width("+" + QString::number(yScale) + " " + QSTRING_MU_SYMBOL + "V");
    const int textBoxHeight = fontMetrics().height();
    frame = rect();
    frame.adjust(textBoxWidth + 5, textBoxHeight + 10, -8, -textBoxHeight - 10);

    // Initialize display.
    drawAxisText();
    drawAxisLines();

    if(meanLfpAnalysisData.size() != 0 ){updateLfpAnalysisPlot();} //if the analysis is running redraw the lines
}

void LfpAnalysisPlot::setTScale(int t){

    tScaleInSec = t;
    initializeDisplay();
}

void LfpAnalysisPlot::setTStepValue(int t){

    tStepSec = t;
    initializeDisplay();
}

void LfpAnalysisPlot::setErrorbarDisplayState(bool state){
    errorbarDisplayState = state;
    initializeDisplay();
}


void LfpAnalysisPlot::applyStartProcess(){
    meanLfpAnalysisData.resize(0);
    stdOfmeanLfpAnalysisData.resize(0);
    lfpAnalysisData.resize(0);
    //stdLfpAnalysisData.resize(0);
    //mLfpAnalysisData.resize(0);

}

void LfpAnalysisPlot::applyStopProcess(){
    meanLfpAnalysisData.resize(0);
    stdOfmeanLfpAnalysisData.resize(0);
    lfpAnalysisData.resize(0);
    //stdLfpAnalysisData.resize(0);
    //mLfpAnalysisData.resize(0);
}

void LfpAnalysisPlot::setAnalysisWindow(double startInMs, double endInMs){
    if(startInMs == 0 && endInMs == 0)
    {
        windowStartTimeInMs = - (lfpPlot->preTriggerTSteps) * tLfpStepMsec ;
        windowEndTimeInMs = (lfpPlot->totalTSteps - lfpPlot->preTriggerTSteps)*tLfpStepMsec;
    }else{
        windowStartTimeInMs = startInMs;
        windowEndTimeInMs = endInMs;
    }
        setSampleRate(1000/tLfpStepMsec);
}

void LfpAnalysisPlot::changeAnalysisType(int newType){
    analysisType = newType;
}
