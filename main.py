# main.py
# Pydroid 3 + KivyMD uyumlu tek dosyalık deprem uygulaması.
# Gerekli paketler:
# pip install kivy kivymd requests

from __future__ import annotations

import re
from datetime import datetime
from threading import Thread

import requests
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel


AFAD_URL = "https://deprem.afad.gov.tr/apiv2/event/filter"
TIMEOUT = 12


def safe_text(value, default="—"):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def parse_time(value):
    """
    Farklı tarih formatlarını yakalamaya çalışır.
    Başarısız olursa None döner.
    """
    if not value:
        return None

    text = str(value).strip()

    patterns = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
    ]

    for fmt in patterns:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass

    # ISO benzeri metinler için son deneme
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


def format_time(value):
    dt = parse_time(value)
    if dt is None:
        return safe_text(value)
    return dt.strftime("%d.%m.%Y %H:%M:%S")


def is_turkiye_event(item: dict) -> bool:
    """
    Türkiye filtresi.
    Veri alanları değişse bile çalışabilsin diye birkaç anahtar kontrol edilir.
    """
    fields = [
        item.get("location"),
        item.get("loc"),
        item.get("place"),
        item.get("province"),
        item.get("city"),
        item.get("region"),
        item.get("country"),
    ]
    joined = " | ".join(safe_text(x, "") for x in fields).lower()

    turkey_keywords = [
        "türkiye",
        "turkiye",
        "turkey",
        "tr",
    ]
    return any(k in joined for k in turkey_keywords)


def normalize_event(item: dict) -> dict:
    """
    AFAD veri alanları farklı isimlerle dönerse diye esnek normalizasyon.
    """
    magnitude = (
        item.get("magnitude")
        or item.get("mag")
        or item.get("mw")
        or item.get("ml")
        or item.get("md")
    )

    location = (
        item.get("location")
        or item.get("loc")
        or item.get("place")
        or item.get("province")
        or item.get("city")
        or item.get("region")
    )

    depth = item.get("depth") or item.get("depthKm") or item.get("depth_km")
    time_value = item.get("date") or item.get("time") or item.get("datetime") or item.get("eventDate")

    lat = item.get("latitude") or item.get("lat")
    lon = item.get("longitude") or item.get("lon") or item.get("lng")

    return {
        "magnitude": safe_text(magnitude),
        "location": safe_text(location),
        "depth": safe_text(depth),
        "time_raw": safe_text(time_value),
        "time": format_time(time_value),
        "latitude": safe_text(lat),
        "longitude": safe_text(lon),
        "raw": item,
        "dt": parse_time(time_value),
    }


def extract_list(payload):
    """
    API bazen liste, bazen sözlük döndürür.
    İçinden listeleri güvenli biçimde çıkarır.
    """
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("data", "result", "items", "events", "content", "rows"):
            value = payload.get(key)
            if isinstance(value, list):
                return value

        # İçinde tek kayıt varsa onu da değerlendir
        return [payload]

    return []


