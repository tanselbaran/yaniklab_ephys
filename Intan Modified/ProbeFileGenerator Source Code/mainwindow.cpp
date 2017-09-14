
#include "mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent)
{
    shankDisplay = 0;
    numberOfElectrodes = 0;
    numberOfShank = 1;
    currentIndexInMap = 0;
    currentShank = 0;

    //save Directory
    saveDirectoryLabel = new QLabel("Not selected");
    selectSaveDirectoryPushButton = new QPushButton(tr("Save Directory"));

    connect(selectSaveDirectoryPushButton, SIGNAL(clicked(bool)), this , SLOT(selectSaveDirectory()));

    QHBoxLayout *saveDirectoryLayout = new QHBoxLayout;
    saveDirectoryLayout->addWidget(selectSaveDirectoryPushButton);
    saveDirectoryLayout->addWidget(saveDirectoryLabel);

    //name part
    probeNameLineEdit  = new QLineEdit(tr("Please type name here"));

    QHBoxLayout *nameLayout = new QHBoxLayout;
    nameLayout->addWidget(new QLabel(tr("Probe Name:")));
    nameLayout->addWidget(probeNameLineEdit);


    //Probe properties part
    numberOfShanksLineEdit = new QLineEdit(tr("x"));
    numberOfElectrodesLineEdit = new QLineEdit(tr("xx"));

    probeTypeComboBox = new QComboBox;
    probeTypeComboBox->addItem(tr("linear"));
    probeTypeComboBox->addItem(tr("tetrote"));
    probeTypeComboBox->setCurrentIndex(0);
    probeType = LINEAR_PROBE_TYPE;

    connect(probeTypeComboBox, SIGNAL(currentIndexChanged(int)) , this , SLOT(setProbeType(int)));


    QHBoxLayout *probePropertiesLayout = new QHBoxLayout;
    probePropertiesLayout->addWidget(new QLabel(tr("number of Shanks")));
    probePropertiesLayout->addWidget(numberOfShanksLineEdit);
    probePropertiesLayout->addWidget(new QLabel(tr("Type")));
    probePropertiesLayout->addWidget(probeTypeComboBox);
    probePropertiesLayout->addWidget(new QLabel(tr("number of Electrodes")));
    probePropertiesLayout->addWidget(numberOfElectrodesLineEdit);

    //Mapping start stop buttons
    startMappingPushButton = new QPushButton(tr("Start Mapping"));
    connect(startMappingPushButton, SIGNAL(clicked(bool)), this , SLOT(startMapping()));

    clearMappingPushButton = new QPushButton(tr("Clear Mapping"));
    clearMappingPushButton->setEnabled(false);
    connect(clearMappingPushButton, SIGNAL(clicked(bool)), this , SLOT(clearMapping()));

    saveProbePushButton = new QPushButton(tr("Save Probe"));
    saveProbePushButton->setEnabled(false);
    connect(saveProbePushButton, SIGNAL(clicked(bool)), this , SLOT(saveProbe()));

    QHBoxLayout *mappingButtonsLayout = new QHBoxLayout;
    mappingButtonsLayout->addWidget(startMappingPushButton);
    mappingButtonsLayout->addWidget(clearMappingPushButton);
    mappingButtonsLayout->addWidget(saveProbePushButton);


    QVBoxLayout *leftLayout = new QVBoxLayout;
    leftLayout->addLayout(saveDirectoryLayout);
    leftLayout->addLayout(nameLayout);
    leftLayout->addLayout(probePropertiesLayout);
    leftLayout->addLayout(mappingButtonsLayout);


    electrodeRegisterLineEdit = new QLineEdit(tr("Enter number of Red Electrode"));
    electrodeRegisterLineEdit->setEnabled(false);
    connect(electrodeRegisterLineEdit, SIGNAL(returnPressed()), this, SLOT(addElementToMap()));

    registerEachShankComboBox = new QComboBox;
    registerEachShankComboBox->addItem(tr("No Shank found to Display"));
    registerEachShankComboBox->setEnabled(false);
    connect(registerEachShankComboBox, SIGNAL(currentIndexChanged(int)),this,SLOT(shankChanged(int)));

    rightLayout = new QVBoxLayout;
    rightLayout->addWidget(electrodeRegisterLineEdit);
    rightLayout->addWidget(registerEachShankComboBox);


    mainLayout = new QHBoxLayout;
    mainLayout->addLayout(leftLayout);
    mainLayout->addLayout(rightLayout);

    QWidget *mainWidget = new QWidget;
    mainWidget->setLayout(mainLayout);

    setCentralWidget(mainWidget);

}


void MainWindow::startMapping(){
    //get name
    probeName = probeNameLineEdit->text();
    probeNameLineEdit->setEnabled(false);

    //fileName
    //fileName = folderName + probeName + ".dat" ;
    selectSaveDirectoryPushButton->setEnabled(false);

    //get number of shank
    numberOfShank = numberOfShanksLineEdit->text().toInt();
    numberOfShanksLineEdit->setEnabled(false);

    //get number of Electrodes
    numberOfElectrodes = numberOfElectrodesLineEdit->text().toInt();
    numberOfElectrodesLineEdit->setEnabled(false);

    if(probeType == LINEAR_PROBE_TYPE){electrodesPerShank = numberOfElectrodes / numberOfShank;}
    else{electrodesPerShank = numberOfElectrodes / (numberOfShank*4);}

    //disable the probeTypeComboBox
    probeTypeComboBox->setEnabled(false);

    saveProbePushButton->setEnabled(false);

    //Initiliaze for registration
    probeMap.resize(numberOfElectrodes);
    probeMap.fill(-1);

    currentIndexInMap = 0;
    currentShank = 0;

    //Adjust the shank number combo bar

    for (int i = 0 ; i < numberOfShank ; ++i){
        QString stringText = "Shank " + QString::number(i+1);
        registerEachShankComboBox->addItem(stringText);
    }
    registerEachShankComboBox->removeItem(0);
    registerEachShankComboBox->setEnabled(true);

    //Display the probe and add to Main Layout
    //Enable changes to the map
    electrodeRegisterLineEdit->setEnabled(true);
    clearMappingPushButton->setEnabled(true);
    startMappingPushButton->setEnabled(false);

    if(shankDisplay){ rightLayout->removeWidget(shankDisplay); shankDisplay->~ShankDisplay() ; shankDisplay = 0;}

    shankDisplay = new ShankDisplay(this,this);
    rightLayout->addWidget(shankDisplay);

}

