import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    
    property int currentIndex: -1
    
    signal instanceSelected(int index)
    signal instanceDoubleClicked(int index)
    
    SystemPalette {
        id: systemPalette
        colorGroup: SystemPalette.Active
    }
    
    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        
        GridView {
            id: instanceGrid
            anchors.fill: parent
            anchors.margins: 10
            cellWidth: 120
            cellHeight: 140
            model: launcher ? launcher.instanceModel() : null
            clip: true
            
            onCurrentIndexChanged: {
                root.instanceSelected(currentIndex)
            }

            delegate: Item {
                width: instanceGrid.cellWidth
                height: instanceGrid.cellHeight

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: 4
                    color: instanceGrid.currentIndex === index ? systemPalette.highlight : "transparent"
                    radius: 3

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 5

                        Rectangle {
                            width: 64
                            height: 64
                            color: systemPalette.base
                            border.color: systemPalette.mid
                            Layout.alignment: Qt.AlignHCenter
                            radius: 4
                            
                            Text {
                                text: (model && model.source === "Steam") ? "ST" : "LO"
                                anchors.centerIn: parent
                                font.pixelSize: 20
                                color: systemPalette.text
                            }
                        }

                        Text {
                            text: model ? model.name : ""
                            Layout.alignment: Qt.AlignHCenter
                            elide: Text.ElideRight
                            width: parent.width - 10
                            horizontalAlignment: Text.AlignHCenter
                            color: instanceGrid.currentIndex === index ? systemPalette.highlightedText : systemPalette.text
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: instanceGrid.currentIndex = index
                        onDoubleClicked: root.instanceDoubleClicked(index)
                    }
                }
            }
        }
    }
}