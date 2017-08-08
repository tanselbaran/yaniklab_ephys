#include <QtGui>
#if QT_VERSION >= QT_VERSION_CHECK(5,0,0)
#include <QtWidgets>
#endif
#include <vector>
#include <queue>
#include <iostream>
#include <QtAlgorithms>

#include "probe.h"
#include "probedisplaywidget.h"
#include "globalconstants.h"
#include "signalchannel.h"
#include "signalsources.h"

Probe::Probe( QString name, int type, int shankNumber, QVector<int> map,  SignalChannel *inSignalChannel ,SignalSources *inSignalSources ,QWidget *parent) :
    QWidget(parent)
{
    probeName = name;
    probeType = type;
    numberOfShanks = shankNumber;
    currentChannel = inSignalChannel;
    signalSources = inSignalSources;

    probeMapArray = map;
    probeMap.resize(numberOfShanks);
    shankFrames.resize(numberOfShanks);

    if(probeType == LINEAR_PROBE_TYPE){
        for(int i = 0 ; i < numberOfShanks ; ++i){
            probeMap[i].resize( map.size()/ numberOfShanks );
            for (int j = 0 ; j < probeMap[i].size() ; ++j){
                probeMap[i][j].resize(1);
            }
        }
    }else if(probeType == TETROTE_PROBE_TYPE){
        for(int i = 0 ; i < numberOfShanks ; ++i){
            probeMap[i].resize( map.size()/ (4*numberOfShanks) );
            for (int j = 0 ; j < probeMap[i].size() ; ++j){
                probeMap[i][j].resize(4);
            }
        }
    }

    convert2Map(map);

    setBackgroundRole(QPalette::Window);
    setAutoFillBackground(true);
    setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);
    //setFocusPolicy(Qt::StrongFocus);
    //QWidget::resize(PROBE_X_SIZE, PROBE_Y_SIZE);

    draw();
}

QString Probe::getProbeName(){
    return probeName;
}

int     Probe::getProbeType(){
    return probeType;
}

void    Probe::setNewChannel(  SignalChannel *newChannel ){
    currentChannel = newChannel;
    draw();
}

void Probe::setUpShanks(){

    frame = rect();

    int ySize_shank = height() - 10;
    int xSize_shank = (width()-10) / numberOfShanks;

    int yOffset_shank = 5;
    int xOffset_shank = xSize_shank + 2;

    //Generate frame positions for Shanks
    subShankFrames.resize(numberOfShanks);
     for( int i = 0 ; i < numberOfShanks ; ++i){
         int x_shank = 5 + xOffset_shank * i;
         int y_shank = yOffset_shank;
         QRect shankRect = QRect(x_shank, y_shank, xSize_shank, ySize_shank);
         shankFrames[i] = shankRect;

         //do similar calculations for each shank to divide it sub-rects
         int ySize = ySize_shank / (probeMap[i].size() + 1) ;
         int xOffset = shankRect.left();
         int yOffset = shankRect.top();
         subShankFrames[i].resize(probeMap[i].size()+1); // +1 for the bottom display Triangle
         for (int j = 0 ; j < probeMap[i].size() ; ++j){
             subShankFrames[i][probeMap[i].size() -1  - j ] = QRect(xOffset, yOffset + j*ySize , xSize_shank, ySize);
         }
         subShankFrames[i][probeMap[i].size()] = QRect(xOffset, yOffset + probeMap[i].size()*ySize , xSize_shank, ySize);
     }

}

