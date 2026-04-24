[app]
title = Deprem App
package.name = depremapp
package.domain = org.seyidali
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,json,txt
version = 0.1.0

requirements = python3,kivy,kivymd,requests

orientation = portrait
fullscreen = 0

# Eğer main.py dışında başka ana dosya kullanacaksan burada düzenlenir.
# entrypoint = main.py

[buildozer]
log_level = 2
warn_on_root = 1

[python]
# Gereksiz büyük paketlerden kaçınmak için sade tutuyoruz.

[android]
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a,armeabi-v7a
android.permissions = INTERNET
android.private_storage = True
android.allow_backup = False

# İhtiyaç olursa açılabilir:
# android.enable_androidx = True

[linux]

[ios]
