[app]
title = Dayflow — Habit Tracker
package.name = dayflow
package.domain = org.example
source.dir = .
source.include_exts = py,kv,png,jpg,atlas,txt
version = 2.0.0
requirements = python3,kivy==2.3.0,plyer,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = VIBRATE,POST_NOTIFICATIONS,RECORD_AUDIO
android.api = 35
android.accept_sdk_license = True
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
