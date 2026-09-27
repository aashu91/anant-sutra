# SutraOS Banyan Tree 360-Degree Drone Orbit Video Renderer
# Generates a 20-second (300 frames @ 15 FPS) 360-degree drone orbit around a massive ancient Banyan tree at sunset.

import os
import math
import tempfile
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

class Banyan360DroneRenderer:
    def __init__(self, width=640, height=640, fps=15, duration_sec=20.0):
        self.width = width
        self.height = height
        self.fps = fps
        self.duration_sec = duration_sec
        self.num_frames = int(fps * duration_sec)
        self.cx = width // 2
        self.cy = height // 2

    def render_banyan_frame(self, frame_idx):
        t = frame_idx / float(self.num_frames) # 0.0 to 1.0
        angle_rad = t * 2.0 * math.pi # 360 degree drone orbit
        
        # 1. Sunset Sky Gradient (Golden Hour 2800K -> Deep Indigo Horizon)
        img = Image.new("RGB", (self.width, self.height), (12, 18, 40))
        draw = ImageDraw.Draw(img)
        
        sky_h = int(self.height * 0.6)
        for y in range(sky_h):
            ratio = y / float(sky_h)
            r = int(18 * (1-ratio) + 245 * ratio)
            g = int(30 * (1-ratio) + 140 * ratio)
            b = int(70 * (1-ratio) + 40 * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
            
        # Sun Disc near Horizon
        sun_x = int(self.cx + math.sin(angle_rad) * 120)
        sun_y = int(sky_h * 0.7)
        draw.ellipse([sun_x-40, sun_y-40, sun_x+40, sun_y+40], fill=(255, 235, 170))

        # 2. Ground Plane (Mossy Green Earth & Roots Base)
        draw.rectangle([0, sky_h, self.width, self.height], fill=(25, 42, 22))

        # 3. 360 Drone Orbit Camera Transformation Matrix
        # Calculate parallax shift for background environment vs central Banyan tree
        cam_offset_x = int(math.sin(angle_rad) * 35)
        
        tree_x = self.cx
        tree_y = sky_h + 20

        # 4. Ancient Banyan Trunk & Massive Gnarled Prop Roots
        trunk_w = 90
        trunk_h = 180
        
        # Main Central Trunk
        draw.rectangle([tree_x - trunk_w//2, tree_y - trunk_h, tree_x + trunk_w//2, tree_y], fill=(65, 45, 30))
        
        # Vertical Gnarled Root Striations (Brown/Wood Bark Shading)
        for r_i in range(-trunk_w//2 + 5, trunk_w//2 - 5, 8):
            rx = tree_x + r_i + int(math.sin(r_i + frame_idx*0.05) * 3)
            draw.line([(rx, tree_y - trunk_h), (rx + int(r_i*0.2), tree_y)], fill=(45, 30, 20), width=3)

        # Hanging Aerial Prop Roots (Columnar roots descending from branches)
        for prop_i in range(-140, 145, 25):
            px = tree_x + prop_i + cam_offset_x
            py_top = tree_y - trunk_h + int(abs(prop_i) * 0.3)
            draw.line([(px, py_top), (px + int(prop_i*0.1), tree_y + 10)], fill=(75, 52, 35), width=4)

        # 5. Massive Sprawling Banyan Canopy (Layered Deep Green Foliage)
        canopy_r = 210
        canopy_cy = tree_y - trunk_h - 20
        
        # Background Canopy Shadow Layer
        draw.ellipse([tree_x - canopy_r - 20, canopy_cy - 100, tree_x + canopy_r + 20, canopy_cy + 90], fill=(15, 48, 18))
        
        # Midground Foliage Clusters
        rng = np.random.default_rng(777)
        for _ in range(35):
            cx = tree_x + rng.integers(-canopy_r + 30, canopy_r - 30) + cam_offset_x
            cy = canopy_cy + rng.integers(-70, 70)
            cr = rng.integers(35, 75)
            # Leaf color variance: emerald green to sunlit golden green
            leaf_g = rng.integers(90, 160)
            draw.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=(25, leaf_g, 30))

        # Golden Hour Volumetric Sunbeams filtering through Canopy
        beam_img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        beam_draw = ImageDraw.Draw(beam_img)
        for b in range(5):
            bx = sun_x + (b - 2) * 60
            beam_draw.polygon([(sun_x, sun_y), (bx - 40, self.height), (bx + 40, self.height)], fill=(255, 220, 120, 30))
        beam_img = beam_img.filter(ImageFilter.GaussianBlur(radius=10))
        img.paste(beam_img, (0, 0), beam_img)

        # Smooth Post-Processing
        img = img.filter(ImageFilter.SMOOTH)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.15)
        return img

    def generate_video(self, output_mp4="/sdcard/Download/banyan_tree_360_drone.mp4"):
        print(f"[\033[95mBanyan360DroneRenderer\033[0m] Rendering {self.num_frames} frames (20s 360-degree drone orbit)...")
        
        frames = []
        for idx in range(self.num_frames):
            frame_img = self.render_banyan_frame(idx)
            frames.append(frame_img)
            if idx % 30 == 0 or idx == self.num_frames - 1:
                angle_deg = int((idx / float(self.num_frames)) * 360)
                print(f"  Rendered Frame {idx+1:03d}/{self.num_frames} | Drone Orbit Angle: {angle_deg}°")

        out_dir = os.path.dirname(output_mp4)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with tempfile.TemporaryDirectory() as tmpdir:
            for i, frame in enumerate(frames):
                frame.save(os.path.join(tmpdir, f"frame_{i:04d}.png"))
                
            cmd = [
                "ffmpeg", "-y", "-framerate", str(self.fps),
                "-i", os.path.join(tmpdir, "frame_%04d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", output_mp4
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
        print(f"[\033[92m[SUCCESS]\033[0m 20-Second 360 Drone Video Generated: {output_mp4}")
        return output_mp4

if __name__ == "__main__":
    renderer = Banyan360DroneRenderer(width=640, height=640, fps=15, duration_sec=20.0)
    out_file = renderer.generate_video("/sdcard/Download/banyan_tree_360_drone.mp4")
    print("Generated Video Size:", os.path.getsize(out_file), "bytes")
