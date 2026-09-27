# SutraOS Sovereign Cinematic Engine (SutraCinematics)
# Direct Pixel Manifestation Engine for Ram Mandir Ayodhya -> Milky Way Logarithmic Zoom

import os
import math
import time
import tempfile
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

class SutraCinematicsEngine:
    """
    SutraCinematics: Unified Sovereign Cinematic Intelligence & Direct Pixel Engine.
    Executes Step 1 (MCM Compilation) & Step 2 (Direct Pixel Manifestation).
    """
    def __init__(self, width=640, height=640, fps=10, duration_sec=5.0):
        self.width = width
        self.height = height
        self.fps = fps
        self.duration_sec = duration_sec
        self.num_frames = int(fps * duration_sec)
        self.cx = width // 2
        self.cy = height // 2

    def compile_ram_mandir_mcm(self):
        """Step 1: Compile Master Cinematic Manifest (MCM)"""
        print("[\033[94mSutraCinematics-MCM\033[0m] Compiling Master Cinematic Manifest...")
        
        mcm = {
            "title": "Shri Ram Mandir Ayodhya to Milky Way Logarithmic Zoom",
            "scale_range": [1.5, 21.0], # 10^1.5m (30m Drone) -> 10^21m (Milky Way)
            "optics": {
                "initial_lens_mm": 24.0,
                "aperture_f_stop": 2.8,
                "shutter_angle": 180.0,
                "sensor_format": "Full Frame 35mm"
            },
            "lighting_physics": {
                "sandstone_floodlights": "2800K Warm Amber",
                "blue_hour_sky": "6500K Cool Blue",
                "sarayu_diyas": "2000K Point Lights",
                "atmosphere_rayleigh": "beta = lambda^-4 (Lapis Blue Rim)",
                "galactic_core": "100,000K O/B Stars + Interstellar Dust Absorption"
            },
            "trajectory_k": (21.0 - 1.5) / self.duration_sec
        }
        return mcm

    def render_temple_scale(self, scale_log10, frame_idx, total_frames):
        """Phase 1: Ram Mandir Drone Shot (Scale 10^1.5m -> 10^4.0m)"""
        img = Image.new("RGB", (self.width, self.height), (10, 20, 45))
        draw = ImageDraw.Draw(img)
        
        t = (4.0 - scale_log10) / 2.5 # 1.0 down to 0.0
        scale_factor = math.pow(10.0, (4.0 - scale_log10))
        
        # Twilight Blue Hour Sky Gradient
        for y in range(int(self.height * 0.6)):
            ratio = y / (self.height * 0.6)
            r = int(12 * (1 - ratio) + 35 * ratio)
            g = int(25 * (1 - ratio) + 60 * ratio)
            b = int(75 * (1 - ratio) + 140 * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
            
        # Sarayu River & Ghat Diya Lights (2000K Warm Gold Dots)
        river_y = int(self.height * 0.65)
        draw.rectangle([0, river_y, self.width, self.height], fill=(8, 18, 38))
        
        rng = np.random.default_rng(108 + frame_idx)
        diya_x = rng.integers(0, self.width, 150)
        diya_y = rng.integers(river_y, self.height, 150)
        for dx, dy in zip(diya_x, diya_y):
            draw.ellipse([dx-1, dy-1, dx+1, dy+1], fill=(255, 180, 50))
            
        # Ram Mandir Nagara Architecture (Pink Sandstone 2800K + Golden Dhwaja/Kalash)
        m_width = int(160 * scale_factor)
        m_height = int(220 * scale_factor)
        m_x = self.cx - m_width // 2
        m_y = river_y - m_height
        
        # Main Mandir Structure (Sandstone Pink-Amber)
        draw.rectangle([m_x, m_y + int(m_height*0.4), m_x + m_width, river_y], fill=(185, 105, 65))
        
        # Shikhar Spire (Tiered Pyramid)
        spire_points = [
            (self.cx, m_y),
            (m_x + int(m_width*0.2), m_y + int(m_height*0.4)),
            (m_x + int(m_width*0.8), m_y + int(m_height*0.4))
        ]
        draw.polygon(spire_points, fill=(210, 125, 75))
        
        # Golden Kalash & Dhwaja (Flag)
        kalash_r = max(2, int(8 * scale_factor))
        draw.ellipse([self.cx-kalash_r, m_y-kalash_r*2, self.cx+kalash_r, m_y], fill=(255, 215, 60))
        draw.polygon([(self.cx, m_y-kalash_r*2), (self.cx+int(15*scale_factor), m_y-kalash_r*2-int(8*scale_factor)), (self.cx, m_y-kalash_r*2-int(12*scale_factor))], fill=(255, 120, 20))
        
        # Sandstone Warm Floodlight Rim
        img = img.filter(ImageFilter.SMOOTH)
        return img

    def render_subcontinent_scale(self, scale_log10, frame_idx):
        """Phase 2: India Subcontinent & City Night-Lights Grid (Scale 10^4.0m -> 10^11.0m)"""
        img = Image.new("RGB", (self.width, self.height), (2, 5, 15))
        draw = ImageDraw.Draw(img)
        
        t = (11.0 - scale_log10) / 7.0 # 1.0 down to 0.0
        
        # Earth Curvature Limb
        earth_r = int(100 + t * 240)
        earth_cy = self.cy + int(120 * (1.0 - t))
        
        # Rayleigh Blue Atmosphere Halo
        draw.ellipse([self.cx-earth_r-12, earth_cy-earth_r-12, self.cx+earth_r+12, earth_cy+earth_r+12], fill=(20, 80, 200))
        # Earth Ocean
        draw.ellipse([self.cx-earth_r, earth_cy-earth_r, self.cx+earth_r, earth_cy+earth_r], fill=(10, 35, 95))
        
        # India Subcontinent Landmass Shape (Green/Brown)
        land_draw = ImageDraw.Draw(img)
        land_poly = [
            (self.cx - int(earth_r*0.3), earth_cy - int(earth_r*0.4)),
            (self.cx + int(earth_r*0.4), earth_cy - int(earth_r*0.3)),
            (self.cx + int(earth_r*0.1), earth_cy + int(earth_r*0.4)),
            (self.cx - int(earth_r*0.2), earth_cy + int(earth_r*0.1))
        ]
        land_draw.polygon(land_poly, fill=(25, 85, 45))
        
        # City Night Light Fibers (Golden/White LED Grid - Delhi, Ayodhya, Varanasi, Mumbai)
        rng = np.random.default_rng(200)
        for _ in range(80):
            lx = self.cx + rng.integers(-int(earth_r*0.25), int(earth_r*0.25))
            ly = earth_cy + rng.integers(-int(earth_r*0.25), int(earth_r*0.25))
            draw.ellipse([lx-1, ly-1, lx+1, ly+1], fill=(255, 210, 100))
            
        img = img.filter(ImageFilter.SMOOTH_MORE)
        return img

    def render_milkyway_scale(self, scale_log10, frame_idx):
        """Phase 3: Deep Space & Milky Way Spiral Galaxy (Scale 10^11.0m -> 10^21.0m)"""
        img = Image.new("RGB", (self.width, self.height), (1, 3, 10))
        draw = ImageDraw.Draw(img)
        
        zoom = math.pow(10.0, (21.0 - scale_log10) * 0.35)
        
        # Background Starfield
        rng = np.random.default_rng(300)
        sx = rng.integers(0, self.width, 250)
        sy = rng.integers(0, self.height, 250)
        sb = rng.integers(120, 255, 250)
        for x, y, b in zip(sx, sy, sb):
            draw.point((int(x), int(y)), fill=(b, b, min(255, b+50)))
            
        # Milky Way 4-Arm Spiral
        galaxy_r = int(160 * zoom)
        num_arms = 4
        num_dots = 1000
        
        for i in range(num_dots):
            r = (i / float(num_dots)) * galaxy_r
            angle = (i % num_arms) * (2 * math.pi / num_arms) + (r * 0.035)
            
            px = int(self.cx + r * math.cos(angle))
            py = int(self.cy + r * math.sin(angle))
            
            dist = math.sqrt((px-self.cx)**2 + (py-self.cy)**2) / (galaxy_r + 1e-5)
            bright = max(0, int(255 * (1.0 - dist)))
            
            if 0 <= px < self.width and 0 <= py < self.height:
                draw.ellipse([px-1, py-1, px+1, py+1], fill=(min(255, bright+90), min(255, int(bright*0.85)+50), min(255, int(bright*0.95)+120)))
                
        # Sagittarius A* Core Glow
        core_r = max(2, int(20 * zoom))
        draw.ellipse([self.cx-core_r, self.cy-core_r, self.cx+core_r, self.cy+core_r], fill=(255, 245, 210))
        
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
        return img

    def execute_direct_manifestation(self, mcm, output_mp4="/sdcard/Download/sutra_ram_mandir_cosmic_zoom.mp4"):
        """Step 2: Direct Pixel Manifestation Synthesis"""
        print(f"[\033[93mSutraCinematics-Engine\033[0m] Executing Direct Pixel Manifestation ({self.num_frames} frames)...")
        
        scales = np.linspace(mcm["scale_range"][0], mcm["scale_range"][1], self.num_frames)
        frames = []
        
        for idx, scale_val in enumerate(scales):
            if scale_val < 4.0:
                frame_img = self.render_temple_scale(scale_val, idx, self.num_frames)
            elif scale_val < 11.0:
                frame_img = self.render_subcontinent_scale(scale_val, idx)
            else:
                frame_img = self.render_milkyway_scale(scale_val, idx)
                
            frames.append(frame_img)
            
            if idx % 10 == 0 or idx == self.num_frames - 1:
                print(f"  Manifested Frame {idx+1:02d}/{self.num_frames} | Log10 Scale: 10^{scale_val:.2f}m")
                
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
            
        print(f"[\033[92m[SUCCESS]\033[0m Direct Pixel Manifestation Complete: {output_mp4}")
        return output_mp4

if __name__ == "__main__":
    engine = SutraCinematicsEngine(width=640, height=640, fps=15, duration_sec=20.0)
    mcm = engine.compile_ram_mandir_mcm()
    out_video = engine.execute_direct_manifestation(mcm, "/sdcard/Download/sutra_ram_mandir_cosmic_zoom_20s.mp4")
    print("Generated 20s Video Size:", os.path.getsize(out_video), "bytes")

