#!/usr/bin/env python3

# V. 0.5.1

import os,sys,shutil,stat
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, Gio, GLib, GObject, Pango
from gi.repository import GdkPixbuf
from pathlib import Path
import json
from threading import Thread
from threading import Event
import queue
from subprocess import Popen, PIPE, CalledProcessError
import signal


_curr_dir = os.getcwd()

def _error_log(_error):
    pass
    # _now = datetime.datetime.now().strftime("%Y-%m-%d %H:%m")
    # _ff = open(os.path.join(_curr_dir, "error.log"), "a")
    # _ff.write(_now+": "+_error+"\n\n")
    # _ff.close()

_HOME = Path.home()

# _display = Gdk.Display.get_default()
# display_type = GObject.type_name(_display.__gtype__)

# is_wayland = display_type=="GdkWaylandDisplay"
# if not is_wayland:
    # _error_log("Wayland required.")
    # sys.exit()

# is_x11 = display_type=="GdkX11Display"


# other options
_other_settings_conf = None
_other_settings_config_file = os.path.join(_curr_dir,"configs","other_settings.json")
_starting_other_settings_conf = {"pad-value":4,"logout":"","shutdown":"","reboot":"","lock":"","user1":"","user2":"","rebuild":1,"wlrctl":1,"fifo":1}
if not os.path.exists(_other_settings_config_file):
    try:
        _ff = open(_other_settings_config_file,"w")
        _data_json = _starting_other_settings_conf
        json.dump(_data_json, _ff, indent = 4)
        _ff.close()
        _other_settings_conf = _starting_other_settings_conf
    except:
        _error_log("Service config file error.")
        sys.exit()
else:
    _ff = open(_other_settings_config_file, "r")
    _other_settings_conf = json.load(_ff)
    _ff.close()

USE_FIFO = 1
if USE_FIFO:
    FIFO = os.path.join(_curr_dir,'wbarmenufifo')
    # commands: __open __close __exit
    if not os.path.exists(FIFO):
        try:
            os.mkfifo(FIFO)
        except Exception as E:
            print("Error while creating the fifo; exiting...")
            sys.exit(0)

# screen = Gdk.Screen.get_default()
# provider = Gtk.CssProvider()
# provider.load_from_path(os.path.join(_curr_dir,"configs/panelstyle.css"))
# Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


_menu_conf = None
_menu_config_file = os.path.join(_curr_dir,"configs","menu.json")
# live_search: num. of chars to perform a seeking; num_items: number of items per row in the menu window; the menu editor command
_starting_menu_conf = {"wwidth":880,"wheight":600,"terminal":"",\
"cat_icon_size":64,"item_icon_size":64,"live_search":3,"num_items":3,"menu_editor":""}

if not os.path.exists(_menu_config_file):
    try:
        _ff = open(_menu_config_file,"w")
        _data_json = _starting_menu_conf
        json.dump(_data_json, _ff, indent = 4)
        _ff.close()
        _menu_conf = _starting_menu_conf
    except:
        _error_log("Menu config file error.")
        sys.exit()
else:
    _ff = open(_menu_config_file, "r")
    _menu_conf = json.load(_ff)
    _ff.close()


_menu_favorites = os.path.join(_curr_dir,"favorites")
if not os.path.exists(_menu_favorites):
    _f = open(_menu_favorites,"w")
    _f.write("\n")
    _f.close()

# check files are executable
_file_to_check_exec = ["restart.sh","poweroff.sh","menu_editor","logout.sh","wbarmenu_toggle.sh"]
for _ff in _file_to_check_exec:
    if os.path.exists(os.path.join(_curr_dir, _ff)):
        if not os.access(_ff,os.X_OK):
            st = os.stat(_ff)
            os.chmod(_ff, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def MyDialog(data1, data2, parent):
    dialog = Gtk.AlertDialog()
    dialog.set_message(data1)
    dialog.set_detail(data2)
    dialog.set_modal(True)
    dialog.set_buttons(["Close"])
    dialog.show(parent)


# qq = queue.Queue(maxsize=1)
# USER_THEME=0

# add a monitor after adding a new path
app_dirs_user = [os.path.join(os.path.expanduser("~"), ".local/share/applications")]
app_dirs_system = ["/usr/share/applications", "/usr/local/share/applications"]
#### main application categories
# Bookmarks = []
Development = []
Education = []
Game = []
Graphics = []
Multimedia = []
Network = []
Office = []
Settings = []
System = []
Utility = []
Other = []


# icon_theme = Gtk.IconTheme.get_default()
icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())

main_categories = ["Multimedia","Development","Education","Game","Graphics","Network","Office","Settings","System","Utility"]
    
# removed "Audio" e "Video" main categories
freedesktop_main_categories = ["AudioVideo","Development", 
                            "Education","Game","Graphics","Network",
                            "Office","Settings","System","Utility"]
# additional categories
development_extended_categories = ["Building","Debugger","IDE","GUIDesigner",
                            "Profiling","RevisionControl","Translation",
                            "Database","WebDevelopment"]

office_extended_categories = ["Calendar","ContanctManagement","Office",
                            "Dictionary","Chart","Email","Finance","FlowChart",
                            "PDA","ProjectManagement","Presentation","Spreadsheet",
                            "WordProcessor","Engineering"]

graphics_extended_categories = ["2DGraphics","VectorGraphics","RasterGraphics",
                            "3DGraphics","Scanning","OCR","Photography",
                            "Publishing","Viewer"]

utility_extended_categories = ["TextTools","TelephonyTools","Compression",
                            "FileTools","Calculator","Clock","TextEditor",
                            "Documentation"]

settings_extended_categories = ["DesktopSettings","HardwareSettings",
                            "Printing","PackageManager","Security",
                            "Accessibility"]

network_extended_categories = ["Dialup","InstantMessaging","Chat","IIRCClient",
                            "FileTransfer","HamRadio","News","P2P","RemoteAccess",
                            "Telephony","VideoConference","WebBrowser","Internet"]

# added "Audio" and "Video" main categories
audiovideo_extended_categories = ["Audio","Video","Midi","Mixer","Sequencer","Tuner","TV",
                            "AudioVideoEditing","Player","Recorder",
                            "DiscBurning"]

game_extended_categories = ["ActionGame","AdventureGame","ArcadeGame",
                            "BoardGame","BlockGame","CardGame","KidsGame",
                            "LogicGame","RolePlaying","Simulation","SportGame",
                            "StrategyGame","Amusement","Emulator"]

education_extended_categories = ["Art","Construction","Music","Languages",
                            "Science","ArtificialIntelligence","Astronomy",
                            "Biology","Chemistry","ComputerScience","DataVisualization",
                            "Economy","Electricity","Geography","Geology","Geoscience",
                            "History","ImageProcessing","Literature","Math","NumericAnalysis",
                            "MedicalSoftware","Physics","Robots","Sports","ParallelComputing",
                            "Electronics"]

system_extended_categories = ["FileManager","TerminalEmulator","FileSystem",
                            "Monitor","Core"]

# _categories = [freedesktop_main_categories,development_extended_categories,office_extended_categories,graphics_extended_categories,utility_extended_categories,settings_extended_categories,network_extended_categories,audiovideo_extended_categories,game_extended_categories,education_extended_categories,system_extended_categories]

def _on_find_cat(_cat):
    if not _cat:
        return "Other"
    
    ccat = _cat.split(";")
    for cccat in ccat:
        # search in the main categories first
        if cccat in freedesktop_main_categories:
            # from AudioVideo to Multimedia
            if cccat == "AudioVideo":
                return "Multimedia"
            return cccat
        elif cccat in development_extended_categories:
            return "Development"
        elif cccat in office_extended_categories:
            return "Office"
        elif cccat in graphics_extended_categories:
            return "Graphics"
        elif cccat in utility_extended_categories:
            return "Utility"
        elif cccat in settings_extended_categories:
            return "Settings"
        elif cccat in network_extended_categories:
            return "Network"
        elif cccat in audiovideo_extended_categories:
            #return "AudioVideo"
            return "Multimedia"
        elif cccat in game_extended_categories:
            return "Game"
        elif cccat in education_extended_categories:
            return "Education"
        elif cccat in system_extended_categories:
            return "System"
    
    return "Other"


