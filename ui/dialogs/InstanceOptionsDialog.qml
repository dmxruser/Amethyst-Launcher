import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    
    property int instanceIndex: -1
    property string instanceName: ""
    property bool geodeEnabled: false
    property var profiles: []
    property string selectedProfile: "Default"
    
    signal profileSelected(string profile)
    signal profileCreated(string name)
    signal profileDeleted(string name)
    signal geodeToggled(bool enabled)
    signal instanceRenamed(string newName)
    
    title: qsTr("Instance Options")
    x: (window.width - width) / 2
    y: (window.height - height) / 2
    modal: true
    standardButtons: DialogButtonBox.Ok | DialogButtonBox.Cancel
    implicitWidth: 500
    
    onOpened: refresh()
    
    function refresh() {
        if (root.instanceIndex === -1) return
        nameField.text = launcher.instanceModel().data(launcher.instanceModel().index(root.instanceIndex, 0), 257)
        geodeEnabledCheck.checked = launcher.get_geode_enabled(root.instanceIndex)
        refreshProfiles()
    }
    
    function refreshProfiles() {
        profileListModel.clear()
        var profs = launcher.get_profiles(root.instanceIndex)
        for (var i = 0; i < profs.length; i++) {
            profileListModel.append({name: profs[i]})
        }
    }

    contentItem: ColumnLayout {
        spacing: 15
        
        GroupBox {
            title: qsTr("General")
            Layout.fillWidth: true
            
            RowLayout {
                width: parent.width
                Label { text: qsTr("Name:") }
                TextField {
                    id: nameField
                    Layout.fillWidth: true
                }
            }
        }

        GroupBox {
            title: qsTr("Geode")
            Layout.fillWidth: true
            Layout.preferredHeight: 300
            
            ColumnLayout {
                anchors.fill: parent

                CheckBox {
                    id: geodeEnabledCheck
                    text: qsTr("Enable Geode")
                    onCheckedChanged: root.geodeToggled(checked)
                }
                
                Frame {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    padding: 0
                    
                    ListView {
                        id: profileListView
                        anchors.fill: parent
                        model: ListModel { id: profileListModel }
                        clip: true
                        ScrollBar.vertical: ScrollBar {
                            policy: ScrollBar.AlwaysOn
                        }
                        
                        delegate: ItemDelegate {
                            width: profileListView.width
                            contentItem: RowLayout {
                                spacing: 8
                                Label {
                                    text: name
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                    font.bold: name === root.selectedProfile
                                }
                                Button {
                                    text: name === root.selectedProfile ? qsTr("Selected") : qsTr("Select")
                                    flat: true
                                    enabled: name !== root.selectedProfile
                                    onClicked: root.profileSelected(name)
                                }
                                Button {
                                    text: qsTr("Delete")
                                    flat: true
                                    enabled: name !== "Default"
                                    visible: name !== "Default"
                                    onClicked: {
                                        root.profileDeleted(name)
                                        if (root.selectedProfile === name) root.selectedProfile = "Default"
                                        root.refreshProfiles()
                                    }
                                }
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    TextField {
                        id: newProfileField
                        Layout.fillWidth: true
                        placeholderText: qsTr("New profile name")
                    }
                    Button {
                        text: qsTr("Add")
                        enabled: newProfileField.text.length > 0
                        onClicked: {
                            root.profileCreated(newProfileField.text)
                            newProfileField.text = ""
                            root.refreshProfiles()
                        }
                    }
                }
            }
        }
    }
}