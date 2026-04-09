import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "ui/dialogs"
import "ui/components"

ApplicationWindow {
    id: window
    width: 900
    height: 600
    visible: true
    title: qsTr("Amethyst Launcher")
    color: palette.window

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Global Toolbar
        ToolBar {
            Layout.fillWidth: true
            RowLayout {
                anchors.fill: parent
                ToolButton {
                    text: qsTr("Add Instance")
                    onClicked: downloadDialog.open()
                }
                ToolButton {
                    text: qsTr("Settings")
                    onClicked: settingsDialog.open()
                }
                Item { Layout.fillWidth: true }
                ToolButton {
                    text: qsTr("Refresh")
                    onClicked: launcher ? launcher.detect_installations() : null
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // Instance Grid
            InstanceGrid {
                id: instanceGrid
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                onInstanceSelected: (index) => sidebar.updateSidebar(index)
                onInstanceDoubleClicked: (index) => launcher ? launcher.launch_instance_with_profile(index, window.selectedProfile) : null
            }

            // Instance Sidebar
            InstanceSidebar {
                id: sidebar
                Layout.fillHeight: true
                Layout.preferredWidth: 180
                
                currentIndex: instanceGrid.currentIndex
                instanceName: (launcher && currentIndex !== -1) ? launcher.instanceModel().data(launcher.instanceModel().index(currentIndex, 0), 257) : ""
                ownershipStatus: (launcher && currentIndex !== -1) ? launcher.get_ownership(currentIndex) : "Unknown"
                source: (launcher && currentIndex !== -1) ? launcher.get_source(currentIndex) : "Steam"
                canLaunch: {
                    if (!launcher || currentIndex === -1) return false
                    var src = launcher.get_source(currentIndex)
                    if (src === "Local") return true
                    var status = launcher.get_ownership(currentIndex)
                    return status === "Owned" || status === "Family Shared"
                }
                selectedProfile: window.selectedProfile
                
                onLaunchClicked: launcher ? launcher.launch_instance_with_profile(currentIndex, window.selectedProfile) : null
                onEditClicked: {
                    optionsDialog.instanceIndex = currentIndex
                    optionsDialog.selectedProfile = window.selectedProfile
                    optionsDialog.open()
                }
                onFolderClicked: launcher ? launcher.open_instance_folder(currentIndex) : null
                onDeleteClicked: {
                    if (launcher) {
                        deleteConfirmDialog.instanceName = launcher.instanceModel().data(launcher.instanceModel().index(currentIndex, 0), 257)
                        deleteConfirmDialog.open()
                    }
                }
            }
        }
    }

    DownloadDialog {
        id: downloadDialog
        
        Connections {
            target: downloader || null
            function onOutput_received(line) { downloadDialog.statusText = line }
            function onFinished(success, msg) {
                downloadStatusLabel.text = msg
                if (success && launcher) {
                    launcher.detect_installations()
                }
            }
        }
    }

    InstanceOptionsDialog {
        id: optionsDialog
        
        onProfileSelected: (name) => window.selectedProfile = name
        onProfileCreated: (name) => launcher ? launcher.create_geode_profile(instanceIndex, name) : null
        onProfileDeleted: (name) => launcher ? launcher.delete_geode_profile(instanceIndex, name) : null
    }

    SettingsDialog {
        id: settingsDialog
    }

    DeleteConfirmDialog {
        id: deleteConfirmDialog
        
        onAccepted: {
            if (launcher) {
                launcher.delete_instance(instanceGrid.currentIndex)
                instanceGrid.currentIndex = -1
            }
        }
    }

    property string selectedProfile: "Default"

    ListModel {
        id: profileModel
    }
}