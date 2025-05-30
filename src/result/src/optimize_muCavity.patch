 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/src/optimize_muCavity.py
index 0000000000000000000000000000000000000000..413feb28e8a83a9161fe24ee53091e95fdf3be60 100644
--- a//dev/null
+++ b/src/optimize_muCavity.py
@@ -0,0 +1,110 @@
+import json
+import math
+import struct
+import zlib
+
+
+def quality_factor(radius_cm, q_peak=6e6, r_opt=0.25, sigma=0.08):
+    """Gaussian-like quality factor vs radius."""
+    return q_peak * math.exp(-((radius_cm - r_opt) / sigma) ** 2)
+
+
+def mode_volume(radius_cm, height_cm):
+    return math.pi * radius_cm * radius_cm * height_cm
+
+
+def grid_search(r_min=0.1, r_max=0.5, h_min=0.05, h_max=0.2, n_r=21, n_h=15):
+    """Simple grid search with reduced resolution to keep output small."""
+    results = []
+    best = None
+    best_obj = -1.0
+    for i in range(n_r):
+        r = r_min + (r_max - r_min) * i / (n_r - 1)
+        for j in range(n_h):
+            h = h_min + (h_max - h_min) * j / (n_h - 1)
+            q = quality_factor(r)
+            vol = mode_volume(r, h)
+            obj = q / vol if vol > 0 else 0
+            valid = vol <= 0.1
+            point = {
+                "radius_cm": r,
+                "height_cm": h,
+                "Q": q,
+                "mode_volume_cm3": vol,
+                "objective": obj,
+                "valid": valid,
+            }
+            results.append(point)
+            if valid and obj > best_obj:
+                best_obj = obj
+                best = {
+                    "radius_cm": r,
+                    "height_cm": h,
+                    "Q": q,
+                    "mode_volume_cm3": vol,
+                    "objective": obj,
+                }
+    return results, best
+
+
+def save_json(results, best, path):
+    with open(path, "w") as f:
+        json.dump({"points": results, "best": best}, f, indent=2)
+
+
+def set_pixel(img, width, x, y, color):
+    if 0 <= x < width and 0 <= y < len(img) // (width * 3):
+        idx = (y * width + x) * 3
+        img[idx:idx+3] = color
+
+
+def make_plot(results, path, r_min=0.1, r_max=0.5, h_min=0.05, h_max=0.2):
+    width, height = 400, 300
+    img = bytearray([255] * width * height * 3)
+    for x in range(20, width - 10):
+        set_pixel(img, width, x, height - 20, (0, 0, 0))
+    for y in range(10, height - 20):
+        set_pixel(img, width, 20, height - 1 - y, (0, 0, 0))
+    valids = [p for p in results if p["valid"]]
+    if not valids:
+        min_obj = max_obj = 0
+    else:
+        objs = [p["objective"] for p in valids]
+        min_obj, max_obj = min(objs), max(objs)
+    for p in valids:
+        r, h, obj = p["radius_cm"], p["height_cm"], p["objective"]
+        x = int(20 + (r - r_min) / (r_max - r_min) * (width - 40))
+        y = int(20 + (h - h_min) / (h_max - h_min) * (height - 40))
+        y = height - y
+        ratio = (obj - min_obj) / (max_obj - min_obj) if max_obj > min_obj else 0
+        red = int(255 * ratio)
+        blue = 255 - red
+        color = (red, 0, blue)
+        for dy in range(-2, 3):
+            for dx in range(-2, 3):
+                set_pixel(img, width, x + dx, y + dy, color)
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
+    results, best = grid_search()
+    save_json(results, best, "result/opt_design.json")
+    make_plot(results, "docs/plot/opt_result.png")
+    print("Best design:", best)
+
+
+if __name__ == "__main__":
+    main()
 
EOF
)
