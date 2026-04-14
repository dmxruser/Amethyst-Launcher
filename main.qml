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
    color: systemPalette.window

    SystemPalette {
        id: systemPalette
        colorGroup: SystemPalette.Active
    }
    
    Component.onCompleted: {
        if (launcher && launcher.setupStatus !== "ready") {
            setupWizard.setupStatus = launcher.setupStatus
            setupWizard.open()
        }
    }

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
                ToolButton {
                    text: qsTr("Logs")
                    onClicked: {
                        logDialog.logText = launcher ? launcher.get_debug_log() : "No launcher"
                        logDialog.open()
                    }
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
        launcher: launcher

        Connections {
            target: downloader
            function onOutput_received(line) { downloadDialog.statusText = line }
            function onFinished(success, msg) {
                downloadDialog.statusText = msg
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
        onGeodeToggled: (enabled) => launcher ? launcher.toggle_geode(instanceIndex, enabled) : null
        onInstallGeode: () => launcher ? launcher.install_geode(instanceIndex) : null

        Connections {
            target: launcher || null
            function onGeodeStatusChanged(msg) { optionsDialog.statusLabel.text = msg }
        }
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
    
    SetupWizard {
        id: setupWizard
        
        Connections {
            target: launcher
            function onSetupStatusChanged(status) {
                if (status !== "ready") {
                    setupWizard.setupStatus = status
                    setupWizard.open()
                } else {
                    setupWizard.close()
                }
            }
        }
    }

    Dialog {
        id: logDialog
        title: qsTr("Debug Logs")
        width: 500
        height: 400
        standardButtons: DialogButtonBox.Close

        ScrollView {
            anchors.fill: parent
            TextArea {
                id: logTextArea
                readOnly: true
                text: logDialog.logText
                font.family: "monospace"
                font.pixelSize: 10
            }
        }

        property string logText: ""
    }

    property string selectedProfile: "Default"

    ListModel {
        id: profileModel
    }
}