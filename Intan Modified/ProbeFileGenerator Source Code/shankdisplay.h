#ifndef SHANKDISPLAY_H
#define SHANKDISPLAY_H

#include <QWidget>
#include "mainwindow.h"

#define SHANK_X_SIZE 120
#define SHANK_Y_SIZE 500
class MainWindow;

class ShankDisplay : public QWidget
{
    Q_OBJECT
public:
    explicit ShankDisplay( MainWindow *inMainWindow, QWidget *parent = 0);

    QSize minimumSizeHint() const;
    QSize sizeHint() const;

signals:

public slots:
    void updatePlot();
protected:

    void paintEvent(QPaintEvent *event);
    //void closeEvent(QCloseEvent *event);
    void mousePressEvent(QMouseEvent *event);
    void resizeEvent(QResizeEvent* event);

private:

    MainWindow *mainWindow;
    int startIndexOfDisplay;

    QVector<QRect> frameList;
    QBrush unselectedElectrodeBrush;
    QBrush selectedElectrodeBrush;
    QBrush electrodeBackgroundBrush;
    QPen unselectedWritingPen;
    QPen selectedWritingPen;

    QPixmap pixmap;
    QRect frame;

    void setUpFrames();
    void getStartIndexOfDisplay();
    void draw();
    int findClosestChannel2Click(QPoint p);

};

#endif // SHANKDISPLAY_H
