import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    
    SystemPalette {
        id: systemPalette
        colorGroup: SystemPalette.Active
    }
    
    title: qsTr("Settings")
    x: (window.width - (width || 450)) / 2
    y: (window.height - (height || 400)) / 2
    modal: true
    standardButtons: DialogButtonBox.Ok | DialogButtonBox.Cancel
    width: 450
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 15
        spacing: 15
        
        GroupBox {
            title: qsTr("Downloads")
            Layout.fillWidth: true
            
            ColumnLayout {
                spacing: 10
                anchors.fill: parent
                
                RowLayout {
                    Layout.fillWidth: true
                    Label { text: qsTr("Download path:"); Layout.preferredWidth: 100 }
                    TextField {
                        id: downloadPathField
                        Layout.fillWidth: true
                        text: launcher ? launcher.downloadPath : ""
                        readOnly: true
                    }
                    Button {
                        text: qsTr("Browse")
                        onClicked: {
                            // TODO: Implement folder picker
                        }
                    }
                }
            }
        }
        
        GroupBox {
            title: qsTr("Appearance")
            Layout.fillWidth: true
            
            ColumnLayout {
                spacing: 10
                anchors.fill: parent
                
                CheckBox {
                    id: showNotificationsCheck
                    text: qsTr("Show notifications")
                    checked: true
                }
            }
        }
        
        GroupBox {
            title: qsTr("About")
            Layout.fillWidth: true
            
            ColumnLayout {
                anchors.fill: parent
                Label {
                    text: qsTr("Amethyst Launcher v") + (appVersion || "0.1.0a")
                }
                Label {
                    text: qsTr("A Geometry Dash launcher with Geode support")
                    font.pixelSize: 11
                    color: systemPalette.text
                }
            }
        }
    }
    
    onAccepted: {
        // No settings currently need explicit saving here
    }
}