def fetch_earthquakes():
    """
    AFAD verisini çeker, Türkiye dışını filtreler, sadeleştirir ve sıralar.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Android) DepremApp/1.0",
        "Accept": "application/json, text/plain, */*",
    }

    response = requests.get(AFAD_URL, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()

    try:
        payload = response.json()
    except Exception:
        # JSON gelmezse deneme başarısız sayılır
        return []

    items = extract_list(payload)
    results = []

    for item in items:
        if not isinstance(item, dict):
            continue
        if not is_turkiye_event(item):
            continue
        results.append(normalize_event(item))

    # En yeni en üstte
    results.sort(key=lambda x: x["dt"] or datetime.min, reverse=True)
    return results


class DepremApp(MDApp):
    def build(self):
        self.title = "Deprem TR"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"

        self.all_events = []
        self.filtered_events = []
        self.loading = False

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10),
        )

        # Başlık kartı
        header = MDCard(
            size_hint_y=None,
            height=dp(92),
            radius=[22, 22, 22, 22],
            elevation=2,
            padding=dp(14),
        )
        header_box = BoxLayout(orientation="vertical", spacing=dp(4))
        header_box.add_widget(
            MDLabel(
                text="Deprem TR",
                font_style="H4",
                bold=True,
                halign="left",
            )
        )
        header_box.add_widget(
            MDLabel(
                text="Sadece Türkiye depremleri • Canlı liste",
                font_style="Body2",
                halign="left",
            )
        )
        header.add_widget(header_box)

        # Arama + yenileme
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(46),
            spacing=dp(8),
        )

        self.search_input = TextInput(
            hint_text="İl / ilçe / bölge ara",
            multiline=False,
            size_hint_x=1,
            background_color=(0.18, 0.18, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 0.3, 0.3, 1),
            padding=[dp(12), dp(12), dp(12), dp(12)],
        )
        self.search_input.bind(text=self.on_search_text)

        refresh_btn = Button(
            text="Yenile",
            size_hint_x=None,
            width=dp(96),
            background_normal="",
            background_color=(0.85, 0.1, 0.1, 1),
            color=(1, 1, 1, 1),
        )
        refresh_btn.bind(on_release=lambda *_: self.refresh_data())

        row.add_widget(self.search_input)
        row.add_widget(refresh_btn)

        # Özet kartları
        stats = GridLayout(
            cols=3,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(92),
        )
        self.count_card = self._stat_card("Kayıt", "0")
        self.strongest_card = self._stat_card("En Büyük", "—")
        self.latest_card = self._stat_card("Son Kayıt", "—")

        stats.add_widget(self.count_card)
        stats.add_widget(self.strongest_card)
        stats.add_widget(self.latest_card)

        # Durum
        self.status_label = Label(
            text="Hazır.",
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle",
            color=(0.85, 0.85, 0.85, 1),
        )
        self.status_label.bind(size=self._sync_label_text_size)

        # Liste alanı
        self.events_box = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            padding=[0, 0, 0, dp(12)],
        )
        self.events_box.bind(minimum_height=self.events_box.setter("height"))

        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(self.events_box)

        root.add_widget(header)
        root.add_widget(row)
        root.add_widget(stats)
        root.add_widget(self.status_label)
        root.add_widget(scroll)

        Clock.schedule_once(lambda *_: self.refresh_data(), 0.2)
        return root

    def _sync_label_text_size(self, instance, _size):
        instance.text_size = (instance.width, None)

    def _stat_card(self, title, value):
        card = MDCard(
            size_hint_y=None,
            height=dp(88),
            radius=[18, 18, 18, 18],
            elevation=1,
            padding=dp(10),
        )
        box = BoxLayout(orientation="vertical", spacing=dp(2))
        t = MDLabel(text=title, font_style="Caption", halign="left")
        v = MDLabel(text=value, font_style="H5", bold=True, halign="left")
        box.add_widget(t)
        box.add_widget(v)
        card.add_widget(box)
        card._value_label = v
        return card

    def set_stat(self, card, value):
        card._value_label.text = value

    def set_status(self, text):
        self.status_label.text = text

    def on_search_text(self, *_):
        query = self.search_input.text.strip().lower()
        if not query:
            self.filtered_events = list(self.all_events)
        else:
            def match(ev):
                hay = " ".join([
                    ev["location"],
                    ev["time"],
                    ev["magnitude"],
                    ev["depth"],
                    ev["latitude"],
                    ev["longitude"],
                ]).lower()
                return query in hay

            self.filtered_events = [ev for ev in self.all_events if match(ev)]

        self.render_events()

    def refresh_data(self):
        if self.loading:
            return

        self.loading = True
        self.set_status("Depremler yükleniyor...")
        self.events_box.clear_widgets()
        self.events_box.add_widget(self._message_card("Yükleniyor..."))

        thread = Thread(target=self._refresh_worker, daemon=True)
        thread.start()

    def _refresh_worker(self):
        try:
            events = fetch_earthquakes()
            Clock.schedule_once(lambda *_: self._apply_loaded_data(events), 0)
        except requests.RequestException as exc:
            Clock.schedule_once(lambda *_: self._apply_error(f"Bağlantı hatası: {exc}"), 0)
        except Exception as exc:
            Clock.schedule_once(lambda *_: self._apply_error(f"Beklenmeyen hata: {exc}"), 0)

    def _apply_loaded_data(self, events):
        self.loading = False
        self.all_events = events
        self.on_search_text()

        count = len(self.all_events)
        self.set_stat(self.count_card, str(count))

        if count:
            strongest = max(
                self.all_events,
                key=lambda x: self._magnitude_value(x["magnitude"]),
            )
            self.set_stat(self.strongest_card, strongest["magnitude"])
            self.set_stat(self.latest_card, strongest["time"] if strongest["time"] != "—" else "—")
            self.set_status(f"{count} kayıt bulundu. Türkiye filtresi aktif.")
        else:
            self.set_stat(self.strongest_card, "—")
            self.set_stat(self.latest_card, "—")
            self.set_status("Kayıt bulunamadı.")

    def _apply_error(self, message):
        self.loading = False
        self.all_events = []
        self.filtered_events = []
        self.set_stat(self.count_card, "0")
        self.set_stat(self.strongest_card, "—")
        self.set_stat(self.latest_card, "—")
        self.set_status(message)
        self.events_box.clear_widgets()
        self.events_box.add_widget(self._message_card(message))

    def _magnitude_value(self, text):
        try:
            return float(re.sub(r"[^\d.,-]", "", str(text)).replace(",", "."))
        except Exception:
            return 0.0

    def _message_card(self, text):
        card = MDCard(
            size_hint_y=None,
            height=dp(72),
            radius=[18, 18, 18, 18],
            elevation=1,
            padding=dp(12),
        )
        label = MDLabel(text=text, halign="center", valign="middle")
        card.add_widget(label)
        return card

    def _event_card(self, ev):
        mag = ev["magnitude"]
        loc = ev["location"]
        time_text = ev["time"]
        depth = ev["depth"]
        lat = ev["latitude"]
        lon = ev["longitude"]

        card = MDCard(
            size_hint_y=None,
            height=dp(118),
            radius=[18, 18, 18, 18],
            elevation=2,
            padding=dp(12),
        )

        box = BoxLayout(orientation="vertical", spacing=dp(4))

        top = MDLabel(
            text=f"[b]M {mag}[/b]   {loc}",
            markup=True,
            halign="left",
            valign="middle",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(28),
        )
        top.bind(size=self._sync_label_text_size)

        middle = MDLabel(
            text=f"🕒 {time_text}",
            halign="left",
            valign="middle",
            font_style="Body2",
            size_hint_y=None,
            height=dp(22),
        )
        middle.bind(size=self._sync_label_text_size)

        bottom = MDLabel(
            text=f"📏 Derinlik: {depth} km   •   📍 {lat}, {lon}",
            halign="left",
            valign="middle",
            font_style="Body2",
            size_hint_y=None,
            height=dp(22),
        )
        bottom.bind(size=self._sync_label_text_size)

        box.add_widget(top)
        box.add_widget(middle)
        box.add_widget(bottom)
        card.add_widget(box)
        return card

    def render_events(self):
        self.events_box.clear_widgets()

        if not self.filtered_events:
            self.events_box.add_widget(
                self._message_card("Filtreye uygun deprem kaydı yok.")
            )
            return

        for ev in self.filtered_events:
            self.events_box.add_widget(self._event_card(ev))


if __name__ == "__main__":
    DepremApp().run()
