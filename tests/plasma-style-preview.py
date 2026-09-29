#!/usr/bin/env python3
"""Renderiza o Plasma Style de build/ com o KSvg de verdade, sem tocar no sistema.

Uso: python3 tests/plasma-style-preview.py [saida.png]   (padrão: build/plasma-style-preview.png)

Monta XDG_DATA_HOME/XDG_CONFIG_HOME/XDG_CACHE_HOME temporários (tema, plasmarc e as cores
do esquema Gibi) e fotografa uma cena QML offscreen: barra encostada e flutuante,
tarefas nos 5 estados, popup com cabeçalho, dica e os controles do Plasma
(PlasmaComponents 3). Precisa de python-pyqt6 e do tema renderizado
(python3 -m tooling render --only plasma-style,kde-colors).
"""
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCENE = r"""
import QtQuick
import QtQuick.Layouts
import org.kde.ksvg as KSvg
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PC3

Rectangle {
    width: 980; height: 640
    gradient: Gradient {
        GradientStop { position: 0.0; color: "#6d7f8a" }
        GradientStop { position: 0.5; color: "#b88a5a" }
        GradientStop { position: 1.0; color: "#3c4a3a" }
    }

    // barra de cima encostada: só a borda de baixo
    KSvg.FrameSvgItem {
        x: 0; y: 0; width: parent.width; height: 32
        imagePath: "widgets/panel-background"
        enabledBorders: KSvg.FrameSvg.BottomBorder
    }
    // barra flutuante com as tarefas: todas as bordas
    KSvg.FrameSvgItem {
        id: dock
        x: 150; y: 560; width: 680; height: 56
        imagePath: "widgets/panel-background"
        Row {
            anchors.centerIn: parent
            spacing: 6
            Repeater {
                model: ["normal", "hover", "focus", "attention", "minimized", "progress"]
                KSvg.FrameSvgItem {
                    width: 96; height: 44
                    imagePath: "widgets/tasks"
                    prefix: modelData
                    PC3.Label { anchors.centerIn: parent; text: modelData }
                }
            }
        }
    }

    // sombra do popup (no sistema quem desenha é o KWin, com estas mesmas peças)
    KSvg.FrameSvgItem {
        x: popup.x - 10; y: popup.y - 10; width: popup.width + 20; height: popup.height + 20
        imagePath: "dialogs/background"; prefix: "shadow"
    }
    // popup (diálogo do Plasma) com cabeçalho
    KSvg.FrameSvgItem {
        id: popup
        x: 30; y: 60; width: 460; height: 470
        imagePath: "dialogs/background"
        KSvg.FrameSvgItem {
            x: 0; y: 0; width: parent.width; height: 44
            imagePath: "widgets/plasmoidheading"
            prefix: "header"
            PC3.Label { anchors.centerIn: parent; text: "Cabeçalho do popup" }
        }
        ColumnLayout {
            x: 16; y: 56; width: parent.width - 32
            spacing: 10
            RowLayout {
                PC3.Button { text: "Botão" }
                PC3.Button { text: "Marcado"; checkable: true; checked: true }
                PC3.Button { text: "Desabilitado"; enabled: false }
                PC3.ToolButton { icon.name: "configure"; text: "Ferramenta" }
            }
            PC3.TextField { Layout.fillWidth: true; placeholderText: "Buscar…" }
            RowLayout {
                PC3.CheckBox { text: "check"; checked: true }
                PC3.CheckBox { text: "desligado" }
                PC3.RadioButton { text: "radio"; checked: true }
                PC3.RadioButton { text: "radio 2" }
            }
            RowLayout {
                PC3.Switch { text: "ligado"; checked: true }
                PC3.Switch { text: "desligado" }
            }
            PC3.Slider { Layout.fillWidth: true; value: 0.4 }
            PC3.ProgressBar { Layout.fillWidth: true; value: 0.6 }
            PC3.TabBar {
                Layout.fillWidth: true
                PC3.TabButton { text: "Ativa" }
                PC3.TabButton { text: "Inativa" }
            }
            RowLayout {
                spacing: 6
                Repeater {
                    model: ["normal", "hover", "selected", "selected+hover"]
                    KSvg.FrameSvgItem {
                        Layout.preferredWidth: 96; Layout.preferredHeight: 30
                        imagePath: "widgets/viewitem"; prefix: modelData
                        PC3.Label { anchors.centerIn: parent; text: modelData }
                    }
                }
            }
        }
    }

    // estados sobrepostos do botão e do campo, lado a lado
    Column {
        x: 520; y: 60; spacing: 10
        Repeater {
            model: [["widgets/button", "normal", ""], ["widgets/button", "normal", "hover"],
                    ["widgets/button", "pressed", ""], ["widgets/button", "normal", "focus"],
                    ["widgets/button", "toolbutton-hover", ""], ["widgets/lineedit", "base", ""],
                    ["widgets/lineedit", "base", "hover"], ["widgets/lineedit", "base", "focus"]]
            KSvg.FrameSvgItem {
                width: 200; height: 34
                imagePath: modelData[0]; prefix: modelData[1]
                KSvg.FrameSvgItem {
                    anchors.fill: parent; visible: modelData[2] !== ""
                    imagePath: modelData[0]; prefix: modelData[2]
                }
                PC3.Label { anchors.centerIn: parent; text: modelData[1] + (modelData[2] ? " + " + modelData[2] : "") }
            }
        }
    }

    // dica
    KSvg.FrameSvgItem {
        x: 760; y: 70; width: 190; height: 34
        imagePath: "widgets/tooltip"
        PC3.Label { anchors.centerIn: parent; text: "Dica (tooltip)" }
    }
}
"""

GRAB = r"""
import sys
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQuick import QQuickView
app = QGuiApplication(sys.argv)
view = QQuickView()
view.setSource(QUrl.fromLocalFile(sys.argv[1]))
errors = [e.toString() for e in view.errors()]
if errors:
    sys.exit("\n".join(errors))
view.show()
QTimer.singleShot(1500, lambda: (view.grabWindow().save(sys.argv[2]), app.quit()))
app.exec()
"""


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build/plasma-style-preview.png").resolve()
    with open(ROOT / "palette.toml", "rb") as f:
        name = tomllib.load(f)["theme"]["name"]
    theme, scheme = ROOT / "build/plasma-style/theme", ROOT / "build/kde-colors/scheme.colors"
    if not (theme / "metadata.json").is_file() or not scheme.is_file():
        sys.exit("rode antes: python3 -m tooling render --only plasma-style,kde-colors")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "data/plasma/desktoptheme").mkdir(parents=True)
        (tmp / "data/plasma/desktoptheme" / name).symlink_to(theme)
        (tmp / "config").mkdir()
        (tmp / "config/plasmarc").write_text(f"[Theme]\nname={name}\n")
        shutil.copy(scheme, tmp / "config/kdeglobals")  # o .colors tem o formato do kdeglobals
        (tmp / "scene.qml").write_text(SCENE)
        (tmp / "grab.py").write_text(GRAB)
        env = dict(os.environ, XDG_DATA_HOME=str(tmp / "data"), XDG_CONFIG_HOME=str(tmp / "config"),
                   XDG_CACHE_HOME=str(tmp / "cache"), QT_QPA_PLATFORM="offscreen")
        subprocess.run([sys.executable, tmp / "grab.py", tmp / "scene.qml", out], env=env, check=True)
    print(out)


if __name__ == "__main__":
    main()
