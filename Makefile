all: stellate_ui.py

stellate_ui.py: stellate.ui
	pyuic5 $< -o $@
