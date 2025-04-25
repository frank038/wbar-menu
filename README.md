# wbar-menu
This is a menu application manager.


Requirements:
- python3
- gtk4 python bindings
- wlrctl (needed to open and close; an internal method is alse present, but it is retarded in opening/show)
- wayland


Features:

- execute or integrate in other applications (or use a keybinding) the file wbarmenu_toggle.sh to have the open/close functionality;
- bookmarks: just right click on an application and choose yes to add it; right click on an bookmarked application to remove it; the bookmarks can be dragged around;
- application searching integration;
- launchs only terminal applications, if a terminal is setted;
- custom buttons for logout, reboot and shutdown; and to launch a menu editor (a script for menulibre is already present);
- the list of the applications will rebuild automatically (this behaviour can be changed: in this case the menu must be rebuilt manually - a button will appear at left);
- the open/close functionality uses a simple fifo file (the command are: __exit to close the program; __toggle to open or close the program);
- graphical configurator for all its options.

May have some unknown issues.


Waybar example configuration (don't forget to set a style in style.css):

First add "custom/mymenu" in modules-left/center/right section

"custom/mymenu": {
    "format": "  ",
    "tooltip": false,
    "on-click": "$HOME/SOME_FOLDERS/wbar-menu/wbarmenu_toggle.sh"
},


Labwc example rule (the window will appear at the top-left of the monitor):

/<windowRule title="wbarmenu-1">
/    <skipWindowSwitcher>yes</skipWindowSwitcher>
/    <ignoreConfigureRequest>yes</ignoreConfigureRequest>
/    <fixedPosition>yes</fixedPosition>
/    <action name="MoveTo" x="10" y="50" />
/    <action name="alwaysOnTop"/>
/</windowRule>

![My image](https://github.com/frank038/wbar-menu/blob/main/screenshot1.jpg)

![My image](https://github.com/frank038/wbar-menu/blob/main/screenshot2.jpg)

![My image](https://github.com/frank038/wbar-menu/blob/main/screenshot3.jpg)
