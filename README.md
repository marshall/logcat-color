# logcat-color
A colorful and highly configurable alternative to the `adb logcat` command from
the Android SDK.

# Installation

**Installation with pip / easy_install** (may require sudo)
    
    $ pip install logcat-color
    .. or ..
    $ easy_install logcat-color

**Installation from source** (requires setuptools, may require sudo)

To get the source, simply [download and extract a release tarball](https://github.com/marshall/logcat-color/downloads).
Alternatively, you can clone the logcat-color git repository directly:
    
    $ git clone git://github.com/marshall/logcat-color.git

To install logcat-color from the source directory, run:
    
    $ python setup.py install

## Examples

Run and colorify `adb logcat`
    
    $ logcat-color

Colorify an old logcat text file you have laying around
    
    $ logcat-color < /path/to/my.log

Pipe logcat-color to egrep for only the tags you care about
    
    $ logcat-color -e | egrep '(Tag1|Tag2)'

Run logcat-color with a [custom profile](#profiles) for [filters](#profile_filters), colors, and custom arguments)
    
    $ logcat-color <profile-name>

logcat-color also supports most of the standard adb / logcat arguments, making it a suitable full-time replacement for `adb logcat`
    
    $ alias logcat=/path/to/logcat-color
    $ logcat -e
    $ logcat -d
    $ logcat -s 123456789 -b radio -b main

For command line usage documentation:
    
    $ logcat-color --help

## <a id="configuration"></a>Configuration

logcat-color supports a configuration file at `$HOME/.logcat-color`

The configuration file is simply a python script, with a few interesting variables
and types available to it.

**Sample .logcat-color**
    
    # Full path to adb, default is to look at the environment variable ADB, or
    # fall back on using "adb" from the system PATH
    adb = "/path/to/adb"

    # Width of the TAG column, default is 20
    tag_width = 20

    # Width of the PID column, default is 8
    pid_width = 8

    # Width of priority (log level) column, default is 3
    priority_width = 3

    # Whether or not to wrap the message inside a column. Setting this to False
    # enables easier copy/paste. default is True
    wrap = True

## <a id="profiles"></a> Profiles

Profiles live in the [logcat-color configuration file](#configuration), and
allow logcat-color to customize ADB and logging even further.

In short, a single Profile can:

* [Filter](#profile_filters) based on arbitrary log data.
* Use custom adb command line arguments, devices, and log formats
* Customize display and color configuration.

A profile is created by simply calling the Profile python constructor with
various named arguments. The only required argument is the Profile's `name`:

    Profile(name = "myProfile", ...)

You can then have logcat-color use this profile by providing it on the command
line. For example:
    
    $ logcat-color myProfile

To customize the Profile, simply pass more named arguments to the `Profile`
constructor. This is a list of all the currently supported named arguments:

* `buffers`: A list of logcat buffers to display. By default logcat uses only the
  `main` system buffer. See the [Android documentation for logcat buffers](http://developer.android.com/tools/debugging/debugging-log.html#alternativeBuffers)
  for more information.
* `device`: Specifies the device this profile is intended for.
  Valid values: True (connect to first available device), or a string with
  the serial ID of the device as reported by `adb devices`
* `emulator`: Similar to `device`, but providing `True` connects to the first
  available emulator instead.
* `filters`: A list or tuple of [custom filters](#profile_filters).
* `format`: The logcat format to use. By default logcat uses the `brief` format.
  See the [Android documentation for logcat formats](http://developer.android.com/tools/debugging/debugging-log.html#outputFormat)
  for more information.
* `name`: The profile name (required).
* `priorities`: A list or tuple of priority levels. logcat-color will exclude
  any messages that contain priorities not in this list.
  Valid priorities: `V` (verbose), `D` (debug), `I` (info), `W` (warn),
  `E` (error), `F` (fatal).
* `tags`: A list, tuple, or dict of logcat tag names. logcat-color will exclude
  any messages that contain tags not in this list. When a dict is used, you can
  also assign custom colors to each tag.
  Valid tag colors: `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`, `WHITE`
* `wrap`: Whether or not to wrap the message column. Default is `True`.

Here is an extended example:
    
    Profile(name = "radio",
        # Specify a custom device
        device = "device_name",

        # Enable both radio and main buffers (-b radio -b main)
        buffers = ("radio", "main"),

        # Only pay attention to the RIL and RILC tags, and give them custom colors
        tags = {
            "RIL": BLUE,
            "RILC": GREEN
        },

        # Only look at these priority levels
        priorities = ("I", "W", "E"),

        # Use threadtime format to get date/time stamps and thread IDs
        format = "threadtime",

        # Some custom filters
        filters = (
          r"My Custom Regex",
          lambda data: data["message"] == "Custom filter"
        )
    )

### <a id="profile_filters"></a> Filters

Filters allow your profile to have complete control over what log data you
actually see when you run logcat-color.

logcat-color will run each line of log output through the list of filters in
your profile. Only when the entire list of filters have accepted the line will
it actually be displayed. This is the equivalent of logically ANDing the results
of each filter. If you require different logic, you should use a custom function
filter, and combine the results of various filters manually.

There are currently two different kinds of filters:

#### Regex filters

When the regex matches the message portion of a line of logcat output, that line
will then be matched against the next filter. For example:
    
    # A negated regex -- exclude any line that matches this
    def negatedRegex(regex):
      return r"^(?!.*" + regex + ").*$"

    Profile(...
      filters = (negatedRegex(r"debugging: "), r"my custom regex")
    )

#### Function filters

When the function returns `True` for a line of log output, that line will then
be matched against the next filter. The function will be passed a `data`
dictionary that contains all of the log data:

* `"priority"`: One of the logcat priorities: `V` (verbose), `D` (debug),
  `I` (info), `W` (warn), `E` (error), `F` (fatal).
  Availability: All logcat formats.
* `"message"`: The log message itself
  Availability: All logcat formats.
* `"tag"`: The Tag of this log message.
  Availability: All logcat formats except `thread`.
* `"pid"`: The PID of the process that logged the message (in string form).
  Availability: All logcat formats except `tag`.
* `"tid"`: The ID of the thread that logged the message (in string form).
  Availability: `thread`, `threadtime`, and `long` formats.
* `"date"`: The date of the log message (in string form).
  Availability: `time`, `threadtime`, and `long` formats.
* `"time"`: The time of the log message (in string form).
  Availability: `time`, `threadtime`, and `long` formats.

Notice that many of these fields are conditional based on the logcat output
format. Be careful when constructing the logic of function filters, as the field
you are filtering may not exist in the message!

An example of a function filter:
    
    # only include messages from my app's tags
    def onlyMyApp(data):
        # Tag isn't available in "thread" format, so use get() to be safe and
        # return None instead of raising an exception
        return data.get("tag") in ("MyAppTag1", "MyAppTag2")

    Profile(...
        filters = (onlyMyApp)
    )

## Screenshot
![logcat-color screenshot of Boot2Gecko](https://img.skitch.com/20120629-jkeek3mbk2ibk9w75xqku88wpt.jpg)

## Thanks

Thanks to [Jeff Sharkey](http://jsharkey.org) for the original script that logcat-color is based on, [coloredlogcat.py](http://jsharkey.org/blog/2009/04/22/modifying-the-android-logcat-stream-for-full-color-debugging/).