void Probe::draw(){
    setUpShanks();

    QPainter painter(&pixmap);
    painter.initFrom(this);

    painter.setPen(Qt::blue);
    for( int i = 0 ; i < numberOfShanks ; ++i){
        painter.drawRect(shankFrames.at(i));
        painter.setPen(Qt::red);

        QBrush rectBrush = QBrush(Qt::blue);
        QBrush notSelectedChannelBrush = QBrush(Qt::black);
        QBrush selectedChannelBrush = QBrush(Qt::red);
        QBrush circBrush = notSelectedChannelBrush;

        int probDispSize = subShankFrames[i][0].width() / 3 ;
        for (int j = 0 ; j < subShankFrames[i].size()-1 ; ++j){
            painter.setPen(Qt::black);
            painter.drawRect(subShankFrames[i][j]);

            QRect f = subShankFrames[i][j];
            //initialize the pen and brush used for electrode circle and Text Info
            QPen linPen = QPen(Qt::black);
            linPen.setWidth(2);

            //Fill the center rectangle for overall probe display
            painter.fillRect(QRect( f.center().x() - (probDispSize)/2 , f.top() , probDispSize , f.height()) , rectBrush);

            // The painting takes part from top to bottom of the probe however indexes are recorded from bottom to top.
            //reverting the scan order to compensate this
            const int correctedIndex = j;//probeMap[i].size() - j  - 1;

            if(probeType == LINEAR_PROBE_TYPE){
                //setting Amplfier channel name for comparison with the native channel name
                /*QString channelName =  QString::number(probeMap[i][correctedIndex][0]);
                if(channelName.length() == 1){channelName = "A-00" + channelName;}
                else if (channelName.length() == 2){channelName = "A-0" + channelName;}
                else if (channelName.length() == 3){channelName = "A-" + channelName;}*/

                //If selected channel change the color
                /*if(QString::compare(channelName, currentChannel->nativeChannelName, Qt::CaseInsensitive) == 0){ circBrush = selectedChannelBrush;}
                else{circBrush = notSelectedChannelBrush;} */

                if(probeMap[i][correctedIndex].at(0) == currentChannel->nativeChannelNumber){ circBrush = selectedChannelBrush;}
                else{circBrush = notSelectedChannelBrush;}

                //draw the circle in the center of the rect
                QPainterPath circlePath;
                int radius = (probDispSize > f.height()) ? f.height()/10 : probDispSize / 10;
                circlePath.addEllipse(QRect(f.center().x()-radius , f.center().y() - radius, 2*radius , 2*radius)); //(f.center());
                painter.fillPath(circlePath, circBrush);

                //display the Text depending the allignment side
                const int textBoxWidth = painter.fontMetrics().width("A" + QString::number(probeMap[i][correctedIndex][0]));
                const int textBoxHeight = painter.fontMetrics().height();


                if ( j % 2 == 0) // allign the probe number to the left
                {

                    painter.drawText(f.left() + 2, f.center().y()- textBoxHeight/2,
                                      textBoxWidth, textBoxHeight,
                                      Qt::AlignRight | Qt::AlignCenter,"A" + QString::number(probeMap[i][correctedIndex][0]));

                    //draw the connection line to the cirle for showing which probe is (
                    painter.drawLine(f.left() + textBoxWidth + 2, f.center().y() -1 , f.center().x() , f.center().y());
                }else{
                    painter.drawText(f.right() - textBoxWidth - 1, f.center().y() - textBoxHeight/2,
                                      textBoxWidth, textBoxHeight,
                                      Qt::AlignLeft| Qt::AlignCenter, "A" + QString::number(probeMap[i][correctedIndex][0]));

                    painter.drawLine(f.right() - textBoxWidth - 1, f.center().y() -1 , f.center().x() , f.center().y());
                }


            }else if( probeType == TETROTE_PROBE_TYPE){

                int radius = (probDispSize > f.height()) ? f.height()/10 : probDispSize / 10;
                QPainterPath notSelectedCirclePath;
                QPainterPath selectedCirclePath;
                //electrode at index 0
                QString channelName =  QString::number(probeMap[i][correctedIndex][0]);
                if(channelName.length() == 1){channelName = "A-00" + channelName;}
                else if (channelName.length() == 2){channelName = "A-0" + channelName;}
                if(probeMap[i][correctedIndex].at(0) == currentChannel->nativeChannelNumber){
                    selectedCirclePath.addEllipse(QRect(f.center().x()-radius , f.center().y() +f.height()/4 -  radius, 2*radius , 2*radius));
                }
                else{
                    notSelectedCirclePath.addEllipse(QRect(f.center().x()-radius , f.center().y() +f.height()/4 -  radius, 2*radius , 2*radius));
                }

                //electrode at index 1

                if(probeMap[i][correctedIndex].at(1) == currentChannel->nativeChannelNumber){
                   selectedCirclePath.addEllipse(QRect(f.center().x()-probDispSize/4-radius , f.center().y() - radius, 2*radius , 2*radius));
                }
                else{
                    notSelectedCirclePath.addEllipse(QRect(f.center().x()-probDispSize/4-radius , f.center().y() - radius, 2*radius , 2*radius));
                }

                //electrode at index 2

                if(probeMap[i][correctedIndex].at(2) == currentChannel->nativeChannelNumber){
                    selectedCirclePath.addEllipse(QRect(f.center().x()-radius , f.center().y() -f.height()/4 -  radius, 2*radius , 2*radius));
                }
                else{
                    notSelectedCirclePath.addEllipse(QRect(f.center().x()-radius , f.center().y() -f.height()/4 -  radius, 2*radius , 2*radius));
                }

                //electrode at index 3

                if(probeMap[i][correctedIndex].at(3) == currentChannel->nativeChannelNumber){
                   selectedCirclePath.addEllipse(QRect(f.center().x()+probDispSize/4-radius , f.center().y() - radius, 2*radius , 2*radius));
                }
                else{
                    notSelectedCirclePath.addEllipse(QRect(f.center().x()+probDispSize/4-radius , f.center().y() - radius, 2*radius , 2*radius));
                }

                painter.fillPath(notSelectedCirclePath, notSelectedChannelBrush);
                painter.fillPath(selectedCirclePath, selectedChannelBrush);


                //display the Texts and the line

                //Index 0
                int textBoxWidth = painter.fontMetrics().width("A" + QString::number(probeMap[i][correctedIndex][0]));
                int textBoxHeight = painter.fontMetrics().height();

                painter.drawText(f.left() + 2 , f.center().y() + f.height()/4 - textBoxHeight/2,
                                  textBoxWidth, textBoxHeight,
                                  Qt::AlignRight | Qt::AlignCenter,"A" + QString::number(probeMap[i][correctedIndex][0]));

                 painter.drawLine(f.left() +2 + textBoxWidth, f.center().y() + f.height()/4  , f.center().x() , f.center().y() + f.height()/4 );

                //Index 1
                 textBoxWidth = painter.fontMetrics().width("A" + QString::number(probeMap[i][correctedIndex][1]));
                 textBoxHeight = painter.fontMetrics().height();

                painter.drawText(f.left() + 2 , f.center().y() - textBoxHeight/2,
                                  textBoxWidth, textBoxHeight,
                                  Qt::AlignRight | Qt::AlignCenter,"A" + QString::number(probeMap[i][correctedIndex][1]));


                painter.drawLine(f.left() +2 + textBoxWidth, f.center().y() , f.center().x() - probDispSize/4 , f.center().y() );

                //Index 2
                 textBoxWidth = painter.fontMetrics().width("A" + QString::number(probeMap[i][correctedIndex][2]));
                 textBoxHeight = painter.fontMetrics().height();

                painter.drawText(f.right() -textBoxWidth - 2 , f.center().y() - f.height()/4 - textBoxHeight/2,
                                  textBoxWidth, textBoxHeight,
                                  Qt::AlignRight | Qt::AlignCenter,"A" + QString::number(probeMap[i][correctedIndex][2]));


                painter.drawLine(f.right() -2 - textBoxWidth, f.center().y() - f.height()/4  , f.center().x() , f.center().y() - f.height()/4 );

                //Index 3
                textBoxWidth = painter.fontMetrics().width("A" + QString::number(probeMap[i][correctedIndex][3]));
                textBoxHeight = painter.fontMetrics().height();

                painter.drawText(f.right() -textBoxWidth - 2 , f.center().y() - textBoxHeight/2,
                                  textBoxWidth, textBoxHeight,
                                  Qt::AlignRight | Qt::AlignCenter,"A" + QString::number(probeMap[i][correctedIndex][3]));


                painter.drawLine(f.right() -2 - textBoxWidth, f.center().y() , f.center().x() + probDispSize/4, f.center().y() );


            }
        }

        //draw the triangle tip of each shanks.
        QRect f = subShankFrames[i][subShankFrames.at(i).size()-1];
        QPolygon trianglePoly;
        trianglePoly << QPoint( f.center().x() - (probDispSize)/2 , f.top()) ;
        trianglePoly << QPoint( f.center().x() + (probDispSize)/2 , f.top()) ;
        trianglePoly << QPoint (f.center().x(), f.bottom());
        QPainterPath trianglePath;
        trianglePath.addPolygon(trianglePoly);
        painter.fillPath(trianglePath, rectBrush );

        painter.setPen(Qt::blue);

    }
    //qDebug() << currentChannel->nativeChannelName;
    update();
}
void Probe::convert2Map( QVector<int> map){

    if(probeType == LINEAR_PROBE_TYPE){

        int div_value = map.size() / numberOfShanks ;

        for(int i = 0 ; i < map.size(); ++i ){
            probeMap[i / div_value ][i % div_value ][0] = map.at(i);
        }

    }else if(probeType == TETROTE_PROBE_TYPE){

        int div_value = map.size() / numberOfShanks ;
        for(int i = 0 ; i < map.size(); ++i ){
            probeMap[i / div_value][(i % div_value) / 4][i % 4] = map.at(i);
        }

    }else{

    }
}


