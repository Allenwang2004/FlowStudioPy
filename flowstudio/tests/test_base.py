import pytest
from flowstudio.flow_window import FLOW_Window
from flowstudio.flow_license_mechanism import License_Mechanism


@pytest.fixture
def window(qtbot):
    wnd = FLOW_Window()
    wnd.resize(1100, 700)
    wnd.show()
    wnd.license_mechanism = License_Mechanism(wnd, is_testing=True)
    wnd.nodesListWidget.addMyItems()
    if wnd.isVisible():
        wnd.settingDialog.onTargetSelect()
    qtbot.addWidget(wnd)
    return wnd
