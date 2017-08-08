#ifndef PROBEDISPLAYWIDGET_H
#define PROBEDISPLAYWIDGET_H


#include <QWidget>


class QComboBox;
class QPushButton;
class QLabel;
class WavePlot;
class QVBoxLayout;
class Probe;
class SignalChannel;

class ProbeDisplayWidget : public QWidget
{
    Q_OBJECT
public:
    explicit ProbeDisplayWidget(WavePlot *inWavePlot, QWidget *parent = 0);

    void setNewChannel(SignalChannel  *newChannel  );

signals:
    void selectedChannelChanged(SignalChannel* newChannel);

public slots:

private slots:
    void echoChannelChange(SignalChannel* newChannel);
    void loadProbeFolder();
    void groupWavePlots( int index);
    void selectProbe(int index);
    void adjustGroupingOptions();
private:
    WavePlot *wavePlot;
    Probe *probe;

    QVector<QString> probeNameList;
    QVector<int> probeTypeList;
    QVector<int> probeNumberOfShanksList;
    QVector<QVector<int>> probeMapList;

    QPushButton *loadProbeFolderButton;

    QComboBox *selectProbeComboBox;
    QComboBox *groupWavePlotsComboBox;

    QLabel *displayProbeNameLabel;

    QVBoxLayout *mainLayout;
    void updateLayout();
    void setUpDefaultProbes();

};

#endif // PROBEDISPLAYWIDGET_H