void Probe::paintEvent(QPaintEvent * /* event */)
{
    QStylePainter stylePainter(this);
    stylePainter.drawPixmap(0, 0, pixmap);
}

void Probe::mousePressEvent(QMouseEvent *event){
    if (event->button() == Qt::LeftButton) {
        currentChannel = findClosestChannel2Click(event->pos());
        emit channelChanged(currentChannel);
        draw();
    } else {
        QWidget::mousePressEvent(event);
    }
}


void Probe::resizeEvent(QResizeEvent*) {
    // Pixel map used for double buffering.
    pixmap = QPixmap(size());
    pixmap.fill();
    draw();
}

QSize Probe::minimumSizeHint() const
{
    return QSize(PROBE_X_SIZE, PROBE_Y_SIZE);
}

QSize Probe::sizeHint() const
{
    return QSize(PROBE_X_SIZE, PROBE_Y_SIZE);
}

SignalChannel* Probe::findClosestChannel2Click(QPoint p){

    int distance2 = 0;
    int smallestDistance2 = 0;
    int closestShankIndex = -1;
    int closestFrameIndex = -1;
    int closestTetroteIndex = -1;
    SignalChannel *result = currentChannel;
    for (int i = 0; i < subShankFrames.size(); ++i) {
        for(int j = 0 ; j < subShankFrames[i].size() -1 ; ++j ) {

            QRect f = subShankFrames[i][j];
            distance2 = (p.x() - f.center().x())*(p.x() - f.center().x()) +
                            (p.y() - f.center().y())*(p.y() - f.center().y());

            if ((distance2 < smallestDistance2) || ((i==0) && (j == 0))) {
                smallestDistance2 = distance2;
                closestShankIndex = i;
                closestFrameIndex = j;
                //for tetrote there is an additional comparison for which electrode to detect inside the tetrote
                if(probeType == TETROTE_PROBE_TYPE){
                    int minVal;
                    int dist2d = (p.x() - f.center().x())*(p.x() - f.center().x()) +
                                    (p.y() - f.center().y() - f.height()/4)*(p.y() - f.center().y() - f.height()/4);
                    minVal = dist2d; closestTetroteIndex = 0;

                    //index 1
                    dist2d = (p.x() - f.center().x() + f.width()/4)*(p.x() - f.center().x()+f.width()/4) +
                                                        (p.y() - f.center().y())*(p.y() - f.center().y());
                    minVal = (dist2d > minVal) ? minVal : dist2d;
                    closestTetroteIndex = (dist2d > minVal) ? closestTetroteIndex : 1 ;

                    //index 2
                    dist2d = (p.x() - f.center().x())*(p.x() - f.center().x()) +
                                                        (p.y() - f.center().y() + f.height()/4)*(p.y() - f.center().y() + f.height()/4);
                    minVal = (dist2d > minVal) ? minVal : dist2d;
                    closestTetroteIndex = (dist2d > minVal) ? closestTetroteIndex : 2 ;

                    //index 3
                    dist2d = (p.x() - f.center().x() - f.width()/4)*(p.x() - f.center().x() - f.width()/4) +
                                                        (p.y() - f.center().y())*(p.y() - f.center().y());
                    minVal = (dist2d > minVal) ? minVal : dist2d;
                    closestTetroteIndex = (dist2d > minVal) ? closestTetroteIndex : 3 ;
                }
            }

        }

    }

    //Select the channel closest to mouse click
    if(probeType == LINEAR_PROBE_TYPE){

        QString channelName =  QString::number(probeMap[closestShankIndex][closestFrameIndex][0]);
        if(channelName.length() == 1){channelName = "A-00" + channelName;}
        else if (channelName.length() == 2){channelName = "A-0" + channelName;}
        else if (channelName.length() == 3){channelName = "A-" + channelName;}

        result = signalSources->findChannelFromName(channelName) ;
        qDebug() << result->nativeChannelName;

    }else if (probeType == TETROTE_PROBE_TYPE){
        QString channelName =  QString::number(probeMap[closestShankIndex][closestFrameIndex][closestTetroteIndex]);
        if(channelName.length() == 1){channelName = "A-00" + channelName;}
        else if (channelName.length() == 2){channelName = "A-0" + channelName;}
        else if (channelName.length() == 3){channelName = "A-" + channelName;}

        result = signalSources->findChannelFromName(channelName) ;
        qDebug() << result->nativeChannelName;
    }else{
        result = currentChannel;
    }

    return result;
}

QVector<int> Probe::getMapArray(){
    return probeMapArray;
}
