[app]
title = Deprem TR
package.name = depremtr
package.domain = org.seyidali
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,json,txt
version = 0.1.0

# requirements kısmındaki openssl, requests modülünün HTTPS (SSL) istekleri atabilmesi için Android'de şarttır, doğru eklemişsiniz.
requirements = python3,kivy==2.3.0,kivymd,pillow,requests,urllib3,certifi,charset-normalizer,idna,openssl

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.private_storage = True
android.allow_backup = False
android.enable_androidx = True

# SDK lisans onayını Buildozer içinden de garanti altına alıyoruz.
android.accept_sdk_license = True

# DİKKAT: p4a.branch = master satırını kaldırdım. 
# Buildozer'ın kendi içindeki kararlı (stable) python-for-android sürümünü kullanması,
# GitHub Actions üzerinde rastgele günlerde hata almanızı engeller.
