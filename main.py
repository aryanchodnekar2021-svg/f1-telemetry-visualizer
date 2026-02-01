import arcade
import fastf1
import os
from collections import deque

# ================= SETTINGS =================
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
SCREEN_TITLE = "F1 Race Replay"

BG_COLOR = (15, 15, 20)
PANEL_BG = (25, 25, 35)
ACCENT_COLOR = (0, 255, 150)
TEXT_COLOR = (220, 220, 220)
GRID_COLOR = (60, 60, 70)

# ================= HELPERS =================
def hex_to_rgb(hex_str):
    if not hex_str:
        return (255, 255, 255)
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def draw_rect(left, right, top, bottom, color):
    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)

# ================= TELEMETRY GRAPH =================
class TelemetryGraph:
    def __init__(self, x, y, width, height, title, color, max_val, unit=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.color = color
        self.max_val = max_val
        self.unit = unit
        self.history = deque(maxlen=120)

    def add_value(self, value):
        self.history.append(value)

    def draw(self):
        draw_rect(self.x, self.x + self.width, self.y + self.height, self.y, PANEL_BG)

        arcade.draw_text(
            self.title, self.x + 8, self.y + self.height - 22,
            TEXT_COLOR, 11, bold=True
        )

        if self.history:
            arcade.draw_text(
                f"{self.history[-1]:.0f}{self.unit}",
                self.x + self.width - 70, self.y + self.height - 22,
                self.color, 12, bold=True
            )

        for i in range(1, 5):
            y = self.y + 15 + (self.height - 40) * i / 4
            arcade.draw_line(self.x + 8, y, self.x + self.width - 8, y, GRID_COLOR, 1)

        if len(self.history) > 1:
            for i in range(len(self.history) - 1):
                x1 = self.x + 10 + (self.width - 20) * i / len(self.history)
                y1 = self.y + 15 + (self.height - 40) * (self.history[i] / self.max_val)
                x2 = self.x + 10 + (self.width - 20) * (i + 1) / len(self.history)
                y2 = self.y + 15 + (self.height - 40) * (self.history[i + 1] / self.max_val)
                arcade.draw_line(x1, y1, x2, y2, self.color, 2.5)

# ================= MAIN WINDOW =================
class F1RaceReplay(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BG_COLOR)

        if not os.path.exists("cache"):
            os.makedirs("cache")
        fastf1.Cache.enable_cache("cache")

        print("Loading F1 data...")
        session = fastf1.get_session(2023, "Silverstone", "R")
        session.load(laps=True, telemetry=True)

        self.all_telemetry = {}
        self.driver_colors = {}
        self.driver_names = {}
        self.max_telemetry_length = 0

        for _, row in session.results.iterrows():
            drv = row["Abbreviation"]
            try:
                lap = session.laps.pick_driver(drv).pick_fastest()
                tel = lap.get_telemetry()
                self.all_telemetry[drv] = tel
                self.max_telemetry_length = max(self.max_telemetry_length, len(tel))
                self.driver_colors[drv] = hex_to_rgb(row["TeamColor"])
                self.driver_names[drv] = f"{row['FirstName']} {row['LastName']}"
            except:
                pass

        self.selected_driver = "HAM" if "HAM" in self.all_telemetry else list(self.all_telemetry.keys())[0]
        self.current_step = 0
        self.speed = 3
        self.paused = False
        self.driver_click_areas = {}

        gw, gh, gs = 260, 130, 14
        lx, top = 15, SCREEN_HEIGHT - 120

        self.graphs = {
            "speed": TelemetryGraph(lx, top - (gh + gs) * 1, gw, gh, "SPEED", ACCENT_COLOR, 360, " km/h"),
            "throttle": TelemetryGraph(lx, top - (gh + gs) * 2, gw, gh, "THROTTLE", (90, 220, 120), 100, "%"),
            "brake": TelemetryGraph(lx, top - (gh + gs) * 3, gw, gh, "BRAKE", (240, 90, 90), 100, "%"),
            "gear": TelemetryGraph(lx, top - (gh + gs) * 4, gw, gh, "GEAR", (240, 200, 80), 8)
        }

    # ================= DRAW =================
    def on_draw(self):
        self.clear()

        # ===== HEADER =====
        arcade.draw_text(
            "F1 RACE REPLAY",
            20, SCREEN_HEIGHT - 45,
            ACCENT_COLOR,
            26,
            bold=True
        )

        arcade.draw_text(
            "Interactive Formula 1 telemetry & race visualisation",
            20, SCREEN_HEIGHT - 70,
            TEXT_COLOR,
            12
        )

        # ===== TRACK PANEL =====
        track_x, track_y = 300, 60
        track_w, track_h = 700, 700
        padding = 60

        draw_rect(track_x, track_x + track_w, track_y + track_h, track_y, PANEL_BG)

        ref = self.all_telemetry[self.selected_driver]
        min_x, max_x = ref["X"].min(), ref["X"].max()
        min_y, max_y = ref["Y"].min(), ref["Y"].max()
        scale = min((track_w - 2 * padding) / (max_x - min_x),
                    (track_h - 2 * padding) / (max_y - min_y))

        for i in range(len(ref) - 1):
            x1 = track_x + padding + (ref["X"].iloc[i] - min_x) * scale
            y1 = track_y + padding + (ref["Y"].iloc[i] - min_y) * scale
            x2 = track_x + padding + (ref["X"].iloc[i+1] - min_x) * scale
            y2 = track_y + padding + (ref["Y"].iloc[i+1] - min_y) * scale
            arcade.draw_line(x1, y1, x2, y2, (80, 80, 90), 4)

        for drv, tel in self.all_telemetry.items():
            if self.current_step < len(tel):
                cx = track_x + padding + (tel["X"].iloc[self.current_step] - min_x) * scale
                cy = track_y + padding + (tel["Y"].iloc[self.current_step] - min_y) * scale
                color = self.driver_colors[drv]

                if drv == self.selected_driver:
                    arcade.draw_circle_filled(cx, cy, 14, (255, 255, 255))
                    arcade.draw_circle_filled(cx, cy, 10, ACCENT_COLOR)
                else:
                    arcade.draw_circle_filled(cx, cy, 7, color)

        tel = self.all_telemetry[self.selected_driver]
        if self.current_step < len(tel):
            self.graphs["speed"].add_value(tel["Speed"].iloc[self.current_step])
            self.graphs["throttle"].add_value(tel["Throttle"].iloc[self.current_step])
            self.graphs["brake"].add_value(tel["Brake"].iloc[self.current_step])
            self.graphs["gear"].add_value(tel["nGear"].iloc[self.current_step])

        for g in self.graphs.values():
            g.draw()

        # ===== LEADERBOARD =====
        lbx, lby = 1030, 60
        draw_rect(lbx, lbx + 340, lby + 780, lby, PANEL_BG)
        arcade.draw_text("STANDINGS", lbx + 10, lby + 740, TEXT_COLOR, 14, bold=True)

        self.driver_click_areas.clear()
        for i, drv in enumerate(self.all_telemetry.keys()):
            y = lby + 700 - i * 32
            self.driver_click_areas[drv] = (lbx, y - 5, lbx + 340, y + 22)

            if drv == self.selected_driver:
                draw_rect(lbx, lbx + 340, y + 22, y - 5, (45, 45, 60))

            arcade.draw_text(drv, lbx + 15, y,
                             ACCENT_COLOR if drv == self.selected_driver else TEXT_COLOR,
                             12, bold=True)
            arcade.draw_text(self.driver_names[drv], lbx + 60, y, TEXT_COLOR, 10)

        # ===== TRACKING INFO (BOTTOM) =====
        tracked_name = self.driver_names.get(self.selected_driver, self.selected_driver)
        arcade.draw_text(
            f"TRACKING DRIVER: {tracked_name} ({self.selected_driver})",
            300, 25,
            ACCENT_COLOR,
            14,
            bold=True
        )

    # ================= UPDATE =================
    def on_update(self, delta_time):
        if not self.paused:
            self.current_step += self.speed
            if self.current_step >= self.max_telemetry_length:
                self.current_step = 0

    # ================= INPUT =================
    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.paused = not self.paused
        elif key == arcade.key.UP:
            self.speed = min(self.speed + 1, 20)
        elif key == arcade.key.DOWN:
            self.speed = max(self.speed - 1, 1)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for drv, (x1, y1, x2, y2) in self.driver_click_areas.items():
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self.selected_driver = drv
                    for g in self.graphs.values():
                        g.history.clear()
                    break

# ================= RUN =================
if __name__ == "__main__":
    F1RaceReplay()
    arcade.run()
