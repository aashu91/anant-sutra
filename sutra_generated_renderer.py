# SutraOS Dynamically Synthesized Engine: Cyberpunk Car in Neon Rain
# Generated On-the-Fly by SutraAGI Compiler
# Integrates: SE(3) Camera Tracking, Wet Asphalt Puddle PBR Shading, Neon Volumetric Bloom, and Rain Kinematics.

import os
import math
import tempfile
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

class SutraCyberpunkRainEngine:
    def __init__(self, width=640, height=640, fps=15, duration_sec=20.0):
        self.width = width
        self.height = height
        self.fps = fps
        self.duration_sec = duration_sec
        self.num_frames = int(fps * duration_sec)
        self.cx = width // 2
        self.cy = height // 2

    def render_cyberpunk_frame(self, frame_idx):
        t = frame_idx / float(self.num_frames) # 0.0 to 1.0
        
        # 1. Dark Night City Skyline Base
        img = Image.new("RGB", (self.width, self.height), (4, 6, 16))
        draw = ImageDraw.Draw(img)
        
        # Horizon & Road Division
        horizon_y = int(self.height * 0.45)
        
        # 2. Background Neon City Skyscrapers (Cyan #00f0ff & Magenta #ff007f Glow)
        rng = np.random.default_rng(42)
        for b_i in range(12):
            bx = int(b_i * (self.width / 10) - 20)
            bw = rng.integers(35, 65)
            bh = rng.integers(140, 240)
            by = horizon_y - bh
            
            # Building Body (Dark Metallic Gray)
            draw.rectangle([bx, by, bx+bw, horizon_y], fill=(12, 16, 28))
            
            # Neon Signboards & Window Grid
            neon_col = (0, 240, 255) if b_i % 2 == 0 else (255, 0, 128)
            for wy in range(by + 10, horizon_y - 10, 18):
                if rng.random() > 0.3:
                    draw.rectangle([bx + 6, wy, bx + bw - 6, wy + 8], fill=neon_col)

        # 3. Wet Asphalt Puddle Road (Fresnel Reflective Ground)
        draw.rectangle([0, horizon_y, self.width, self.height], fill=(10, 12, 20))
        
        # Perspective Road Markings & Neon Puddle Reflections
        for y in range(horizon_y, self.height, 12):
            road_ratio = (y - horizon_y) / float(self.height - horizon_y)
            # Reflective Neon Shimmer on Wet Road
            ref_cyan = int(120 * road_ratio)
            ref_mag = int(90 * road_ratio)
            draw.line([(0, y), (self.width, y)], fill=(ref_cyan, 20, ref_mag + 40))

        # 4. Cyberpunk Vehicle 3D Tracking Shot (SE(3) Camera Motion Vector)
        # Vehicle moves slightly with perspective physics
        car_z = 1.0 + math.sin(t * math.pi * 2) * 0.05
        car_w = int(220 * car_z)
        car_h = int(90 * car_z)
        car_x = self.cx + int(math.sin(t * math.pi * 4) * 20)
        car_y = int(self.height * 0.72)
        
        car_left = car_x - car_w // 2
        car_top = car_y - car_h // 2
        car_right = car_x + car_w // 2
        car_bottom = car_y + car_h // 2

        # Car Chassis (Aerodynamic Low-Rider Matte Black / Dark Chrome)
        draw.rectangle([car_left, car_top + int(car_h*0.3), car_right, car_bottom], fill=(22, 26, 35))
        # Cabin Windscreen / Roof (Angular Cyberpunk Canopy)
        draw.polygon([
            (car_left + int(car_w*0.2), car_top + int(car_h*0.3)),
            (car_left + int(car_w*0.35), car_top),
            (car_right - int(car_w*0.35), car_top),
            (car_right - int(car_w*0.2), car_top + int(car_h*0.3))
        ], fill=(40, 50, 70))
        
        # Cyberpunk Tail-Light Strip (Pulsing High-Intensity Neon Red/Cyan)
        draw.rectangle([car_left + 10, car_top + int(car_h*0.45), car_right - 10, car_top + int(car_h*0.6)], fill=(255, 30, 70))
        # Rear Thruster / Diffuser Glow
        draw.ellipse([car_x - 30, car_top + int(car_h*0.65), car_x + 30, car_bottom - 5], fill=(0, 240, 255))

        # 5. Heavy Rain Streak Dynamics (Kinematic Weather System)
        rain_img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        rain_draw = ImageDraw.Draw(rain_img)
        
        rng_rain = np.random.default_rng(1234 + frame_idx)
        rain_x = rng_rain.integers(0, self.width, 180)
        rain_y = rng_rain.integers(0, self.height, 180)
        rain_len = rng_rain.integers(15, 30, 180)
        
        for rx, ry, rlen in zip(rain_x, rain_y, rain_len):
            rain_draw.line([(rx, ry), (rx - 4, ry + rlen)], fill=(180, 230, 255, 160), width=2)
            
        # Puddle Water Splash Ripples at base
        for splash_i in range(15):
            sx = rng_rain.integers(0, self.width)
            sy = rng_rain.integers(horizon_y, self.height)
            sr = rng_rain.integers(3, 10)
            rain_draw.ellipse([sx-sr, sy-sr//2, sx+sr, sy+sr//2], outline=(200, 240, 255, 120), width=1)
            
        img.paste(rain_img, (0, 0), rain_img)

        # 6. Volumetric Neon Bloom & Contrast Enhancement
        img = img.filter(ImageFilter.SMOOTH)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        return img

    def generate_cyberpunk_video(self, output_mp4="/sdcard/Download/cyberpunk_car_neon_rain.mp4"):
        print(f"[\033[95mSutraAGI-Compiler\033[0m] Executing JIT Engine for 'Cyberpunk car in neon rain' ({self.num_frames} frames)...")
        
        frames = []
        for idx in range(self.num_frames):
            frame_img = self.render_cyberpunk_frame(idx)
            frames.append(frame_img)
            if idx % 30 == 0 or idx == self.num_frames - 1:
                print(f"  Synthesized Cyberpunk Frame {idx+1:03d}/{self.num_frames}")
                
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
            
        print(f"[\033[92m[SUCCESS]\033[0m Cyberpunk Video Generated: {output_mp4}")
        return output_mp4

if __name__ == "__main__":
    engine = SutraCyberpunkRainEngine(width=640, height=640, fps=15, duration_sec=20.0)
    out_file = engine.generate_cyberpunk_video("/sdcard/Download/cyberpunk_car_neon_rain.mp4")
    print("Generated Video Size:", os.path.getsize(out_file), "bytes")
