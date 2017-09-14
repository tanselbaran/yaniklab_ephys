#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QtWidgets>
#include <iostream>

#include "shankdisplay.h"

#define LINEAR_PROBE_TYPE 0
#define TETROTE_PROBE_TYPE 1

class ShankDisplay;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);

    int currentIndexInMap; //ranges from 0 to numberOfElectrodes - 1
    int currentShank;
    int probeType;
    int numberOfShank;
    int electrodesPerShank; //corresponds to tetrote number per shank for Tetrote probes
    QVector<int> probeMap;

signals:
    void newMapElementRecieved();
public slots:

private slots:

    void setProbeType(int index);
    void shankChanged(int index);

    void selectSaveDirectory();
    void startMapping();
    void saveProbe();
    void clearMapping();
    void addElementToMap();

private:

    QString probeName;

    ShankDisplay *shankDisplay;

    int numberOfElectrodes; //total number electrodes 32 / 64 /128 etc.

    QString fileName; //file name including the path to the file
    QString folderName;

    // user interface widgets
    QLabel *saveDirectoryLabel;

    QHBoxLayout *mainLayout;
    QVBoxLayout *rightLayout;

    QLineEdit *probeNameLineEdit;
    QLineEdit *numberOfShanksLineEdit;
    QLineEdit *numberOfElectrodesLineEdit;

    QLineEdit *electrodeRegisterLineEdit; //registerer for corresponding electrode

    QComboBox *probeTypeComboBox;

    QComboBox *registerEachShankComboBox;

    QPushButton *startMappingPushButton;
    QPushButton *clearMappingPushButton;
    QPushButton *selectSaveDirectoryPushButton;
    QPushButton *checkRegisteredProbePushButton;
    QPushButton *saveProbePushButton;


};

#endif // MAINWINDOW_H
