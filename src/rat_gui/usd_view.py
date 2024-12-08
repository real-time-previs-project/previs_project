from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog
from PyQt5.QtCore import Qt

class USDHierarchyView(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Scene Hierarchy"])
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)
        self.populate_tree()

    def populate_tree(self):
        """Populate the USD hierarchy with sample data."""
        root = QTreeWidgetItem(self, ["world"])
        terrain = QTreeWidgetItem(root, ["terrain"])
        light = QTreeWidgetItem(root, ["light1"])
        camera = QTreeWidgetItem(root, ["camera1"])
        sim = QTreeWidgetItem(root, ["simulation"])

        terrain.addChild(QTreeWidgetItem(["rock"]))
        terrain.addChild(QTreeWidgetItem(["grass"]))

    def open_context_menu(self, position):
        """Open a context menu for tree actions."""
        menu = QMenu()
        add_action = menu.addAction("Add Element")
        delete_action = menu.addAction("Delete Element")
        rename_action = menu.addAction("Rename Element")
        action = menu.exec_(self.viewport().mapToGlobal(position))

        if action == add_action:
            self.add_element()
        elif action == delete_action:
            self.delete_element()
        elif action == rename_action:
            self.rename_element()

    def add_element(self):
        """Add a new element to the tree."""
        selected_item = self.currentItem()
        if selected_item:
            new_item = QTreeWidgetItem(selected_item, ["new_element"])
            selected_item.addChild(new_item)
            selected_item.setExpanded(True)

    def delete_element(self):
        """Delete the selected element from the tree."""
        selected_item = self.currentItem()
        if selected_item and selected_item.parent():
            selected_item.parent().removeChild(selected_item)

    def rename_element(self):
        """Rename the selected element in the tree."""
        selected_item = self.currentItem()
        if selected_item:
            new_name, ok = QInputDialog.getText(self, "Rename Element", "Enter new name:")
            if ok and new_name:
                selected_item.setText(0, new_name)
