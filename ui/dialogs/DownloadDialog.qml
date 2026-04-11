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
    y: (window.height - (height || 450)) / 2
    modal: true
    standardButtons: DialogButtonBox.Cancel
    width: 400
    
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
            text: qsTr("<b>Setup Required:</b> Complete the setup wizard before downloading.")
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            font.pixelSize: 11
            color: "#ff6600"
        }

        Label {
            text: qsTr("<b>Steam Client Required:</b> This launcher uses your installed Steam client's console to fetch official game files. You must be logged into a Steam account that owns Geometry Dash.")
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            font.pixelSize: 11
            color: systemPalette.text
        }

        Rectangle { Layout.fillWidth: true; height: 1; color: systemPalette.mid }

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