the_menu = []

def _f_populate_menu():
    global the_menu
    the_menu = []
    _ap = Gio.AppInfo
    _list_apps = _ap.get_all()
    for _el in _list_apps:
        # no display
        if _el.get_nodisplay():
            continue
        # display name
        _el_name = _el.get_display_name()
        # category
        _cat_tmp = _el.get_categories()
        _el_cat = _on_find_cat(_cat_tmp)
        # executable
        _el_exec = _el.get_executable()
        # icon
        _el_icon = _el.get_icon()
        if _el_icon:
            if isinstance(_el_icon,Gio.ThemedIcon):
                _el_icon = _el_icon.to_string()
            elif isinstance(_el_icon,Gio.FileIcon):
                _el_icon = _el_icon.get_file().get_path()
        else:
            _el_icon = None
        # comment
        _el_comment = _el.get_description() or None
        _el_path = _el.get_filename()
        
        if not _el_name or not _el_exec or not _el_path:
            continue
        else:
            the_menu.append([_el_name,_el_cat,_el_exec,_el_icon,_el_comment,_el_path,_el])
            

class SignalObject(GObject.Object):
    
    def __init__(self):
        GObject.Object.__init__(self)
        self._name = ""
        self.value = -99
        self._list = []
    
    @GObject.Property(type=str)
    def propName(self):
        'Read-write integer property.'
        return self._name

    @propName.setter
    def propName(self, name):
        self._name = name
    
    @GObject.Property(type=int)
    def propInt(self):
        'Read-write integer property.'
        return self.value

    @propInt.setter
    def propInt(self, value):
        self.value = value
    
    @GObject.Property(type=object)
    def propList(self):
        'Read-write integer property.'
        return self._list

    @propList.setter
    def propList(self, data):
        self._list = [data]


# logout/reboot/shutdonw window
class commandWin(Gtk.Window):
    def __init__(self, _parent, _command):
        super().__init__()
        
        self._parent = _parent
        self._command = _command
        
        self.set_decorated(False)
        
        # self.connect('focus-out-event', self.on_focus_out)
        
        self.self_style_context = self.get_style_context()
        self.self_style_context.add_class("commandwin")
        
        _pad1 = 10
        self.main_box = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL,spacing=_pad1)
        self.main_box.set_margin_start(_pad1)
        self.main_box.set_margin_end(_pad1)
        self.set_child(self.main_box)
        
        # button box
        self.bbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.bbox.set_homogeneous(homogeneous=True)
        self.main_box.append(self.bbox)
        #
        _cancel_btn = Gtk.Button(label="Cancel")
        _cancel_btn.connect('clicked', self.on_cancel)
        self.bbox.append(_cancel_btn)
        
        c_btn = Gtk.Button.new()
        self.bbox.append(c_btn)
        
        if self._command == "logout":
            c_btn.set_label("Logout?")
            c_btn.connect('clicked',self.on_c_btn, "logout")
        elif self._command == "restart":
            c_btn.set_label("Restart?")
            c_btn.connect('clicked',self.on_c_btn, "restart")
        elif self._command == "shutdown":
            c_btn.set_label("Shutdown?")
            c_btn.connect('clicked',self.on_c_btn, "shutdown")
        elif self._command == "exit":
            c_btn.set_label("Exit?")
            c_btn.connect('clicked',self.on_c_btn, "exit")
        
        self.set_visible(True)
    
    
    def on_c_btn(self, btn, _type):
        try:
            _f = None
            if _type == "logout":
                _f = self._parent._logout
            elif _type == "restart":
                _f = self._parent._reboot
            elif _type == "shutdown":
                _f = self._parent._shutdown
            elif _type == "exit":
                self._parent._parent._to_close()
            elif _type == "lock":
                _f = self._parent._lock
            
            if _f:
                os.system(f"{_f} &")
        except:
            self.close()
        self.close()
    
    # def on_c_btn(self, btn, _type):
        # try:
            # _f = None
            # if _type == "logout":
                # _ff = os.path.join(_curr_dir, "logout.sh")
                # if os.path.exists(_ff):
                    # if not os.access(_ff,os.X_OK):
                        # os.chmod(_ff, 0o740)
                    # _f = _ff
            # elif _type == "restart":
                # _ff = os.path.join(_curr_dir, "restart.sh")
                # if os.path.exists(_ff):
                    # if not os.access(_ff,os.X_OK):
                        # os.chmod(_ff, 0o740)
                    # _f = _ff
            # elif _type == "shutdown":
                # _ff = os.path.join(_curr_dir, "poweroff.sh")
                # if os.path.exists(_ff):
                    # if not os.access(_ff,os.X_OK):
                        # os.chmod(_ff, 0o740)
                    # _f = _ff
            # elif _type == "exit":
                # self._parent._parent._to_close()
            
            # if _f:
                # os.system(f"{_f} &")
        # except:
            # self.close()
        # self.close()
    
    def on_cancel(self, btn):
        self.close()