void MainWindow::clearMapping(){

    //clear items from registerEachShankComboBox
    registerEachShankComboBox->addItem(tr("No Shank found to Display"));
    registerEachShankComboBox->setCurrentIndex(0);

    for(int i = 0 ; i < registerEachShankComboBox->count(); ++i){
        registerEachShankComboBox->removeItem(0);
    }
    registerEachShankComboBox->setEnabled(false);

    //Enable interface for changes
    probeNameLineEdit->setEnabled(true);
    selectSaveDirectoryPushButton->setEnabled(true);
    numberOfShanksLineEdit->setEnabled(true);
    numberOfElectrodesLineEdit->setEnabled(true);
    probeTypeComboBox->setEnabled(true);
    startMappingPushButton->setEnabled(true);

    //Prevent changes to the map
    electrodeRegisterLineEdit->setEnabled(false);
    saveProbePushButton->setEnabled(false);

    probeMap.resize(numberOfElectrodes);
    probeMap.fill(-1);

    currentIndexInMap = 0;
    currentShank = 0;
    if(shankDisplay){mainLayout->removeWidget(shankDisplay); shankDisplay->~ShankDisplay(); shankDisplay = 0;}


}

void MainWindow::setProbeType(int index){
    if(index == 0) {probeType = LINEAR_PROBE_TYPE;}
    else{ probeType = TETROTE_PROBE_TYPE;}
}

void MainWindow::selectSaveDirectory(){
    folderName = QFileDialog::getExistingDirectory();
    saveDirectoryLabel->setText(folderName);
}

void MainWindow::saveProbe(){
    fileName = folderName + "/" + probeName + ".dat";

    QFile saveFile(fileName);

    if(!saveFile.open(QFile::WriteOnly)){
        QMessageBox::information(this, tr("ERROR"), tr("Could not open a file. Please Try another name or folder"));
        probeNameLineEdit->setEnabled(true);
        selectSaveDirectoryPushButton->setEnabled(true);
    }


    //open dataStream
    QDataStream dataStream(&saveFile);

    //Set Up the used Format in Intan Software RHD2000 Evaluation Board v1.5.1
    dataStream.setVersion(QDataStream::Qt_4_8);
    dataStream.setByteOrder(QDataStream::LittleEndian);

    dataStream << (quint16(0x0000FFFF & numberOfElectrodes));
    dataStream << (quint16 (0x0000FFFF & numberOfShank));
    dataStream << (quint16)(0x0000FFFF & electrodesPerShank);
    dataStream << (quint16)probeType;

    //after this point changes with respect to the probe Type selected
    if( probeType == LINEAR_PROBE_TYPE){
        for(int i = 0 ; i < numberOfElectrodes ; ++i){
            dataStream << (quint16)probeMap[i];
        }
    }else{
        for(int i = 0 ; i < electrodesPerShank; ++i){
            for( int j = 0 ; j < numberOfShank; ++j){
                int mapIndex = j*(numberOfElectrodes/numberOfShank) + i*4;
                dataStream << (quint16)probeMap[mapIndex]; //0
                mapIndex++;
                dataStream << (quint16)probeMap[mapIndex]; //1
                mapIndex++;
                dataStream << (quint16)probeMap[mapIndex]; //2
                mapIndex++;
                dataStream << (quint16)probeMap[mapIndex]; //3
            }
        }
    }

    saveFile.flush();
    saveFile.close();

    QMessageBox::information(this, tr("MESSAGE"), tr("Save is complete! Thanks for using this app."));
    clearMapping();

}

void MainWindow::addElementToMap(){


    int dummyNumber = electrodeRegisterLineEdit->text().toInt();

    if(dummyNumber > numberOfElectrodes || dummyNumber < 0){
        QMessageBox::information(this, tr("ERROR"),tr("Please Enter a Valid Number for Electrode"));
    }else{
        probeMap[currentIndexInMap] = dummyNumber;
        if( ++currentIndexInMap == numberOfElectrodes){
            currentIndexInMap = numberOfElectrodes - 1;
            QMessageBox::information(this, tr("PROBE REGISTER"),tr("Probe Registration completed Please Control and Proceed to Save"));
            saveProbePushButton->setEnabled(true);
        }
        currentShank = (probeType == LINEAR_PROBE_TYPE) ? currentIndexInMap/electrodesPerShank : currentIndexInMap/(4*electrodesPerShank);
        registerEachShankComboBox->setCurrentIndex(currentShank);
        emit newMapElementRecieved();
    }

    electrodeRegisterLineEdit->setText(tr(" "));
    update();
}

void MainWindow::shankChanged(int index){
    currentShank = index;
    currentIndexInMap = currentShank*(numberOfElectrodes/numberOfShank);
    emit newMapElementRecieved();
}

