import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    
    property string setupStatus: "ready"
    property string statusMessage: ""
    
    SystemPalette {
        id: systemPalette
        colorGroup: SystemPalette.Active
    }
    
    title: qsTr("Setup Required")
    x: (window.width - (width || 450)) / 2
    y: (window.height - (height || 350)) / 2
    modal: true
    width: 450
    
    function checkStatus() {
        if (launcher) {
            root.setupStatus = launcher.check_setup_status()
            if (root.setupStatus === "needs_ownership") {
                statusMessage = "You need to own Geometry Dash on Steam to use this launcher."
            } else if (root.setupStatus === "needs_permissions") {
                statusMessage = "Amethyst needs permission to manage the game folder."
            } else {
                root.close()
            }
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 15
        
        Label {
            text: qsTr("Setup Required")
            font.bold: true
            font.pixelSize: 16
        }
        
        Rectangle { Layout.fillWidth: true; height: 1; color: systemPalette.mid }
        
        Label {
            text: root.statusMessage
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            color: systemPalette.text
        }
        
        Item { Layout.fillHeight: true }
        
        ColumnLayout {
            visible: root.setupStatus === "needs_ownership"
            spacing: 10
            
            Label {
                text: qsTr("How to get Geometry Dash:")
                font.bold: true
            }
            Label {
                text: qsTr("1. Open the Steam Store page below")
                font.pixelSize: 11
                color: systemPalette.text
            }
            Label {
                text: qsTr("2. Purchase (or activate family share)")
                font.pixelSize: 11
                color: systemPalette.text
            }
            Label {
                text: qsTr("3. Verify ownership in Steam settings")
                font.pixelSize: 11
                color: systemPalette.text
            }
            
            Button {
                text: qsTr("Open Steam Store")
                onClicked: {
                    if (launcher) {
                        launcher.open_steam_store()
                    }
                }
            }
        }
        
        ColumnLayout {
            visible: root.setupStatus === "needs_permissions"
            spacing: 10
            
            Label {
                text: qsTr("Authorization Required:")
                font.bold: true
            }
            Label {
                text: qsTr("Amethyst needs to modify the Steam game folder to manage instances. This requires a one-time administrator authorization.")
                font.pixelSize: 11
                color: systemPalette.text
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
            
            Button {
                text: qsTr("Authorize Amethyst")
                Layout.fillWidth: true
                onClicked: {
                    if (launcher) {
                        launcher.request_folder_permissions()
                    }
                }
            }
            
            Label {
                text: qsTr("A UAC prompt will appear. Click Yes to grant permissions.")
                font.pixelSize: 10
                color: systemPalette.mid
            }
        }
        
        RowLayout {
            spacing: 10
            Button {
                text: qsTr("Refresh")
                onClicked: {
                    root.checkStatus()
                }
            }
            Item { Layout.fillWidth: true }
            Button {
                text: qsTr("Done")
                enabled: root.setupStatus === "ready"
                onClicked: {
                    if (launcher) {
                        launcher.refresh_setup_status()
                    }
                    root.close()
                }
            }
            Button {
                text: qsTr("Cancel")
                visible: false
            }
        }
    }
}