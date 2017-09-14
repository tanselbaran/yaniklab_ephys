
#include <QtGui>
#if QT_VERSION >= QT_VERSION_CHECK(5,0,0)
#include <QtWidgets>
#endif
#include <vector>
#include <queue>
#include <iostream>
#include <QtAlgorithms>

#include "shankdisplay.h"
#include "mainwindow.h"

ShankDisplay::ShankDisplay( MainWindow *inMainWindow, QWidget *parent) :
    QWidget(parent)
{
    mainWindow = inMainWindow;
    unselectedElectrodeBrush = QBrush(Qt::black);
    selectedElectrodeBrush= QBrush(Qt::red);
    electrodeBackgroundBrush= QBrush(Qt::blue);
    unselectedWritingPen = QPen(Qt::black);
    unselectedWritingPen.setWidth(2);
    selectedWritingPen = QPen(Qt::red);
    selectedWritingPen.setWidth(2);

    connect(mainWindow, SIGNAL(newMapElementRecieved()), this, SLOT(updatePlot()));
    //set the frames;

    setBackgroundRole(QPalette::Window);
    setAutoFillBackground(true);
    setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);

    draw();
}

void ShankDisplay::draw(){

    getStartIndexOfDisplay();
    setUpFrames();

    QPainter painter(&pixmap);
    painter.initFrom(this);

    painter.fillRect(frame, QBrush(Qt::white));
    int selectedIndex = mainWindow->currentIndexInMap;

    int probeDisplaySize = frameList[0].width() / 3;

    for(int i = 0 ; i < frameList.size()-1 ;++i){


        QRect f = frameList[i];
        int radius = (probeDisplaySize > f.height()) ? f.height()/6 : probeDisplaySize / 6;

        //paint background
        painter.fillRect(QRect(f.center().x() - probeDisplaySize/2 , f.top(), probeDisplaySize, f.height()),electrodeBackgroundBrush);


        if(mainWindow->probeType == LINEAR_PROBE_TYPE){

            int displayIndex = startIndexOfDisplay + i; //corresponds to index at map for Linear probes
            qDebug() << QString::number(displayIndex);
            bool isSelected = displayIndex == mainWindow->currentIndexInMap;

            QPainterPath circlePath;
            circlePath.addEllipse(QRect(f.center().x()-radius , f.center().y() - radius, 2*radius , 2*radius));

            if(isSelected){
                painter.fillPath(circlePath, selectedElectrodeBrush);
                painter.setPen(selectedWritingPen);
            }
            else{
                painter.fillPath(circlePath, unselectedElectrodeBrush);
                painter.setPen(unselectedWritingPen);
            }

            //Text display
            int currentMapValue = mainWindow->probeMap[displayIndex];
            int textBoxWidth;
            QString displayText ;
            if(currentMapValue == -1){
                textBoxWidth = painter.fontMetrics().width("XX");
                displayText = "XX";
            }else{
                textBoxWidth = painter.fontMetrics().width(QString::number(currentMapValue));
                displayText = QString::number(currentMapValue);
            }

            int textBoxHeight = painter.fontMetrics().height();

            if ( i % 2 == 0) // allign the probe number to the left
            {

                painter.drawText(f.left() + 2, f.center().y()- textBoxHeight/2,
                                  textBoxWidth, textBoxHeight,
                                  Qt::AlignCenter, displayText);

                //draw the connection line to the cirle for showing which probe is (
                painter.drawLine(f.left() + textBoxWidth + 10, f.center().y() , f.center().x() , f.center().y());

            }else{
                painter.drawText(f.right() - textBoxWidth - 1, f.center().y() - textBoxHeight/2,
                                  textBoxWidth, textBoxHeight,
                                  Qt::AlignCenter, displayText);

                painter.drawLine(f.right() - textBoxWidth - 10, f.center().y(), f.center().x() , f.center().y());
            }

        }else{
            int displayIndex = startIndexOfDisplay + i*4;

            QPainterPath notSelectedCirclePath;
            QPainterPath selectedCirclePath;
            //electrode at index 0
            if(displayIndex == mainWindow->currentIndexInMap){
                selectedCirclePath.addEllipse(QRect(f.center().x()-radius , f.center().y() +f.height()/4 -  radius, 2*radius , 2*radius));
            }
            else{
                notSelectedCirclePath.addEllipse(QRect(f.center().x()-radius , f.center().y() +f.height()/4 -  radius, 2*radius , 2*radius));
            }

            //electrode at index 1
            if(displayIndex+1== mainWindow->currentIndexInMap){
               selectedCirclePath.addEllipse(QRect(f.center().x()-probeDisplaySize/4-radius , f.center().y() - radius, 2*radius , 2*radius));
            }
            else{
                notSelectedCirclePath.addEllipse(QRect(f.center().x()-probeDisplaySize/4-radius , f.center().y() - radius, 2*radius , 2*radius));
            }

            //electrode at index 2
            if(displayIndex+2== mainWindow->currentIndexInMap){
                selectedCirclePath.addEllipse(QRect(f.center().x()-radius , f.center().y() -f.height()/4 -  radius, 2*radius , 2*radius));
            }
            else{
                notSelectedCirclePath.addEllipse(QRect(f.center().x()-radius , f.center().y() -f.height()/4 -  radius, 2*radius , 2*radius));
            }

            //electrode at index 3
            if(displayIndex+3 == mainWindow->currentIndexInMap){
               selectedCirclePath.addEllipse(QRect(f.center().x()+probeDisplaySize/4-radius , f.center().y() - radius, 2*radius , 2*radius));
            }
            else{
                notSelectedCirclePath.addEllipse(QRect(f.center().x()+probeDisplaySize/4-radius , f.center().y() - radius, 2*radius , 2*radius));
            }

            painter.fillPath(notSelectedCirclePath, unselectedElectrodeBrush);
            painter.fillPath(selectedCirclePath, selectedElectrodeBrush);

            //Text display at index 0
            int currentMapValue = mainWindow->probeMap[displayIndex];
            int textBoxWidth;

            QString displayText ;
            if(currentMapValue == -1){
                textBoxWidth = painter.fontMetrics().width("XX");
                displayText = "XX";
            }else{
                textBoxWidth = painter.fontMetrics().width(QString::number(currentMapValue));
                displayText = QString::number(currentMapValue);
            }

            int textBoxHeight = painter.fontMetrics().height();

            painter.drawText(f.left() + 2 , f.center().y() + f.height()/4 - textBoxHeight/2,
                              textBoxWidth, textBoxHeight,
                              Qt::AlignCenter, displayText);

            painter.drawLine(f.left() + 10 + textBoxWidth, f.center().y() + f.height()/4  , f.center().x() , f.center().y() + f.height()/4 );


            //Text display at index 1
            currentMapValue = mainWindow->probeMap[displayIndex+1];
            textBoxWidth;

            displayText ;
            if(currentMapValue == -1){
                textBoxWidth = painter.fontMetrics().width("XX");
                displayText = "XX";
            }else{
                textBoxWidth = painter.fontMetrics().width(QString::number(currentMapValue));
                displayText = QString::number(currentMapValue);
            }

            textBoxHeight = painter.fontMetrics().height();

            painter.drawText(f.left() + 2 , f.center().y() - textBoxHeight/2,
                              textBoxWidth, textBoxHeight,
                              Qt::AlignCenter, displayText);


            painter.drawLine(f.left() +2 + textBoxWidth, f.center().y() , f.center().x() - probeDisplaySize/4 , f.center().y() );

            //Text display at index 2
            currentMapValue = mainWindow->probeMap[displayIndex+2];
            textBoxWidth;

            displayText ;
            if(currentMapValue == -1){
                textBoxWidth = painter.fontMetrics().width("XX");
                displayText = "XX";
            }else{
                textBoxWidth = painter.fontMetrics().width(QString::number(currentMapValue));
                displayText = QString::number(currentMapValue);
            }

            textBoxHeight = painter.fontMetrics().height();

            painter.drawText(f.right() -textBoxWidth - 2 , f.center().y() - f.height()/4 - textBoxHeight/2,
                              textBoxWidth, textBoxHeight,
                              Qt::AlignCenter, displayText);


            painter.drawLine(f.right() -2 - textBoxWidth, f.center().y() - f.height()/4  , f.center().x() , f.center().y() - f.height()/4 );


            //Text display at index 3
            currentMapValue = mainWindow->probeMap[displayIndex+3];
            textBoxWidth;

            displayText ;
            if(currentMapValue == -1){
                textBoxWidth = painter.fontMetrics().width("XX");
                displayText = "XX";
            }else{
                textBoxWidth = painter.fontMetrics().width(QString::number(currentMapValue));
                displayText = QString::number(currentMapValue);
            }

            textBoxHeight = painter.fontMetrics().height();

            painter.drawText(f.right() -textBoxWidth - 2 , f.center().y() - textBoxHeight/2,
                              textBoxWidth, textBoxHeight,
                              Qt::AlignCenter, displayText);


            painter.drawLine(f.right() -2 - textBoxWidth, f.center().y() , f.center().x() + probeDisplaySize/4, f.center().y() );

        }

    }
    QRect f = frameList[frameList.size()-1];
    QPolygon trianglePoly;
    trianglePoly << QPoint( f.center().x() - (probeDisplaySize)/2 , f.top()) ;
    trianglePoly << QPoint( f.center().x() + (probeDisplaySize)/2 , f.top()) ;
    trianglePoly << QPoint (f.center().x(), f.bottom());
    QPainterPath trianglePath;
    trianglePath.addPolygon(trianglePoly);
    painter.fillPath(trianglePath, electrodeBackgroundBrush );

    update();
}

