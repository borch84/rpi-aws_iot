sudo raspi-config
Navigate to 5 Interfacing options and enable SPI (P4 SPI)
sudo reboot

sudo apt-get install xserver-xorg
sudo apt-get install xinit
sudo apt-get install lxde-core lxterminal lxappearance
sudo apt-get install lightdm

A large chunk of the LightDM download is gnome theme junk. LightDM could be trimmed for LXDE.

sudo raspi-config, select Boot Options, then select Desktop Autologin.

Reboot.

You now have the Debian Raspbian LXDE desktop.

pi@aws-rpi02:~ $ cat /boot/config.txt | grep dtoverlay | tail -1 
dtoverlay=piscreen,speed=16000000,rotate=90

pi@aws-rpi02:~ $ cat /boot/cmdline.txt 
console=tty1 root=/dev/mmcblk0p7 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait fbcon=map:10

sudo apt-get install fbi

pi@aws-rpi02:~ $ cat /usr/share/X11/xorg.conf.d/99-fbturbo.conf 
Section "Device"
  Identifier "myfb"
  Driver "fbdev"
  Option "fbdev" "/dev/fb1"
EndSection

pi@aws-rpi02:~ $ cat /etc/xdg/lxsession/LXDE/touchscreen.sh 
DISPLAY=:0 xinput --set-prop 'ADS7846 Touchscreen' “Coordinate Transformation Matrix” -1 0 1 0 1 0 0 0 1
DISPLAY=:0 xinput --set-prop 'ADS7846 Touchscreen' 'Evdev Axes Swap' 0
DISPLAY=:0 xinput --set-prop 'ADS7846 Touchscreen' 'Evdev Axis Inversion' 1 1

pi@aws-rpi02:~ $ ls -l /etc/xdg/lxsession/LXDE/touchscreen.sh
-rwxr-xr-x 1 pi pi 258 Oct 18 19:55 /etc/xdg/lxsession/LXDE/touchscreen.sh
pi@aws-rpi02:~ $ 

pi@aws-rpi02:~ $ cat /etc/xdg/lxsession/LXDE/autostart 
@lxpanel --profile LXDE
@pcmanfm --desktop --profile LXDE
@lxterminal --command "/etc/xdg/lxsession/LXDE/touchscreen.sh"
@xscreensaver -no-splash
pi@aws-rpi02:~ $ 

pi@aws-rpi02:~ $ ls -l /etc/xdg/lxsession/LXDE/autostart
-rw-r--r-- 1 root root 146 Oct 18 19:21 /etc/xdg/lxsession/LXDE/autostart
pi@aws-rpi02:~ $ 

apt-get install xserver-xorg-input-evdev

The solution is to open /usr/share/X11/xorg.conf.d/40-libinput.conf and change Driver "libinput" to Driver "evdev" for the touchscreen section.

Section "InputClass"
        Identifier "libinput touchscreen catchall"
        MatchIsTouchscreen "on"
        MatchDevicePath "/dev/input/event*"
        Driver "evdev"
EndSection


sudo apt-get install xinput-calibrator

sudo reboot

xinput_calibrator

pi@aws-rpi02:~ $ cat /usr/share/X11/xorg.conf.d/99-calibration.conf
Section "InputClass"
	Identifier	"calibration"
	MatchProduct	"ADS7846 Touchscreen"
	Option	"Calibration"	"3937 218 146 3918"
	Option	"SwapAxes"	"0"
EndSection

# Asegurarse que esta config este asi:
$ cat .config/lxsession/LXDE/autostart 
@lxpanel --profile LXDE
@pcmanfm --desktop --profile LXDE
@xscreensaver -no-splash

# Cuando se tiene el archivo .config/lxsession/LXDE/autostar asi:
# @lxpanel --profile LXDE
# @pcmanfm --desktop --profile LXDE
# @lxterminal --command "/etc/xdg/lxsession/LXDE/touchscreen.sh" <== Remove this line after installation
# @xscreensaver -no-splash

# La sincronizacion del touchscreen no se ejecuta. 

sudo reboot