class menuWin(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = self.get_application()   
        self.set_title("wbarmenu-1")
        self.set_icon_name(os.path.join(_curr_dir,"wicon.png"))
        #
        self.set_decorated(False)
        #
        self.connect("destroy", self._to_close)
        
        # self.connect('focus-out-event', self.on_focus_out)
        # self.connect('show', self.on_show)
        
        # self.event_controller = Gtk.EventControllerFocus.new()
        # self.event_controller.connect('leave', self.on_focus_out)
        # self.add_controller(self.event_controller)
        ####### configs
        # MENU
        self.menu_conf = _menu_conf
        self.menu_width = self.menu_conf["wwidth"]
        self.menu_width_tmp = 0
        self.menu_height = self.menu_conf["wheight"]
        self.menu_height_tmp = 0
        self.menu_terminal = self.menu_conf["terminal"]
        self.menu_terminal_tmp = None
        self.menu_cat_icon_size = self.menu_conf["cat_icon_size"]
        self.menu_cat_icon_size_tmp = 0
        self.menu_item_icon_size = self.menu_conf["item_icon_size"]
        self.menu_item_icon_size_tmp = 0
        self.menu_live_search = self.menu_conf["live_search"]
        self.menu_live_search_tmp = None
        self.menu_n_items = self.menu_conf["num_items"]
        self.menu_n_items_tmp = None
        self.menu_editor = self.menu_conf["menu_editor"]
        self.menu_editor_tmp = None
        # OTHERS
        self.other_settings_conf = _other_settings_conf
        self._pad = self.other_settings_conf["pad-value"]
        self._pad_tmp = None
        self._logout = self.other_settings_conf["logout"]
        self._logout_tmp = None
        self._shutdown = self.other_settings_conf["shutdown"]
        self._shutdown_tmp = None
        self._reboot = self.other_settings_conf["reboot"]
        self._reboot_tmp = None
        self._lock = self.other_settings_conf["lock"]
        self._lock_tmp = None
        self._user1 = self.other_settings_conf["user1"]
        self._user1_tmp = None
        self._user2 = self.other_settings_conf["user2"]
        self._user2_tmp = None
        self._rebuild = self.other_settings_conf["rebuild"]
        self._rebuild_tmp = None
        self._use_wlrctl = self.other_settings_conf["wlrctl"]
        self._use_wlrctl_tmp = None
        self._use_fifo = self.other_settings_conf["fifo"]
        self._use_fifo_tmp = None
        # 
        # if self._use_wlrctl == 1:
            # self._use_fifo = 0
        #
        if not shutil.which("wlrctl"):
            self._use_fifo = 1
        ####### end configs
        
        self.set_size_request(self.menu_width, self.menu_height)
        
        self.list_elements = []
        
        self.main_box = Gtk.Box.new(1,0)
        self.main_box.set_margin_start(self._pad)
        self.main_box.set_margin_end(self._pad)
        self.set_child(self.main_box)
        
        self.self_style_context = self.get_style_context()
        self.self_style_context.add_class("menuwin")
        
        ###############
        self.BTN_ICON_SIZE = self.menu_cat_icon_size
        self.ICON_SIZE = self.menu_item_icon_size
        
        # category box
        self.cbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.cbox.set_homogeneous(True)
        self.main_box.append(self.cbox)
        
        # # separator
        # separator = Gtk.Separator()
        # separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        # self.main_box.pack_start(separator, False, False, 4)
        
        # iconview
        self.ivbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.ivbox.set_homogeneous(True)
        self.ivbox.set_hexpand(True)
        self.ivbox.set_vexpand(True)
        self.main_box.append(self.ivbox)
        
        # scrolled window
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)
        self.scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolledwindow.set_placement(Gtk.CornerType.TOP_LEFT)
        self.ivbox.append(self.scrolledwindow)
        
        ##############
        self.iconview = Gtk.FlowBox()
        self.iconview.set_activate_on_single_click(True)
        self.iconview.set_selection_mode(0)
        self.iconview.set_homogeneous(True)
        self.iconview.set_max_children_per_line(self.menu_n_items)
        self.iconview.set_min_children_per_line(self.menu_n_items)
        self.scrolledwindow.set_child(self.iconview)
        self.iconview.connect('child-activated', self.on_iv_item_activated)
        #
        self.gesture_iv = Gtk.GestureClick.new()
        self.gesture_iv.set_button(3)
        self.iconview.add_controller(self.gesture_iv)
        self.gesture_iv.connect('pressed', self.on_iv_gesture)
        
        # when bookmark items reordering start
        self.is_dragging = 0
        
        drop_controller = Gtk.DropTarget.new(
            type=GObject.TYPE_NONE, actions=Gdk.DragAction.COPY
        )
        drop_controller.set_gtypes([str])
        drop_controller.connect('drop', self.on_drop)
        self.iconview.add_controller(drop_controller)
        
        ##############
        # separator
        separator = Gtk.Separator()
        separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        # self.main_box.pack_start(separator, False, False, 4)
        self.main_box.append(separator)
        
        ### SEARCH BAR
        self.search_bar = Gtk.SearchBar()
        self.search_bar.set_search_mode(True)
        self.searchentry = Gtk.SearchEntry()
        # self.searchentry.connect('icon-press', self.on_icon_press)
        self.searchentry.set_name("mysearchentry")
        # if self._parent.menu_live_search > 2 :
            # 'search'?
        self.searchentry.connect('search-changed', self.on_search)
        # else:
        self.searchentry.connect('activate', self.on_search_return)
        # self.search_bar.connect_entry(self.searchentry)
        self.searchentry.props.hexpand = True
        self.search_bar.set_child(self.searchentry)
        self.search_bar.set_show_close_button(False)
        self.search_bar.set_visible(True)
        self.search_bar.set_search_mode(True)
        self.main_box.append(self.search_bar)
        
        # # separator
        # separator = Gtk.Separator()
        # separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        # self.main_box.append(separator)
        
        # service buttons
        self.btn_box = Gtk.Box.new(0,0)
        self.btn_box.set_hexpand(True)
        # self.btn_box.props.halign = 2
        self.main_box.append(self.btn_box)
        
        ## configurator button
        self.conf_btn = Gtk.Button()
        self.conf_btn.set_tooltip_text("Configurator")
        self.conf_btn.connect('clicked', self.on_button_conf_clicked)
        pix = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(_curr_dir,"icons","settings.png"), int(self.BTN_ICON_SIZE/2), int(self.BTN_ICON_SIZE/2))
        _pb = Gdk.Texture.new_for_pixbuf(pix)
        _image = Gtk.Image.new_from_paintable(_pb)
        _image.set_pixel_size(int(self.BTN_ICON_SIZE/2))
        self.conf_btn.set_child(_image)
        self.btn_box.append(self.conf_btn)
        
        ## menu editor button
        if self.menu_editor:
            self.modify_menu_btn = Gtk.Button()
            self.modify_menu_btn.set_tooltip_text("Modify the menu")
            self.modify_menu_btn.connect('clicked', self.on_modify_menu)
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(_curr_dir,"icons","modify_menu.svg"), int(self.BTN_ICON_SIZE/2), int(self.BTN_ICON_SIZE/2))
            _pb = Gdk.Texture.new_for_pixbuf(pix)
            _image = Gtk.Image.new_from_paintable(_pb)
            _image.set_pixel_size(int(self.BTN_ICON_SIZE/2))
            self.modify_menu_btn.set_child(_image)
            self.btn_box.append(self.modify_menu_btn)
            # self.modify_menu_btn.set_halign(1)
        
        ## manual rebuild menu button
        if self._rebuild == 0:
            self.rebuild_menu_btn = Gtk.Button()
            self.rebuild_menu_btn.set_tooltip_text("Rebuild the menu")
            self.rebuild_menu_btn.connect('clicked', self.rebuild_menu)
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(_curr_dir,"icons","rebuild_menu.png"), int(self.BTN_ICON_SIZE/2), int(self.BTN_ICON_SIZE/2))
            _pb = Gdk.Texture.new_for_pixbuf(pix)
            _image = Gtk.Image.new_from_paintable(_pb)
            _image.set_pixel_size(int(self.BTN_ICON_SIZE/2))
            self.rebuild_menu_btn.set_child(_image)
            self.btn_box.append(self.rebuild_menu_btn)
            # self.rebuild_menu_btn.set_halign(1)
        
        # separator
        separator = Gtk.Separator()
        separator.set_orientation(Gtk.Orientation.VERTICAL)
        separator.set_hexpand(True)
        self.btn_box.append(separator)
        
        if self._logout:
            self.logout_btn = Gtk.Button()
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(_curr_dir,"icons","system-logout.svg"), int(self.BTN_ICON_SIZE/2), int(self.BTN_ICON_SIZE/2))
            _pb = Gdk.Texture.new_for_pixbuf(pix)
            _image = Gtk.Image.new_from_paintable(_pb)
            _image.set_pixel_size(int(self.BTN_ICON_SIZE/2))
            self.logout_btn.set_child(_image)
            self.logout_btn.set_tooltip_text("Logout")
            self.logout_btn.connect('clicked', self.on_service_btn, "logout")
            self.btn_box.append(self.logout_btn)
        
        if self._reboot:
            self.reboot_btn = Gtk.Button()
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(_curr_dir,"icons","system-restart.svg"), int(self.BTN_ICON_SIZE/2), int(self.BTN_ICON_SIZE/2))
            _pb = Gdk.Texture.new_for_pixbuf(pix)
            _image = Gtk.Image.new_from_paintable(_pb)
            _image.set_pixel_size(int(self.BTN_ICON_SIZE/2))
            self.reboot_btn.set_child(_image)
            self.reboot_btn.set_tooltip_text("Restart")
            self.reboot_btn.connect('clicked', self.on_service_btn, "restart")
            self.btn_box.append(self.reboot_btn)
        
        if self._shutdown:
            self.shutdown_btn = Gtk.Button()
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(_curr_dir,"icons","system-shutdown.svg"), int(self.BTN_ICON_SIZE/2), int(self.BTN_ICON_SIZE/2))
            _pb = Gdk.Texture.new_for_pixbuf(pix)
            _image = Gtk.Image.new_from_paintable(_pb)
            _image.set_pixel_size(int(self.BTN_ICON_SIZE/2))
            self.shutdown_btn.set_child(_image)
            self.shutdown_btn.set_tooltip_text("Shutdown")
            self.shutdown_btn.connect('clicked', self.on_service_btn, "shutdown")
            self.btn_box.append(self.shutdown_btn)
        
        # the bookmark button
        self.btn_bookmark = None
        # the last category button pressed
        self._btn_toggled = None
        # populate the menu
        self.on_populate_menu()
        # populate categories
        self.bookmarks = []
        self.set_categories()
        # # this window
        # self.MW = None
        ###########
        self.connect("close-request", self.on_menu_close)
        ###########
        self.connect("hide", self.on_hide)
        self.set_visible(True)
        #
        ## menu rebuild
        if self._rebuild == 1:
            self.q = queue.Queue(maxsize=1)
            gdir1 = Gio.File.new_for_path(os.path.join(_HOME, ".local/share/applications"))
            self.monitor1 = gdir1.monitor_directory(Gio.FileMonitorFlags.SEND_MOVED, None)
            self.monitor1.connect("changed", self.directory_changed)
            gdir2 = Gio.File.new_for_path("/usr/share/applications")
            self.monitor2 = gdir2.monitor_directory(Gio.FileMonitorFlags.SEND_MOVED, None)
            self.monitor2.connect("changed", self.directory_changed)
            gdir3 = Gio.File.new_for_path("/usr/local/share/applications")
            self.monitor3 = gdir3.monitor_directory(Gio.FileMonitorFlags.SEND_MOVED, None)
            self.monitor3.connect("changed", self.directory_changed)
        #
        # fifo thread
        self.event = Event()
        if USE_FIFO and self._use_fifo:
            self.thread_fifo = Thread(target=appThread, args=(self,self.event))
            self.thread_fifo.start()
    
    def directory_changed(self, monitor, file1, file2, event):
        if (event == Gio.FileMonitorEvent.CREATED):
            self.on_directory_changed(file1.get_path(), "created")
        elif (event == Gio.FileMonitorEvent.DELETED):
            self.on_directory_changed(file1.get_path(), "deleted")

    def on_directory_changed(self, _path, _type):
        try:
            if self.q.empty():
                self.q.put("new", timeout=0.001)
        except:
            pass
        #
        if not self.q.empty():
            # if self.MW:
                # self.MW.close()
                # self.MW = None
            #
            self.set_sensitive(False)
            #
            _bookmarks = None
            with open(os.path.join(_curr_dir, "favorites"), "r") as _f:
                _bookmarks = _f.readlines()
            #
            if _type == "deleted":
                for el in _bookmarks[:]:
                    if el.strip("\n") == _path:
                        _bookmarks.remove(el)
                        break
            #
            with open(os.path.join(_curr_dir, "favorites"), "w") as _f:
                for el in _bookmarks:
                    _f.write(el)
            #
            self.rebuild_menu()
            #
            self.set_sensitive(True)
            #
            # reset the view
            self.on_hide(None)
    
    def open_close(self, _action):
        if _action == "toggle":
            if not self._use_wlrctl:
                self.set_visible(not self.get_visible())
                # if self.get_visible():
                    # self.set_visible(False)
                    # #self.minimize()
                # else:
                    # self.set_visible(True)
                    # #self.unminimize()
            else:
                try:
                    os.system("{} &".format(os.path.join(_curr_dir,"wbarmenu_toggle.sh")))
                except:
                    pass
        # reset the view
        self.on_hide(None)
    
    ### menu w h ci ii ls
    def set_menu_cp(self, _type, _value):
        if _type == "w":
            self.menu_width_tmp = _value
        elif _type == "h":
            self.menu_height_tmp = _value
        elif _type == "ci":
           self.menu_cat_icon_size_tmp  = _value
        elif _type == "ii":
            self.menu_item_icon_size_tmp = _value
        elif _type == "ls":
            self.menu_live_search_tmp = _value
        elif _type == "n_item":
            self.menu_n_items_tmp = _value
    
    def on_menu_editor(self, _text):
        self.menu_editor_tmp = _text
    
    def on_term(self, _text):
        self.menu_terminal_tmp = _text
    
    def on_command(self, _text, _type):
        if _type == "logout":
            self._logout_tmp = _text
        elif _type == "shutdown":
            self._shutdown_tmp = _text
        elif _type == "reboot":
            self._reboot_tmp = _text
    
    def on_menu_rebuild(self, _n):
        self._rebuild_tmp = _n
    
    def on_wlrctl(self, _n):
        self._use_wlrctl_tmp = _n
        
    def on_fifo(self, _n):
        self._use_fifo_tmp = _n
    
    def on_button_conf_clicked(self, widget):
        self.open_close("toggle")
        dialog = DialogConfiguration(self)
        dialog.connect("response", self.on_dialog_response)
    
    def on_dialog_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            # # menu
            # if self.MW:
                # self.MW.close()
                # self.MW = None
            # # service
            # if self.OW:
                # self.OW.close()
                # self.OW = None
            
            ## MENU
            if self.menu_width_tmp != 0:
                self.menu_width = self.menu_width_tmp
                self.menu_conf["wwidth"] = self.menu_width
                self.menu_width_tmp = 0
            if self.menu_height_tmp != 0:
                self.menu_height = self.menu_height_tmp
                self.menu_conf["wheight"] = self.menu_height
                self.menu_height_tmp = 0
            if self.menu_terminal_tmp != None:
                self.menu_terminal = self.menu_terminal_tmp
                self.menu_conf["terminal"] = self.menu_terminal
                self.menu_terminal_tmp = None
            if self.menu_cat_icon_size_tmp != 0:
                self.menu_cat_icon_size = self.menu_cat_icon_size_tmp
                self.menu_conf["cat_icon_size"] = self.menu_cat_icon_size
                self.menu_cat_icon_size_tmp = 0
            if self.menu_item_icon_size_tmp != 0:
                self.menu_item_icon_size = self.menu_item_icon_size_tmp
                self.menu_conf["item_icon_size"] = self.menu_item_icon_size
                self.menu_item_icon_size_tmp = 0
            if self.menu_live_search_tmp != None:
                self.menu_live_search = self.menu_live_search_tmp
                self.menu_conf["live_search"] = self.menu_live_search
                self.menu_live_search_tmp = None
            if self.menu_n_items_tmp != None:
                self.menu_n_items = self.menu_n_items_tmp
                self.menu_conf["num_items"] = self.menu_n_items
                self.menu_n_items_tmp = None
            if self.menu_editor_tmp != None:
                self.menu_editor = self.menu_editor_tmp
                self.menu_conf["menu_editor"] = self.menu_editor_tmp
                self.menu_editor_tmp = None
            ## OTHERS
            if self._logout_tmp != None:
                self._logout = self._logout_tmp
                self.other_settings_conf["logout"] = self._logout_tmp
                self._logout_tmp = None
            if self._shutdown_tmp != None:
                self._shutdown = self._shutdown_tmp
                self.other_settings_conf["shutdown"] = self._shutdown_tmp
                self._shutdown_tmp = None
            if self._reboot_tmp != None:
                self._reboot = self._reboot_tmp
                self.other_settings_conf["reboot"] = self._reboot_tmp
                self._reboot_tmp = None
            if self._rebuild_tmp != None:
                self._rebuild = self._rebuild_tmp
                self.other_settings_conf["rebuild"] = self._rebuild_tmp
                self._rebuild_tmp = None
            if self._use_wlrctl_tmp != None:
                self._use_wlrctl = self._use_wlrctl_tmp
                self.other_settings_conf["wlrctl"] = self._use_wlrctl_tmp
                self._use_wlrctl_tmp = None
            if self._use_fifo_tmp != None:
                self._use_fifo = self._use_fifo_tmp
                self.other_settings_conf["fifo"] = self._use_fifo_tmp
                self._use_fifo_tmp = None
            
            # self.on_save_optional_widget_state()
            self.save_conf()
        # elif response == Gtk.ResponseType.CANCEL:
        else:
            self.on_close_dialog_conf()
        dialog.destroy()
    
    def on_close_dialog_conf(self):
        self.menu_width_tmp = 0
        self.menu_height_tmp = 0
        self.menu_terminal_tmp = None
        self.menu_cat_icon_size_tmp = 0
        self.menu_item_icon_size_tmp = 0
        self.menu_live_search_tmp = None
        self.menu_n_items_tmp = None
        self.menu_editor_tmp = None
        #
        self._logout_tmp = None
        self._shutdown_tmp = None
        self._reboot_tmp = None
        self._rebuild_tmp = None
        self._use_wlrctl_tmp = None
        self._use_fifo_tmp = None
    
    def save_conf(self):
        # menu
        _ff = open(_menu_config_file, "w")  
        json.dump(self.menu_conf, _ff, indent = 4)  
        _ff.close()
        # others
        _ff = open(_other_settings_config_file, "w")  
        json.dump(self.other_settings_conf, _ff, indent = 4)  
        _ff.close()
    
    def _to_close(self, w=None, e=None):
        self.event.set()
        self._app.quit()
        
    def on_hide(self, widget):
        self.empty_iconview()
        if self._btn_toggled:
            self._btn_toggled.set_active(False)
        self._btn_toggled = self.btn_bookmark
        self.populate_bookmarks()
        self._btn_toggled.set_active(True)
        self.searchentry.set_text("")
    
    def empty_iconview(self):
        try:
            self.iconview.remove_all()
            self.list_elements = []
        except:
            try:
                for el in self.list_elements:
                    self.iconview.remove(el)
                self.list_elements = []
            except:
                pass
    
    # value is the path of the dragged item
    def on_drop(self, _ctrl, value, _x, _y):
        self.is_dragging = 0
        if value == None:
            return
        if isinstance(value, str):
            # _w is flowbox or image or label
            _w = self.iconview.pick(_x,_y,0)
            # the path in self.bookmarks to substitute with value
            _found = None
            if isinstance(_w, Gtk.Image):
                for el in self.list_elements:
                    if _w in el:
                        _found = el._path
                        break
            elif isinstance(_w, Gtk.FlowBox):
                _found = "__flowbox"
            
            if _found == value:
                return
            
            if _found != None:
                if _found != "__flowbox":
                    item = _found
                    self.bookmarks.remove(value)
                    idx = self.bookmarks.index(item)
                    self.bookmarks.insert(idx+1, value)
                elif _found == "__flowbox":
                    self.bookmarks.remove(value)
                    self.bookmarks.append(value)
                try:
                    with open(_menu_favorites, "w") as _f:
                        for el in self.bookmarks:
                            _f.write(el+"\n")
                    # emptry the iconview
                    self.empty_iconview()
                    # rebuild bookmarks
                    self.populate_bookmarks_at_start()
                    self.populate_category("Bookmarks")
                except Exception as E:
                    self.msg_simple("Error\n"+str(E))
    
    def on_menu_close(self, w):
        pass
        # if self.MW:
            # self.MW.close()
            # self.MW = None
    
    def on_iv_gesture(self, _p,_n,x,y):
        iv = _p.get_widget()
        _child = iv.get_child_at_pos(x,y).get_child()
        _item = _child._path
        # self.set_visible(False)
        # return
        if _item != None:
            # remove from bookmarks
            if _item in self.bookmarks:
                if self._btn_toggled.icat != "Bookmarks":
                    return
                self.open_close("toggle")
                dialog = ynDialog(self, "Delete from Bookmarks?", "Question")
                dialog.connect('response', self.on_yndialog_response, 0, _item)
            # add to bookmarks
            else:
                self.open_close("toggle")
                dialog = ynDialog(self, "Add to Bookmarks?", "Question")
                dialog.connect('response', self.on_yndialog_response, 1, _item)
    
    def on_yndialog_response(self, dialog, response_id, _type, _item):
        # delete the bookmark
        if _type == 0:
            if response_id == Gtk.ResponseType.OK:
                _content = None
                try:
                    self.bookmarks.remove(_item)
                    with open(_menu_favorites, "w") as _f:
                        for el in self.bookmarks:
                            _f.write(el+"\n")
                    # rebuild bookmarks
                    self.populate_bookmarks_at_start()
                    self.populate_category("Bookmarks")
                except Exception as E:
                    self.msg_simple("Error\n"+str(E))
            #
            dialog.destroy()
            # self.MW = None
            # self.close()
        # add the bookmark
        elif _type == 1:
            if response_id == Gtk.ResponseType.OK:
                _content = None
                try:
                    with open(_menu_favorites, "a") as _f:
                        _f.write(_item)
                        _f.write("\n")
                    self.bookmarks.append(_item)
                    # rebuild bookmarks
                    self.populate_bookmarks_at_start()
                    self.populate_category("Bookmarks")
                except Exception as E:
                    self.msg_simple("Error\n"+str(E))
            dialog.destroy()
            # self.MW = None
            # self.close()
        # # rebuild the menu
        # elif _type == 2:
            # if response_id == Gtk.ResponseType.OK:
                # self.rebuild_menu()
            # dialog.destroy()
            # self.MW = None
            # self.close()
    
    def on_modify_menu(self, btn):
        if not shutil.which(self.menu_editor):
            self.msg_simple("Error\n"+"Menu editor not found:\n{}".format(self.menu_editor))
            self.on_focus_out(None)
            return
        try:
            Popen(self.menu_editor, shell=True)
        except Exception as E:
            self.msg_simple("Error\n"+str(E))
        self.on_focus_out(None)
    
    def on_service_btn(self, btn, _type):
        try:
            commandWin(self,_type)
            self.open_close("toggle")
        except:
            pass
    
    def on_populate_menu(self):
        _f_populate_menu()
    
    def rebuild_menu(self, btn=None):
        if btn != None:
            self.open_close("toggle")
            dialog = ynDialog(self, "Rebuild the menu?", "Question")
            dialog.connect('response', self.on_yndialog_menu)
            return
        #
        # if self.MW:
            # self.MW.close()
            # self.MW = None
        _f_populate_menu()
    
    def on_yndialog_menu(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            # self.open_close("toggle")
            _f_populate_menu()
        # elif response_id == Gtk.ResponseType.CANCEL:
            # self.open_close("toggle")
        #
        dialog.destroy()
        # self.MW = None
        # self.close()
        # self.open_close("toggle")
    
    # # clear icon pressed in the search entry
    # def on_icon_press(self, w, p, e):
        # if self._btn_toggled.icat == "Bookmarks":
            # self.empty_iconview()
            # self.populate_bookmarks()
    
    # application searching by pressing enter in the search entry
    def on_search_return(self, widget, _text=None):
        _text = self.searchentry.get_text().lower()
        self.on_on_searching(_text)
        
    # application live searching in the search entry
    def on_search(self, widget, _text=None):
        # wheather not live searching
        if self.menu_live_search < 3:
            if self.searchentry.get_text() == "":
                self.empty_iconview()
                self._btn_toggled = self.btn_bookmark
                self.populate_bookmarks()
                self._btn_toggled.set_active(True)
                return
            return
        _text = self.searchentry.get_text().lower()
        self.on_on_searching(_text)
    
    def on_on_searching(self, _text):
        _n_chars_search = max(3, self.menu_live_search)
        if len(_text) == 0:
            self.empty_iconview()
            self._btn_toggled = self.btn_bookmark
            self.populate_bookmarks()
            self._btn_toggled.set_active(True)
            return
        if len(_text) < _n_chars_search:
            return
        else:
            if self._btn_toggled:
                # if USER_THEME == 0:
                self._btn_toggled.set_active(False)
                self._btn_toggled = None
            self.perform_searching(_text)
    
    def perform_searching(self, _text):
        # # not used
        # if USER_THEME == 1 and USE_LABEL_CATEGORY == 1:
            # self.clabel.set_label("Searching...")
        _cat = ["Development", "Game", "Education", "Graphics", "Multimedia", "Network", "Office", "Utility", "Settings", "System", "Other"]
        _list = []
        # [_el_name,_el_cat,_el_exec,_el_icon,_el_comment,_el_path,_el])
        for _el in the_menu:
            if _el[4]:
                if _text in _el[4].lower():
                    _list.append(_el[5])
                    continue
            if _el[0]:
                if _text in _el[0].lower():
                    if not _text in _list:
                        _list.append(_el[5])
                        continue
            if _el[2]:
                if _text in _el[2].lower():
                    if not _text in _list:
                        _list.append(_el[5])
                        continue
        if _list:
            self.f_on_pop_iv(_list)
    
    def f_on_pop_iv(self, _list):
        self.empty_iconview()
        for _item in _list:
            self.f_menu_item(_item)
        
    # populate the main categories at start
    def set_categories(self):
        self._btn_toggled = None
        #
        _cat = ["Bookmarks", "Development", "Game", "Education", "Graphics", "Multimedia", "Network", "Office", "Utility", "Settings", "System", "Other"]
        _icon = ["Bookmark.svg", "Development.svg", "Game.svg", "Education.svg", "Graphics.svg", "Multimedia.svg", "Network.svg", "Office.svg", "Utility.svg", "Settings.svg", "System.svg", "Other.svg",]
        for i,el in enumerate(_cat):
            # # not used
            # if USER_THEME == 1:
                # _btn = Gtk.Button()
                # _btn.connect('clicked', self.on_toggle_toggled)
                # _btn.connect('focus-in-event', self.on_toggle_toggled)
            # elif USER_THEME == 0:
            _btn = Gtk.ToggleButton()
            _btn.set_can_focus(False)
            _btn.connect('clicked', self.on_toggle_toggled)
            _btn.set_name("mybutton")
            _btn.icat = el
            _btn.set_tooltip_text(el)
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size("icons"+"/"+_icon[i], self.BTN_ICON_SIZE, self.BTN_ICON_SIZE)
            _pb = Gdk.Texture.new_for_pixbuf(pix)
            _image = Gtk.Image.new_from_paintable(_pb)
            _image.set_pixel_size(self.BTN_ICON_SIZE)
            _btn.set_child(_image)
            self.cbox.append(_btn)
            #
            if i == 0:
                # if USER_THEME == 0:
                _btn.set_active(True)
                self._btn_toggled = _btn
                self.btn_bookmark = _btn
                self.populate_bookmarks_at_start()
                self.populate_category(el)
                # if USER_THEME == 1 and USE_LABEL_CATEGORY == 1:
                    # self.clabel.set_label("Bookmarks")
    
    def on_toggle_toggled(self, btn, e=None):
        self.searchentry.set_text("")
        
        if btn == self._btn_toggled:
            btn.set_active(True)
            return
        
        # emptry the iconview
        self.empty_iconview()
        
        # self.searchentry.delete_text(0,-1)
        # if btn.icat != "Bookmarks":
            # self.search_bar.set_visible(False)
        # else:
            # self.search_bar.set_visible(True)
        
        self.scrolledwindow.get_vadjustment().set_value(0)
        # if USER_THEME == 1:
            # self.populate_category(btn.icat)
            # self._btn_toggled = btn
            # if USE_LABEL_CATEGORY == 1:
                # self.clabel.set_label(btn.icat)
            # return
        if self._btn_toggled:
            if btn == self._btn_toggled:
                if e:
                    if e.button == 1:
                        btn.clicked()
                    else:
                        btn.set_active(True)
                return
            else:
                self._btn_toggled.set_active(False)
                if e and e.button != 1:
                    btn.set_active(True)
        #
        self.populate_category(btn.icat)
        self._btn_toggled = btn
    
    def populate_bookmarks_at_start(self):
        _content = None
        with open(_menu_favorites, "r") as _f:
            _content = _f.readlines()
        not_found = 0
        self.bookmarks = []
        for el in _content:
            if el == "\n" or el == "" or el == None:
                continue
            if not os.path.exists(el.strip("\n")):
                not_found +=1
                continue
            self.bookmarks.append(el.strip("\n"))
        if not_found:
            try:
                _f = open(_menu_favorites, "w")
                for el in self.bookmarks:
                    _f.write(el+"\n")
                _f.close()
            except Exception as E:
                self.msg_simple("Error\n"+str(E))
        #
        # self.populate_bookmarks()
    
    def populate_bookmarks(self):
        for eel in self.bookmarks:
            self.f_menu_item(eel)
    
    def on_drag_prepare(self, _ctrl, _x, _y):
        self.is_dragging = 1
        value = None
        _w = _ctrl.get_widget()
        if isinstance(_w, Gtk.Image):
            for el in self.list_elements:
                if _w in el:
                    value = el._path
                    break
        return Gdk.ContentProvider.new_for_value(value)
    
    def on_drag_begin(self, ctrl, _drag):
        icon = Gtk.WidgetPaintable.new(ctrl.get_widget())
        _xpad = max(0,int(ctrl.get_widget().get_width()-self.ICON_SIZE)/2)
        ctrl.set_icon(icon, 0+_xpad-4, -4)
    
    def f_menu_item(self, _item):
        try:
            _ap = Gio.DesktopAppInfo.new_from_filename(_item)
            _name = _ap.get_display_name()
            # executable
            _exec = _ap.get_executable()
            # comment
            _description = _ap.get_description() or None
            _path = _ap.get_filename()
            
            if not _name or not _exec or not _path:
                return
            
            _icon = _ap.get_icon()
            if _icon:
                if isinstance(_icon,Gio.ThemedIcon):
                    _icon = _icon.to_string()
                elif isinstance(_icon,Gio.FileIcon):
                    _icon = _icon.get_file().get_path()
            else:
                _icon = None
            
            pixbuf = None
            if _icon != None:
                _i = self._find_the_icon(_icon)
            _b = Gtk.Box.new(1,0)
            _b.set_tooltip_text(_description)
            if _i != None:
                _i.set_pixel_size(self.ICON_SIZE)
                _b.append(_i)
                drag_controller = Gtk.DragSource()
                drag_controller.connect('prepare', self.on_drag_prepare)
                drag_controller.connect('drag-begin', self.on_drag_begin)
                _i.add_controller(drag_controller)
            _l = Gtk.Label(label=_name)
            _l.set_wrap(True)
            _l.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            _l.set_xalign(0.5)
            _l.set_justify(Gtk.Justification.CENTER)
            _b.append(_l)
            _b._description = _description
            _b._exec = _exec
            _b._path = _path
            _b._ap = _ap
            self.iconview.append(_b)
            self.list_elements.append(_b)
        except:
            return
        
    def populate_category(self, cat_name):
        self.on_populate_category_main(cat_name)
    
    def on_populate_category_main(self, cat_name):
        if cat_name == "Bookmarks":
            for _item in self.bookmarks:
                self.f_menu_item(_item)
                # self.iconview.unselect_all()
            return
        
        for el in the_menu:
            if el[1] == cat_name:
                _i = self._find_the_icon(el[3])
                _b = Gtk.Box.new(1,0)
                if _i != None:
                    _i.set_pixel_size(self.ICON_SIZE)
                    _b.append(_i)
                _l = Gtk.Label(label=el[0])
                _l.set_wrap(True)
                _l.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
                _l.set_xalign(0.5)
                _l.set_justify(Gtk.Justification.CENTER)
                _b.append(_l)
                _b._description = el[4]
                _b._exec = el[3]
                _b._path = el[5]
                _b._ap = el[6]
                _b.set_tooltip_text(el[4])
                self.iconview.append(_b)
                self.list_elements.append(_b)
    
    def _find_the_icon(self,_icon):
        _i = None
        try:
            if os.path.exists(_icon):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(_icon, self.ICON_SIZE, self.ICON_SIZE, True)
                _pb = Gdk.Texture.new_for_pixbuf(pixbuf)
                _i = Gtk.Image.new_from_paintable(_pb)
        except:
            pass
        #
        if _i == None:
            try:
                pixbuf = icon_theme.lookup_icon(_icon, None, self.ICON_SIZE, 1, Gtk.TextDirection.NONE, Gtk.IconLookupFlags.FORCE_REGULAR)
                _i = Gtk.Image.new_from_paintable(pixbuf)
            except:
                pass
        return _i
    
    # launch a program
    def on_iv_item_activated(self, iconview, widget):
        #
        # _b._description = _description
        # _b._exec = _exec
        # _b._path = _path
        # _b._ap = _ap
        #
        _b = widget.get_child()
        app_to_exec = _b._ap
        #
        os.chdir(_HOME)
        ret=app_to_exec.launch()
        os.chdir(_curr_dir)
        if ret == False:
            _exec_name = _b._exec
            self.msg_simple(f"{_exec_name} not found or not setted.")
        self.on_focus_out(None)
    
    def sigtype_handler(self, sig, frame):
        if sig == signal.SIGINT or sig == signal.SIGTERM:
            self._to_close()
    
    # only yes message dialog
    def msg_simple(self, mmessage):
        messagedialog2 = Gtk.MessageDialog(parent=self,
                              modal=True,
                              message_type=Gtk.MessageType.WARNING,
                              buttons=Gtk.ButtonsType.OK,
                              text=mmessage)
        messagedialog2.connect("response", self.dialog_response2)
        messagedialog2.set_visible(True)
    
    def dialog_response2(self, messagedialog2, response_id):
        if response_id == Gtk.ResponseType.OK:
            messagedialog2.destroy()
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            messagedialog2.destroy()
    
    def on_conf_btn(self, btn):
        pass
    
    def on_focus_out(self, event):
        if not self.is_visible():
            # self.event_controller.reset()
            return
        # disabled when bookmarks items are been reordered
        if self.is_dragging:
            return
        self.iconview.unselect_all()
        # open bookmarks next time
        # if self._btn_toggled != self.btn_bookmark:
            # self.btn_bookmark.set_active(True)
            # self.on_toggle_toggled(self.btn_bookmark, None)
        # self.set_visible(False)
        # self.event_controller.reset()
        #
        # if USER_THEME == 0:
        if self._btn_toggled == self.btn_bookmark:
            # self.set_visible(False)
            self.open_close("toggle")
            # self.event_controller.reset()
            return
        self.btn_bookmark.set_active(True)
        self.on_toggle_toggled(self.btn_bookmark, None)
        # elif USER_THEME == 1:
            # self._btn_toggled = self.btn_bookmark
            # self.btn_bookmark.clicked()
            # self.btn_bookmark.grab_focus()
            # if USE_LABEL_CATEGORY == 1:
                # self.clabel.set_label("Bookmarks")
        #
        #self.set_visible(False)
        self.open_close("toggle")
        # self.event_controller.reset()
        
    # def on_show(self, widget):
        # pass


class appThread(Thread):
    
    def __init__(self, win, event):
        self.win = win
        self.event = event
        self.run()
    
    def run(self):
        is_true = 1
        if is_true == 0:
            return
        #
        if self.event.is_set():
            return
        #
        while not self.event.is_set():
            with open(FIFO) as fifo:
                for line in fifo:
                    if line.strip() == "__toggle":
                        self.win.open_close("toggle")
                    # elif line.strip() == "__open":
                        # self.win.open_close("open")
                    # elif line.strip() == "__close":
                        # self.win.open_close("close")
                    elif line.strip() == "__exit":
                        self.event.set()
        else:
            os.kill(os.getpid(), signal.SIGTERM)


class ynDialog(Gtk.Dialog):
    def __init__(self, parent, _title1, _type):
        super().__init__(title=_type, transient_for=parent)
        
        self.add_buttons("OK", Gtk.ResponseType.OK, "Cancel", Gtk.ResponseType.CANCEL)
        self.set_name("Info")
        # self.set_default_size(150, 100)
        label = Gtk.Label(label=_title1)
        box = self.get_child()
        box.append(label)
        self.set_visible(True)


class infoDialog(Gtk.Dialog):
    def __init__(self, parent, _title1, _type):
        super().__init__(title=_type, transient_for=parent)
        
        self.add_buttons(" Close ", Gtk.ResponseType.OK)
        self.set_name("Info")
        # self.set_default_size(150, 100)
        label = Gtk.Label(label=_title1)
        box = self.get_child()
        box.append(label)
        self.set_visible(True)


class DialogConfiguration(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Settings", transient_for=None)
        
        self.add_buttons("OK", Gtk.ResponseType.OK, "Cancel", Gtk.ResponseType.CANCEL)
        self.set_icon_name(os.path.join(_curr_dir,"configurator.svg"))
        
        self._parent = parent
        
        self.set_default_size(100, 100)
        
        self.self_style_context = self.get_style_context()
        self.self_style_context.add_class("configuratorwin")
        
        box = self.get_child()
        
        self.set_decorated(False)
        
        self.connect('close-request', self.delete_event)
        self.connect('destroy', self.delete_event)
        
        self.notebook = Gtk.Notebook.new()
        self.notebook.set_show_border(True)
        box.append(self.notebook)
        
        ## MENU
        self.page2_box = Gtk.Grid.new()
        self.page2_box.set_column_homogeneous(True)
        page2_label = Gtk.Label(label="Menu")
        self.notebook.append_page(self.page2_box, page2_label)
        #
        menu_lbl_w = Gtk.Label(label="Width")
        menu_lbl_w.set_tooltip_text("This application width.")
        self.page2_box.attach(menu_lbl_w,0,0,1,1)
        menu_lbl_w.set_halign(1)
        menu_w_spinbtn = Gtk.SpinButton.new_with_range(0,1000,1)
        menu_w_spinbtn.set_value(self._parent.menu_width)
        self.page2_box.attach_next_to(menu_w_spinbtn,menu_lbl_w,1,1,1)
        menu_w_spinbtn.connect('value-changed', self.on_menu_wh_spinbtn, "w")
        menu_w_spinbtn.set_numeric(True)
        
        menu_lbl_h = Gtk.Label(label="Height")
        menu_lbl_h.set_tooltip_text("This application height.")
        self.page2_box.attach(menu_lbl_h,0,1,1,1)
        menu_lbl_h.set_halign(1)
        menu_h_spinbtn = Gtk.SpinButton.new_with_range(0,1000,1)
        menu_h_spinbtn.set_value(self._parent.menu_height)
        self.page2_box.attach_next_to(menu_h_spinbtn,menu_lbl_h,1,1,1)
        menu_h_spinbtn.connect('value-changed', self.on_menu_wh_spinbtn, "h")
        menu_h_spinbtn.set_numeric(True)
        
        menu_lbl_ci = Gtk.Label(label="Category icon size")
        menu_lbl_ci.set_tooltip_text("The main categories icon size.")
        self.page2_box.attach(menu_lbl_ci,0,2,1,1)
        menu_lbl_ci.set_halign(1)
        menu_ci_spinbtn = Gtk.SpinButton.new_with_range(24,512,1)
        menu_ci_spinbtn.set_value(self._parent.menu_cat_icon_size)
        self.page2_box.attach_next_to(menu_ci_spinbtn,menu_lbl_ci,1,1,1)
        menu_ci_spinbtn.connect('value-changed', self.on_menu_wh_spinbtn, "ci")
        menu_ci_spinbtn.set_numeric(True)
        
        menu_lbl_i = Gtk.Label(label="Item icon size")
        menu_lbl_i.set_tooltip_text("The applications icon size.")
        self.page2_box.attach(menu_lbl_i,0,3,1,1)
        menu_lbl_i.set_halign(1)
        menu_i_spinbtn = Gtk.SpinButton.new_with_range(24,512,1)
        menu_i_spinbtn.set_value(self._parent.menu_item_icon_size)
        self.page2_box.attach_next_to(menu_i_spinbtn,menu_lbl_i,1,1,1)
        menu_i_spinbtn.connect('value-changed', self.on_menu_wh_spinbtn, "ii")
        menu_i_spinbtn.set_numeric(True)
        
        menu_lbl_ls = Gtk.Label(label="Live search characters (3 or more)")
        menu_lbl_ls.set_tooltip_text("Minimum amount of characters to perform a query.")
        self.page2_box.attach(menu_lbl_ls,0,5,1,1)
        menu_lbl_ls.set_halign(1)
        menu_ls_spinbtn = Gtk.SpinButton.new_with_range(0,20,1)
        menu_ls_spinbtn.set_value(self._parent.menu_live_search)
        self.page2_box.attach_next_to(menu_ls_spinbtn,menu_lbl_ls,1,1,1)
        menu_ls_spinbtn.connect('value-changed', self.on_menu_wh_spinbtn, "ls")
        menu_ls_spinbtn.set_numeric(True)
        
        menu_n_item_lbl = Gtk.Label(label="Number of columns")
        menu_n_item_lbl.set_tooltip_text("Number of elements in the view for each row.")
        self.page2_box.attach(menu_n_item_lbl,0,7,1,1)
        menu_n_item_lbl.set_halign(1)
        menu_n_item_spinbtn = Gtk.SpinButton.new_with_range(0,20,1)
        menu_n_item_spinbtn.set_value(self._parent.menu_n_items)
        self.page2_box.attach_next_to(menu_n_item_spinbtn,menu_n_item_lbl,1,1,1)
        menu_n_item_spinbtn.connect('value-changed', self.on_menu_wh_spinbtn, "n_item")
        menu_n_item_spinbtn.set_numeric(True)
        
        menu_editor_lbl = Gtk.Label(label="Menu editor")
        menu_editor_lbl.set_tooltip_text("The program to modify the menu.")
        self.page2_box.attach(menu_editor_lbl,0,8,1,1)
        menu_editor_lbl.set_halign(1)
        menu_editor_e = Gtk.Entry.new()
        menu_editor_e.connect('changed', self.on_menu_editor)
        self.page2_box.attach_next_to(menu_editor_e,menu_editor_lbl,1,1,1)
        menu_editor_e.set_text(self._parent.menu_editor)
        
        term_lbl = Gtk.Label(label="Terminal")
        term_lbl.set_tooltip_text("Some programs work in terminal.")
        self.page2_box.attach(term_lbl,0,9,1,1)
        term_lbl.set_halign(1)
        term_e = Gtk.Entry.new()
        term_e.connect('changed', self.on_term)
        self.page2_box.attach_next_to(term_e,term_lbl,1,1,1)
        term_e.set_text(self._parent.menu_terminal)
        
        ## OTHERS
        self.page3_box = Gtk.Grid.new()
        self.page3_box.set_column_homogeneous(True)
        page3_label = Gtk.Label(label="Other")
        self.notebook.append_page(self.page3_box, page3_label)
        #
        pad_lbl = Gtk.Label(label="Pad")
        self.page3_box.attach(pad_lbl,0,0,1,1)
        pad_lbl.set_halign(1)
        pad_spinbtn = Gtk.SpinButton.new_with_range(0,50,1)
        pad_spinbtn.set_value(self._parent._pad)
        self.page3_box.attach_next_to(pad_spinbtn,pad_lbl,1,1,1)
        # pad_spinbtn.connect('value-changed', self.on_other_spinbtn, "pad")
        pad_spinbtn.set_numeric(True)
        
        logout_lbl = Gtk.Label(label="Logout (command)")
        self.page3_box.attach(logout_lbl,0,1,1,1)
        logout_lbl.set_halign(1)
        logout_e = Gtk.Entry.new()
        logout_e.connect('changed', self.on_command,"logout")
        self.page3_box.attach_next_to(logout_e,logout_lbl,1,1,1)
        logout_e.set_text(self._parent._logout)
        
        shutdown_lbl = Gtk.Label(label="Shutdown (command)")
        self.page3_box.attach(shutdown_lbl,0,2,1,1)
        shutdown_lbl.set_halign(1)
        shutdown_e = Gtk.Entry.new()
        shutdown_e.connect('changed', self.on_command,"shutdown")
        self.page3_box.attach_next_to(shutdown_e,shutdown_lbl,1,1,1)
        shutdown_e.set_text(self._parent._shutdown)
        
        reboot_lbl = Gtk.Label(label="Reboot (command)")
        self.page3_box.attach(reboot_lbl,0,3,1,1)
        reboot_lbl.set_halign(1)
        reboot_e = Gtk.Entry.new()
        reboot_e.connect('changed', self.on_command,"reboot")
        self.page3_box.attach_next_to(reboot_e,reboot_lbl,1,1,1)
        reboot_e.set_text(self._parent._reboot)
        #
        rebuild_lbl = Gtk.Label(label="Automatic menu rebuild")
        rebuild_lbl.set_tooltip_text("If no is choosen, the menu must be rebuilt manually.")
        self.page3_box.attach(rebuild_lbl,0,7,1,1)
        rebuild_lbl.set_halign(1)
        rebuild_combo = Gtk.ComboBoxText.new()
        rebuild_combo.append_text("No")
        rebuild_combo.append_text("Yes")
        rebuild_combo.set_active(self._parent._rebuild)
        self.page3_box.attach_next_to(rebuild_combo,rebuild_lbl,1,1,1)
        rebuild_combo.connect('changed', self.on_rebuild_combo)
        
        wlrctl_lbl = Gtk.Label(label="Use Wlrctl")
        wlrctl_lbl.set_tooltip_text("Use wlrctl to hide or show this program.\nPreferred method.\n\
Commands:\nwlrctl toplevel minimize title:wbarmenu-1\nwlrctl toplevel focus title:wbarmenu-1")
        self.page3_box.attach(wlrctl_lbl,0,8,1,1)
        wlrctl_lbl.set_halign(1)
        wlrctl_combo = Gtk.ComboBoxText.new()
        wlrctl_combo.append_text("No")
        wlrctl_combo.append_text("Yes")
        wlrctl_combo.set_active(self._parent._use_wlrctl)
        self.page3_box.attach_next_to(wlrctl_combo,wlrctl_lbl,1,1,1)
        wlrctl_combo.connect('changed', self.on_wlrctl_combo)
        
        fifo_lbl = Gtk.Label(label="Use fifo (mandatory)")
        fifo_lbl.set_tooltip_text("Use fifo to communicate with the program.\n\
The commands are: __exit (quit the program), __toggle (hide or show the program).\nJust use: echo \"__exit\" > wbarmenufifo .")
        self.page3_box.attach(fifo_lbl,0,9,1,1)
        fifo_lbl.set_halign(1)
        fifo_combo = Gtk.ComboBoxText.new()
        fifo_combo.append_text("No")
        fifo_combo.append_text("Yes")
        fifo_combo.set_active(self._parent._use_fifo)
        self.page3_box.attach_next_to(fifo_combo,fifo_lbl,1,1,1)
        fifo_combo.connect('changed', self.on_fifo_combo)
        
        
        ###########
        self.set_visible(True)
    
    def delete_event(self, widget, event=None):
        self._parent.on_close_dialog_conf()
        return True
    
    ### menu w h ci ii ls n_item
    def on_menu_wh_spinbtn(self, btn, _type):
        self._parent.set_menu_cp(_type, btn.get_value_as_int())
    
    # def on_entry_menu(self, _entry, _type):
        # self._parent.entry_menu(_type, _entry.get_text())
    
    def on_menu_editor(self, _entry):
        self._parent.on_menu_editor(_entry.get_text())
    
    def on_term(self, _entry):
        self._parent.on_term(_entry.get_text())
    
    ### others
    def on_command(self, _entry, _type):
        self._parent.on_command(_entry.get_text(), _type)
    
    def on_rebuild_combo(self, cb):
        self._parent.on_menu_rebuild(cb.get_active())
    
    def on_wlrctl_combo(self, cb):
        self._parent.on_wlrctl(cb.get_active())

    def on_fifo_combo(self, cb):
        self._parent.on_fifo(cb.get_active())
        
        
class Application(Gtk.Application):
    """ Main Aplication class """

    def __init__(self):
        super().__init__(application_id='org.example.wbarmenu',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = menuWin(application=self)
        
        win.present()
        

def main():
    """ Run the main application"""
    app = Application()
    return app.run()

try:
    if __name__ == '__main__':
        main()
    
finally:
    pass
