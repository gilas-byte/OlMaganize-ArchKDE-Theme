#!/usr/bin/env python3
"""Renderiza os widgets com o tema Kvantum de build/ em um PNG, sem tocar no sistema.

Uso: python3 tests/kvantum-preview.py [saida.png]   (padrão: build/kvantum-preview.png)

Monta um XDG_CONFIG_HOME temporário com o tema renderizado, sobe um QApplication
offscreen com o estilo kvantum e fotografa uma janela com cada widget nos estados que
dá para forçar sem mouse (hover, pressionado, marcado, foco, desabilitado). Precisa de
python-pyqt6 e do tema renderizado (python3 -m tooling render --only kvantum).
"""
import os
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build/kvantum-preview.png").resolve()
    with open(ROOT / "palette.toml", "rb") as f:
        name = tomllib.load(f)["theme"]["name"]
    built = ROOT / "build/kvantum"
    if not (built / "theme.svg").is_file():
        sys.exit("rode antes: python3 -m tooling render --only kvantum")
    with tempfile.TemporaryDirectory() as tmp:
        theme = Path(tmp, "Kvantum", name)
        theme.mkdir(parents=True)
        (theme / f"{name}.kvconfig").symlink_to(built / "theme.kvconfig")
        (theme / f"{name}.svg").symlink_to(built / "theme.svg")
        Path(tmp, "Kvantum", "kvantum.kvconfig").write_text(f"[General]\ntheme={name}\n")
        env = dict(os.environ, XDG_CONFIG_HOME=tmp, QT_QPA_PLATFORM="offscreen",
                   GIBI_PREVIEW_OUT=str(out))
        env.pop("QT_STYLE_OVERRIDE", None)
        subprocess.run([sys.executable, __file__, "--child"], env=env, check=True)
    print(out)


