# logcat-color
A colorful alternative to the standard `adb logcat` command from the Android SDK.

## Installation

Either clone this repository, or [download logcat-color directly](https://raw.github.com/marshall/logcat-color/master/logcat-color) and make sure the script is somewhere on your PATH.

**TODO**: Add a homebrew formula

## Examples

Run and colorify `adb logcat`
    
    $ logcat-color

Colorify an old logcat text file you have laying around
    
    $ logcat-color < /path/to/my.log

Pipe logcat-color to egrep for only the tags you care about
    
    $ logcat-color -e | egrep '(Tag1|Tag2)'

logcat-color also supports most of the standard adb / logcat arguments, making it a suitable full-time replacement for `adb logcat`
    
    $ alias logcat=/path/to/logcat-color
    $ logcat -e
    $ logcat -d
    $ logcat -s 123456789 -b radio -b main

## Thanks

Thanks to [Jeff Sharkey](http://jsharkey.org) for the original script that logcat-color is based on, [coloredlogcat.py](http://jsharkey.org/blog/2009/04/22/modifying-the-android-logcat-stream-for-full-color-debugging/).
