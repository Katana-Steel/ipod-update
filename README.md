#### iPod firmware updater

A proof of concept tool that actually allows you to upgrade your iPod firmware without using iTunes.

Requirements:

* urlgrabber
* python-dbus
* sg3_utils
* running HAL
* access to the raw device (most probably root account)

Please note that this is not the authorised way to update your firmware and you are the one responsible for the results in case your iPod stops working. Either take the responsibility or use iTunes.

Please note that the bundled *plistlib.py* is licensed under the Python license and comes from the Python SVN. The file was slightly modified to allow parsing of iTunes plist XML files (arrays using non-continuous indexing).

In future I hope podsleuth and HAL provide a complete userspace solution so a graphical tool becomes a possibility.

Please also note that I am currently not aware of any method allowing the upgrade on iPods Shuffle where no firmware partition is present.

Form more information see the [UpdateProcess](UpdateProcess.md).

