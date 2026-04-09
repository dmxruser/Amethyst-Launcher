import QtQuick
import QtQuick.Controls

Dialog {
    id: root
    
    property string instanceName: ""
    
    title: qsTr("Delete Instance")
    standardButtons: DialogButtonBox.Yes | DialogButtonBox.No
    width: 350
    
    Label {
        text: qsTr("Are you sure you want to delete \"%1\"?\n\nThis action cannot be undone.".arg(root.instanceName))
        wrapMode: Text.WordWrap
    }
}