def child():
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout, QGroupBox,
                                 QHBoxLayout, QLabel, QLineEdit, QListWidget, QMenu,
                                 QProgressBar, QPushButton, QRadioButton, QScrollBar,
                                 QSlider, QSpinBox, QTabWidget, QToolButton, QTreeWidget,
                                 QTreeWidgetItem, QVBoxLayout, QWidget)

    app = QApplication(sys.argv)
    app.setStyle("kvantum")
    app.setFont(QFont("Inter", 10))

    def settle():
        # animate_states=true: o Kvantum faz fade de 200 ms ao trocar de estado
        deadline = time.monotonic() + 0.4
        while time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.01)

    def hover(w):
        w.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, True)
        return w

    root = QWidget()
    root.resize(900, 640)
    grid = QGridLayout(root)

    row = QHBoxLayout()
    row.addWidget(QPushButton("Normal"))
    row.addWidget(hover(QPushButton("Hover")))
    pressed = QPushButton("Pressionado")
    pressed.setDown(True)
    row.addWidget(pressed)
    toggled = QPushButton("Marcado")
    toggled.setCheckable(True)
    toggled.setChecked(True)
    row.addWidget(toggled)
    disabled = QPushButton("Desabilitado")
    disabled.setEnabled(False)
    row.addWidget(disabled)
    default = QPushButton("Padrão")
    default.setDefault(True)
    row.addWidget(default)
    grid.addLayout(row, 0, 0, 1, 2)

    row = QHBoxLayout()
    focused = QPushButton("Foco (Tab)")
    row.addWidget(focused)
    tool = QToolButton()
    tool.setText("Ferramenta")
    row.addWidget(tool)
    raised = QToolButton()
    raised.setText("Autoraise hover")
    raised.setAutoRaise(True)
    row.addWidget(hover(raised))
    edit = QLineEdit("campo de texto")
    row.addWidget(edit)
    focused_edit = QLineEdit("campo com foco")
    row.addWidget(focused_edit)
    grid.addLayout(row, 1, 0, 1, 2)

    row = QHBoxLayout()
    combo = QComboBox()
    combo.addItems(["Combo", "Outro"])
    row.addWidget(combo)
    row.addWidget(hover(QComboBox()))
    editable = QComboBox()
    editable.setEditable(True)
    editable.addItem("Combo editável")
    row.addWidget(editable)
    row.addWidget(QSpinBox())
    grid.addLayout(row, 2, 0, 1, 2)

    row = QHBoxLayout()
    for text, checked, cls in (("check", True, QCheckBox), ("desligado", False, QCheckBox),
                               ("radio", True, QRadioButton), ("radio 2", False, QRadioButton)):
        w = cls(text)
        w.setChecked(checked)
        row.addWidget(w)
    tri = QCheckBox("parcial")
    tri.setTristate(True)
    tri.setCheckState(Qt.CheckState.PartiallyChecked)
    row.addWidget(tri)
    off = QCheckBox("desabilitado")
    off.setChecked(True)
    off.setEnabled(False)
    row.addWidget(off)
    grid.addLayout(row, 3, 0, 1, 2)

    tabs = QTabWidget()
    for label in ("Ativa", "Inativa", "Outra"):
        tabs.addTab(QLabel(f"  conteúdo da aba {label.lower()}"), label)
    tabs.setTabsClosable(True)
    grid.addWidget(tabs, 4, 0)

    lists = QListWidget()
    lists.addItems([f"item {i}" for i in range(20)])
    lists.setCurrentRow(2)
    grid.addWidget(lists, 4, 1, 2, 1)

    tree = QTreeWidget()
    tree.setHeaderLabels(["Nome", "Tamanho"])
    parent = QTreeWidgetItem(tree, ["pasta", "3 itens"])
    for i in range(3):
        QTreeWidgetItem(parent, [f"arquivo {i}.txt", "1 KiB"])
    QTreeWidgetItem(tree, ["fechada", "—"]).addChild(QTreeWidgetItem(["x"]))
    parent.setExpanded(True)
    tree.setCurrentItem(parent.child(1))
    grid.addWidget(tree, 5, 0)

    row = QHBoxLayout()
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setValue(40)
    row.addWidget(slider)
    bar = QProgressBar()
    bar.setValue(60)
    row.addWidget(bar)
    scroll = QScrollBar(Qt.Orientation.Horizontal)
    scroll.setRange(0, 100)
    scroll.setPageStep(30)
    row.addWidget(scroll)
    grid.addLayout(row, 6, 0, 1, 2)

    box = QGroupBox("Grupo")
    QVBoxLayout(box).addWidget(QLabel("dentro do grupo"))
    grid.addWidget(box, 7, 0)
    tip = QLabel("  dica (tooltip)  ")
    tip.setWindowFlags(Qt.WindowType.ToolTip)
    grid.addWidget(QLabel("menu e tooltip: arquivos separados (-menu.png)"), 7, 1)

    root.show()
    root.activateWindow()
    focused.setFocus(Qt.FocusReason.TabFocusReason)
    settle()
    out = Path(os.environ["GIBI_PREVIEW_OUT"])
    root.grab().save(str(out))

    focused_edit.setFocus(Qt.FocusReason.TabFocusReason)
    settle()
    root.grab().save(str(out.with_name(out.stem + "-foco-campo.png")))

    menu = QMenu()
    menu.addAction("Abrir")
    menu.addAction("Salvar").setEnabled(False)
    menu.addSeparator()
    check = menu.addAction("Opção marcada")
    check.setCheckable(True)
    check.setChecked(True)
    menu.addMenu("Submenu").addAction("x")
    menu.setActiveAction(menu.actions()[0])
    menu.popup(root.mapToGlobal(root.rect().center()))
    tip.show()
    app.processEvents()
    menu.grab().save(str(out.with_name(out.stem + "-menu.png")))
    tip.grab().save(str(out.with_name(out.stem + "-tooltip.png")))


if __name__ == "__main__":
    child() if "--child" in sys.argv else main()
