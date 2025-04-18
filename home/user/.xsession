xset s off 
xset -dpms 
xset s noblank 


gpio17=$(gpioget gpiochip4 17)

## wenn 1 dann rate 25, wenn nicht 1 dann rate 50
if [ $gpio17 -eq 1 ]
then
    xrandr --output HDMI-1 --mode 1920x1080 --rate 25
	xrandr --output HDMI-2 --mode 1920x1080 --rate 60
else
    xrandr --output HDMI-1 --mode 1920x1080 --rate 50
	xrandr --output HDMI-2 --mode 1920x1080 --rate 60
fi

#xrandr --output HDMI-1 --mode 1920x1080 --rate 30 
#xrandr --output HDMI-2 --mode 1920x1080 --rate 30

sleep 5

hdmi2_check=$(kmsprint)

if echo "$hdmi2_check" | grep -qE "HDMI-A-2\s+\(connected\)"; then
    echo "HDMI-A-2 ist verbunden"
    chromium-browser --disable-translate --disable-features=TranslateUI --noerrdialogs --disable-infobars --app="http://127.0.0.1/timer" --start-fullscreen --window-position=0,0 --user-data-dir=/home/user/.chromium/profile1 --enable-features=OverlayScrollbar --window-size=1920,1080 --site-per-process &
    chromium-browser --app="http://127.0.0.1/editor" --user-data-dir=/home/user/.chromium/profile2 --kiosk --window-position=1920,0 --window-size=1920,1080
else
    echo "HDMI-A-2 ist nicht verbunden"
    chromium-browser --disable-translate --disable-features=TranslateUI --noerrdialogs --disable-infobars --app="http://127.0.0.1/timer" --start-fullscreen --window-position=0,0 --user-data-dir=/home/user/.chromium/profile1 --enable-features=OverlayScrollbar --window-size=1920,1080 --site-per-process
fi





