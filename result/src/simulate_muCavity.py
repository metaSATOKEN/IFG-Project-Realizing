 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/src/simulate_muCavity.py
index 0000000000000000000000000000000000000000..abd107aad2c3bc9ed769a9a878f5004c5ba1f8e3 100644
--- a//dev/null
+++ b/src/simulate_muCavity.py
@@ -0,0 +1,83 @@
+#!/usr/bin/env python3
+"""Simple μ-cavity Q simulation (approximate)"""
+import json
+import math
+import struct
+import zlib
+
+
+def simulate(params):
+    """Return list of dicts with radius, Q and mode volume."""
+    radii = [0.1 + 0.05 * i for i in range(9)]  # cm
+    results = []
+    q_peak = params.get("q_peak", 6e6)
+    r_opt = params.get("r_opt", 0.25)
+    height = params.get("height", 0.1)  # cm
+    for r in radii:
+        q = q_peak / (1.0 + ((r - r_opt) / 0.08) ** 2)
+        volume = math.pi * r * r * height
+        results.append({
+            "radius_cm": r,
+            "Q": q,
+            "mode_volume_cm3": volume
+        })
+    return results
+
+
+def save_json(data, path):
+    with open(path, "w") as f:
+        json.dump(data, f, indent=2)
+
+
+def set_pixel(img, width, x, y, color):
+    if 0 <= x < width and 0 <= y < len(img) // (width * 3):
+        idx = (y * width + x) * 3
+        img[idx:idx+3] = color
+
+
+def make_plot(data, path):
+    width, height = 400, 300
+    img = bytearray([255] * width * height * 3)
+    # axes
+    for x in range(20, width - 10):
+        set_pixel(img, width, x, height - 20, (0, 0, 0))
+    for y in range(10, height - 20):
+        set_pixel(img, width, 20, height - 1 - y, (0, 0, 0))
+    vols = [d["mode_volume_cm3"] for d in data]
+    qs = [d["Q"] for d in data]
+    v_min, v_max = min(vols), max(vols)
+    q_min, q_max = 0.0, max(qs)
+    for v, q in zip(vols, qs):
+        x = int(20 + (v - v_min) / (v_max - v_min) * (width - 40))
+        y = int(20 + (q - q_min) / (q_max - q_min) * (height - 40))
+        y = height - y
+        for dy in range(-2, 3):
+            for dx in range(-2, 3):
+                set_pixel(img, width, x + dx, y + dy, (255, 0, 0))
+    # build PNG
+    def chunk(tag, data):
+        return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xffffffff)
+    raw = bytearray()
+    for y in range(height):
+        raw.append(0)
+        row = img[y * width * 3:(y + 1) * width * 3]
+        raw.extend(row)
+    png = b'\x89PNG\r\n\x1a\n'
+    png += chunk(b'IHDR', struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0))
+    compressed = zlib.compress(bytes(raw), 9)
+    png += chunk(b'IDAT', compressed)
+    png += chunk(b'IEND', b'')
+    with open(path, "wb") as f:
+        f.write(png)
+
+
+def main():
+    params = {}
+    data = simulate(params)
+    save_json(data, "result/q_vs_r.json")
+    make_plot(data, "docs/plot/mode_volume_vs_q.png")
+    print("Simulation complete. Data points:", len(data))
+
+
+if __name__ == "__main__":
+    main()
 
EOF
)
