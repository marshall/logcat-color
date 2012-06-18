# logcat-color
A colorful alternative to the standard `adb logcat` command from the Android SDK.

# Installation

**Installation with pip / easy_install** (may require sudo)
    
    $ pip install logcat-color
    .. or ..
    $ easy_install logcat-color

**Installation from source** (requires setuptools, may require sudo)
    
    $ python setup.py install


## <a id="configuration"></a>Configuration

logcat-color supports a configuration file at `$HOME/.logcat-color`

The configuration file is simply a python script, with a few interesting variables
and types available to it.

**Sample .logcat-color**
    
    # Width of the TAG column, default is 20
    tag_width = 20

    # Width of the PID column, default is 8
    pid_width = 8

    # Width of priority (log level) column, default is 3
    priority_width = 3


## <a id="profiles"></a> Profiles

Profiles allow logcat-color to customize logging even further. 

In short, a single Profile can:
- Filter certain tags, priorities, or messages
- Use certain command line arguments
- Customized display and color configuration

Profiles live in the [logcat-color configuration file](#configuration). Here is an example:
    
    Profile(name = "radio",
        # Enable both radio and main buffers (-b radio -b main)
        buffers = ("radio", "main"),

        # Only pay attention to the RIL and RILC tags, and give them custom colors
        # Valid colors: RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
        tags = {
            "RIL": BLUE,
            "RILC": GREEN 
        },

        # Only look at these priority levels
        # Valid priorities: V (verbose), D (debug), I (info), W (warn), E (error), F (fatal)
        priorities = [ "I", "W", "E" ],

        # Only pay attention to log messages that match any of these filters
        # Each string is compiled as a regular expression.
        # Functions are called with the tag, priority, and message and
        # must return True to include the message in the log output.
        filters = [
          r"My Custom Regex",
          lambda tag, priority, message: message == "Custom filter"
        ]
    )


## Examples

Run and colorify `adb logcat`
    
    $ logcat-color

Colorify an old logcat text file you have laying around
    
    $ logcat-color < /path/to/my.log

Pipe logcat-color to egrep for only the tags you care about
    
    $ logcat-color -e | egrep '(Tag1|Tag2)'

Run logcat-color with a custom profile for filters, colors, and custom arguments (see [Profiles](#profiles))
    
    $ logcat-color <profile-name>

logcat-color also supports most of the standard adb / logcat arguments, making it a suitable full-time replacement for `adb logcat`
    
    $ alias logcat=/path/to/logcat-color
    $ logcat -e
    $ logcat -d
    $ logcat -s 123456789 -b radio -b main

## Thanks

Thanks to [Jeff Sharkey](http://jsharkey.org) for the original script that logcat-color is based on, [coloredlogcat.py](http://jsharkey.org/blog/2009/04/22/modifying-the-android-logcat-stream-for-full-color-debugging/).