void ShankDisplay::setUpFrames(){

    frame = rect();
    int numberOfFrames = mainWindow->electrodesPerShank;
    int ySize = (height() -10)/(numberOfFrames + 1);
    int xSize = width() - 10;

    int xOffset = 5;
    int yOffset = 2;

    frameList.resize(numberOfFrames+1);
    for(int i = 0 ;  i < numberOfFrames; ++i){
        frameList[numberOfFrames - i - 1] =QRect(xOffset, yOffset + i*ySize, xSize,ySize);
    }
    //frame for triangle
    frameList[numberOfFrames] = QRect(xOffset, yOffset + numberOfFrames*ySize, xSize,ySize);
}

void ShankDisplay::getStartIndexOfDisplay(){

    if(mainWindow->probeType == LINEAR_PROBE_TYPE){
        startIndexOfDisplay = mainWindow->currentShank * mainWindow->electrodesPerShank;
    }else{
        startIndexOfDisplay = 4 * mainWindow->currentShank * mainWindow->electrodesPerShank;
    }
}

void ShankDisplay::updatePlot(){
    draw();
}

int ShankDisplay::findClosestChannel2Click(QPoint p){
    int distance2 = 0;
    int smallestDistance2 = 0;
    int closestShankIndex = -1;
    int closestFrameIndex = -1;
    int closestTetroteIndex = -1;
        for(int i = 0 ; i < frameList.size() -1 ; ++i ) {

            QRect f = frameList[i];
            distance2 = (p.x() - f.center().x())*(p.x() - f.center().x()) +
                            (p.y() - f.center().y())*(p.y() - f.center().y());

            if ((distance2 < smallestDistance2) || i==0){
                smallestDistance2 = distance2;
                closestFrameIndex = i;
                //for tetrote there is an additional comparison for which electrode to detect inside the tetrote
                if(mainWindow->probeType == TETROTE_PROBE_TYPE){
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

    int result;
    if (mainWindow->probeType == LINEAR_PROBE_TYPE){
        result = startIndexOfDisplay + closestFrameIndex;
    }
    else{
        result = startIndexOfDisplay + closestFrameIndex*4 + closestTetroteIndex;
    }

    return result;
}

void ShankDisplay::paintEvent(QPaintEvent * /* event */)
{
    QStylePainter stylePainter(this);
    stylePainter.drawPixmap(0, 0, pixmap);
}

void ShankDisplay::mousePressEvent(QMouseEvent *event){
    if (event->button() == Qt::LeftButton) {
        mainWindow->currentIndexInMap = findClosestChannel2Click(event->pos());
        draw();
    } else {
        QWidget::mousePressEvent(event);
    }
}


void ShankDisplay::resizeEvent(QResizeEvent*) {
    // Pixel map used for double buffering.
    pixmap = QPixmap(size());
    pixmap.fill();
    draw();
}

QSize ShankDisplay::minimumSizeHint() const
{
    return QSize(SHANK_X_SIZE, SHANK_Y_SIZE);
}

QSize ShankDisplay::sizeHint() const
{
    return QSize(SHANK_X_SIZE, SHANK_Y_SIZE);
}
