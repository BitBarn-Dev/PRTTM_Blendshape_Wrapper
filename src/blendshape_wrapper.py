import random
from PySide2 import QtWidgets, QtGui, QtCore
import maya.cmds as cmds
import traceback
from utils import collect_geo_objects, get_maya_main_window
from flow_layout import FlowLayout
from widgets import CheckBoxWidget

class BlendshapeDialog(QtWidgets.QDialog):
    def __init__(self, geo_dict, parent=None):
        super(BlendshapeDialog, self).__init__(parent)
        self.resize(800, 600)
        
        self.setWindowTitle("Blendshape Wrapper")
        self.geo_dict = geo_dict
        self.paired_widgets = []
        
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.render_geo_group = self.create_group("Render Geo")
        self.anim_cache_group = self.create_group("Animation Cache")
        
        self.layout.addWidget(self.render_geo_group)
        self.layout.addWidget(self.anim_cache_group)
        
        self.apply_button = QtWidgets.QPushButton("Apply Blendshapes")
        self.apply_button.clicked.connect(self.apply_blendshapes)
        self.layout.addWidget(self.apply_button)

    def create_group(self, title):
        group_box = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QVBoxLayout(group_box)
        
        namespace_combo = QtWidgets.QComboBox()
        namespace_combo.addItem("Select one")
        namespace_combo.addItems(self.geo_dict.keys())
        namespace_combo.currentIndexChanged.connect(self.update_list_widget)
        
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        list_widget = QtWidgets.QWidget()
        flow_layout = FlowLayout()
        list_widget.setLayout(flow_layout)
        
        scroll_area.setWidget(list_widget)
        
        layout.addWidget(namespace_combo)
        layout.addWidget(scroll_area)
        
        group_box.namespace_combo = namespace_combo
        group_box.scroll_area = scroll_area
        group_box.list_widget = list_widget
        group_box.flow_layout = flow_layout
        
        # Add context menu
        group_box.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        group_box.customContextMenuRequested.connect(lambda pos, gb=group_box: self.show_context_menu(pos, gb))
        
        return group_box

    def show_context_menu(self, pos, group_box):
        context_menu = QtWidgets.QMenu(self)
        
        check_all_action = context_menu.addAction("Check All")
        uncheck_all_action = context_menu.addAction("Uncheck All")
        invert_selection_action = context_menu.addAction("Invert Selection")
        
        action = context_menu.exec_(group_box.mapToGlobal(pos))
        
        if action == check_all_action:
            self.set_all_checked(group_box, True)
        elif action == uncheck_all_action:
            self.set_all_checked(group_box, False)
        elif action == invert_selection_action:
            self.invert_selection(group_box)

    def set_all_checked(self, group_box, checked):
        for widget in self.get_all_widgets(group_box.flow_layout):
            widget.setChecked(checked)
        self.update_pairs()

    def invert_selection(self, group_box):
        for widget in self.get_all_widgets(group_box.flow_layout):
            widget.setChecked(not widget.isChecked())
        self.update_pairs()

    def update_list_widget(self):
        combo = self.sender()
        group_box = combo.parentWidget()
        
        namespace = combo.currentText()
        flow_layout = group_box.flow_layout
        
        # Clear existing widgets
        for i in reversed(range(flow_layout.count())):
            widget = flow_layout.takeAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if namespace != "Select one" and namespace in self.geo_dict:
            # Sort the objects alphabetically
            sorted_objects = sorted(self.geo_dict[namespace], key=str.lower)
            
            for obj in sorted_objects:
                checkbox = CheckBoxWidget(obj)
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(self.update_pairs)
                flow_layout.addWidget(checkbox)
        
        self.update_pairs()

    def update_pairs(self):
        render_geo_widgets = self.get_checked_widgets(self.render_geo_group.flow_layout)
        anim_cache_widgets = self.get_checked_widgets(self.anim_cache_group.flow_layout)
        
        self.paired_widgets = []
        
        for render_widget in render_geo_widgets:
            render_name = render_widget.text()
            for anim_widget in anim_cache_widgets:
                anim_name = anim_widget.text()
                if render_name.lower() == anim_name.lower():
                    self.paired_widgets.append((render_widget, anim_widget))
                    break
        
        self.update_widget_styles()

    def update_widget_styles(self):
        all_widgets = self.get_all_widgets(self.render_geo_group.flow_layout) + \
                      self.get_all_widgets(self.anim_cache_group.flow_layout)
        
        for widget in all_widgets:
            widget.setStyleSheet(self.get_unmatched_style())
        
        for render_widget, anim_widget in self.paired_widgets:
            color = self.generate_matched_color()
            style = self.get_matched_style(color)
            render_widget.setStyleSheet(style)
            anim_widget.setStyleSheet(style)

    def get_unmatched_style(self):
        return """
            QCheckBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
                min-width: 100px;
                max-width: 100px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:checked {
                image: url(:/qt-project.org/styles/commonstyle/images/check.png);
            }
        """

    def get_matched_style(self, color):
        return f"""
            QCheckBox {{
                background-color: {color};
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
                min-width: 100px;
                max-width: 100px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:checked {{
                image: url(:/qt-project.org/styles/commonstyle/images/check.png);
            }}
        """

    def generate_matched_color(self):
        r = random.randint(60, 120)
        g = random.randint(60, 120)
        b = random.randint(60, 120)
        return f"rgb({r}, {g}, {b})"

    def get_all_widgets(self, layout):
        widgets = []
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QtWidgets.QCheckBox):
                widgets.append(widget)
        return widgets

    def get_checked_widgets(self, layout):
        return [w for w in self.get_all_widgets(layout) if w.isChecked()]

    def remove_existing_blendshapes(self, node):
        print(f"Checking for existing blendshapes on node: {node}")
        
        # Check for direct connections
        direct_blendshapes = cmds.listConnections(node, type='blendShape', destination=False, source=True) or []
        
        # Check for blendshapes in the node's history
        history = cmds.listHistory(node) or []
        history_blendshapes = cmds.ls(history, type='blendShape') or []
        
        existing_blendshapes = list(set(direct_blendshapes + history_blendshapes))
        
        print(f"Found {len(existing_blendshapes)} existing blendshape(s) for {node}")
        
        for bs in existing_blendshapes:
            print(f"Removing blendshape: {bs} from node: {node}")
            cmds.delete(bs)
        
        return len(existing_blendshapes)

    def apply_blendshapes(self):
        render_geo_namespace = self.render_geo_group.namespace_combo.currentText()
        anim_cache_namespace = self.anim_cache_group.namespace_combo.currentText()
        
        if render_geo_namespace == "Select one" or anim_cache_namespace == "Select one":
            QtWidgets.QMessageBox.warning(self, "Error", "Please select namespaces for both Render Geo and Animation Cache.")
            return
        
        results = []
        processed_render_geo = set()
        
        for render_widget, anim_widget in self.paired_widgets:
            render_geo = f"{render_geo_namespace}:{render_widget.text()}"
            if render_geo in processed_render_geo:
                continue
            anim_cache = f"{anim_cache_namespace}:{anim_widget.text()}"
            try:
                # Remove existing blendshapes
                removed_count = self.remove_existing_blendshapes(render_geo)
                
                # Create new blendshape
                blendshape_node = self.create_blendshape(render_geo, anim_cache)
                results.append(f"Success: Wrapped {render_geo} to {anim_cache} (BlendShape: {blendshape_node}). Removed {removed_count} existing blendshape(s).")
                processed_render_geo.add(render_geo)
            except Exception as e:
                error_message = f"Error: Failed to wrap {render_geo} to {anim_cache}\n{str(e)}"
                results.append(error_message)
                cmds.warning(error_message)
        
        self.show_results(results)


    def create_blendshape(self, render_geo, anim_cache):
        print(f"Creating blendshape: {render_geo} -> {anim_cache}")
        
        # Check if a blendshape already exists
        existing_blendshapes = cmds.listConnections(render_geo, type='blendShape') or []
        if existing_blendshapes:
            print(f"Found existing blendshape(s) for {render_geo}: {existing_blendshapes}")
            # If a blendshape exists, clear its targets
            for bs in existing_blendshapes:
                cmds.blendShape(bs, edit=True, remove=True, all=True)
            blendshape_node = existing_blendshapes[0]
        else:
            print(f"No existing blendshape found for {render_geo}. Creating new blendshape.")
            # Create a new blendshape if one doesn't exist
            blendshape_node = cmds.blendShape(anim_cache, render_geo, name=f"{render_geo}_blendShape", frontOfChain=True)[0]
        
        # Add or update the target
        cmds.blendShape(blendshape_node, edit=True, target=(render_geo, 0, anim_cache, 1.0))
        
        # Set the weight of the target to 1
        target_name = anim_cache.split(':')[-1]
        cmds.setAttr(f"{blendshape_node}.{target_name}", 1)

        print(f"Blendshape created/updated: {blendshape_node}")
        return blendshape_node

    def show_results(self, results):
        results_dialog = QtWidgets.QDialog(self)
        results_dialog.setWindowTitle("Blendshape Results")
        layout = QtWidgets.QVBoxLayout(results_dialog)
        
        results_text = QtWidgets.QTextEdit()
        results_text.setReadOnly(True)
        results_text.setPlainText("\n".join(results))
        layout.addWidget(results_text)
        
        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(results_dialog.accept)
        layout.addWidget(close_button)
        
        results_dialog.exec_()

if __name__ == "__main__":
    geo_dict = collect_geo_objects()
    maya_main_window = get_maya_main_window()
    dialog = BlendshapeDialog(geo_dict, maya_main_window)
    dialog.show()