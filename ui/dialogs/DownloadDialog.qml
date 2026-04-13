import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root

    property alias statusText: downloadStatusLabel.text
    property alias needsSetup: setupWarning.visible
    property var launcher

    SystemPalette {
        id: systemPalette
        colorGroup: SystemPalette.Active
    }

    title: qsTr("Download New Instance")
    x: (window.width - (width || 400)) / 2
    y: (window.height - (height || 500)) / 2
    modal: true
    closePolicy: Popup.NoAutoClose
    standardButtons: DialogButtonBox.Cancel
    width: 400
    height: 500
    
    onVisibleChanged: {
        if (visible && launcher) {
            var status = launcher.check_setup_status()
            root.needsSetup = (status !== "ready")
            if (status === "needs_ownership") {
                statusText = "You need to own Geometry Dash on Steam first."
            } else if (status === "needs_permissions") {
                statusText = "Please complete setup first."
            }
        }
    }

    function startDownload(name, appId, depotId, manifestId) {
        if (launcher && launcher.check_setup_status() === "ready") {
            launcher.start_download("", "", name, appId, depotId, manifestId, null)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 15
        spacing: 10

        Label {
            id: setupWarning
            visible: false
            text: qsTr("Setup Required")
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            font.pixelSize: 11
            font.bold: true
            color: "#ff6600"
        }

        Rectangle {
            id: steamWarningBox
            Layout.fillWidth: true
            Layout.preferredHeight: steamWarningLayout.implicitHeight + 24
            radius: 2
            color: systemPalette.window
            border.width: 1
            border.color: systemPalette.mid
            
            ColumnLayout {
                id: steamWarningLayout
                anchors.fill: parent
                anchors.margins: 12
                spacing: 6
                
                Label {
                    id: steamWarningTitle
                    text: qsTr("Steam Client Required")
                    font.bold: true
                    font.pixelSize: 12
                    color: systemPalette.text
                    Layout.fillWidth: true
                }
                
                Label {
                    id: steamWarningText
                    text: qsTr("This launcher uses your Steam client to fetch official game files. Make sure Steam is running and you are logged into an account that owns Geometry Dash.")
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                    font.pixelSize: 11
                    lineHeight: 1.2
                    color: systemPalette.text
                    opacity: 0.85
                }
            }
        }

        Label {
            text: qsTr("Instance Name:")
            font.pixelSize: 11
            color: systemPalette.text
        }

        TextField {
            id: instanceName
            placeholderText: qsTr("Instance Name (e.g. 2.11)")
            Layout.fillWidth: true
        }

        ComboBox {
            id: versionSelect
            Layout.fillWidth: true
            model: [
                {text: "2.2081 (Latest 2.2)", app: "322170", depot: "322171", manifest: "3816559102876907245"},
                {text: "2.2074", app: "322170", depot: "322171", manifest: "7678373534998244044"},
                {text: "2.206", app: "322170", depot: "322171", manifest: "7903404280228366327"},
                {text: "2.204", app: "322170", depot: "322171", manifest: "2530486154587189554"},
                {text: "2.11 (Final 2.1)", app: "322170", depot: "322171", manifest: "641118531549408775"},
                {text: "2.1 (Initial)", app: "322170", depot: "322171", manifest: "2062255848267380058"},
                {text: "2.01 (Final 2.0)", app: "322170", depot: "322171", manifest: "631879647548207429"},
                {text: "2.0 (Initial)", app: "322170", depot: "322171", manifest: "2135166447199899913"},
                {text: "1.92", app: "322170", depot: "322171", manifest: "1327679890501772194"}
            ]
            textRole: "text"
        }

        Button {
            text: qsTr("Start Download in Steam")
            Layout.fillWidth: true
            enabled: instanceName.text.length > 0 && !root.needsSetup
            onClicked: {
                var ver = versionSelect.model[versionSelect.currentIndex]
                root.startDownload(
                    instanceName.text,
                    ver.app,
                    ver.depot,
                    ver.manifest
                )
            }
        }

        Label {
            id: downloadStatusLabel
            text: qsTr("Ready")
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            font.pixelSize: 10
            color: systemPalette.mid
        }
    }
}