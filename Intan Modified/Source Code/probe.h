#ifndef PROBE_H
#define PROBE_H

#include <QObject>
#include <QWidget>

#define PROBE_X_SIZE 280
#define PROBE_Y_SIZE 700

class SignalSources;
class SignalChannel;

class Probe : public QWidget
{
    Q_OBJECT
public:
    explicit Probe( QString name, int type, int shankNumber, QVector<int> map, SignalChannel *inSignalChannel, SignalSources *inSignalSources, QWidget *parent = 0);

    QString getProbeName();
    int     getProbeType();
    int     getChannelNumber();

    QVector<QVector<QVector<int>>>  getMap();
    QVector<int> getMapArray();

    void    draw();
    void    setNewChannel(SignalChannel *newChannel);

    QSize minimumSizeHint() const;
    QSize sizeHint() const;

signals:
     void channelChanged(SignalChannel* newChannel);
public slots:

protected:
    void paintEvent(QPaintEvent *event);
    //void closeEvent(QCloseEvent *event);
    void mousePressEvent(QMouseEvent *event);
    void resizeEvent(QResizeEvent* event);

private slots:

private:

    SignalChannel *currentChannel;
    SignalSources  *signalSources;
    int probeType;
    int numberOfShanks;
    QString probeName;
    int selectedElectrodeNumber;

    QVector<QVector<QVector<int>>> probeMap;
    QVector<int> probeMapArray;

    void  convert2Map( QVector<int> map );
    void setUpShanks();
    SignalChannel* findClosestChannel2Click(QPoint p);

    //For Draw function
    QVector<QRect> shankFrames; //assigns each shank corresponding rect to be drawn to
    QVector<QVector<QRect>> subShankFrames; //also includes the low placed triangle
    QPixmap pixmap;
    QRect frame;

};

#endif // PROBE_H
