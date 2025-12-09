from .op_alert_path import CHECKPATH_OT_show_popup
from .handlers import ensure_alert_handlers, remove_alert_handlers
from .menu import CHECKPATH_MT_menu,  CHECKPATH_OT_fake_menu,  CHECKPATH_OT_manual_check, draw_alert_menu

# facultatif : une liste globale des classes si tu veux
def get_alert_path_classes():
    return (
        CHECKPATH_OT_show_popup, CHECKPATH_MT_menu, CHECKPATH_OT_fake_menu, CHECKPATH_OT_manual_check,
    )