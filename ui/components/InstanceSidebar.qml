import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: palette.window
    
    property int currentIndex: -1
    property string instanceName: ""
    property string ownershipStatus: "Unknown"
    property string source: "Steam"
    property bool canLaunch: false
    property string selectedProfile: "Default"
    
    signal launchClicked()
    signal editClicked()
    signal folderClicked()
    signal deleteClicked()
    
    function updateSidebar(index) {
        if (index !== -1) {
            root.currentIndex = index
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 6

        Label {
            text: root.currentIndex !== -1 ? root.instanceName : qsTr("Select Instance")
            font.bold: true
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }

        Label {
            text: root.currentIndex !== -1 ? qsTr("Status: ") + root.ownershipStatus : ""
            font.pixelSize: 11
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            color: {
                var status = root.ownershipStatus
                if (status === "Owned" || status === "Family Shared" || status === "N/A (Local)") return "green"
                if (status.startsWith("Unknown")) return "orange"
                return "red"
            }
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: palette.mid }

        Button {
            text: qsTr("Launch")
            Layout.fillWidth: true
            enabled: root.canLaunch
            onClicked: root.launchClicked()
        }

        Button {
            text: qsTr("Edit")
            Layout.fillWidth: true
            enabled: root.currentIndex !== -1
            onClicked: root.editClicked()
        }

        Button {
            text: qsTr("Folder")
            Layout.fillWidth: true
            enabled: root.currentIndex !== -1
            onClicked: root.folderClicked()
        }

        Item { Layout.fillHeight: true }

        Button {
            text: qsTr("Delete")
            Layout.fillWidth: true
            enabled: root.currentIndex !== -1
            onClicked: root.deleteClicked()
        }
    }
}