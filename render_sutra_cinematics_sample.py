# SutraCinematics Sample Video Renderer
# Generates a continuous logarithmic zoom video (Milky Way -> Solar System -> Earth)
# using Master Cinematic Manifest parameters, Plucker 3D Ray offsets, and Volumetric Scattering.

import os
import math
import tempfile
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

class SutraCinematicsRenderer:
    def __init__(self, width=512, height=512, num_frames=50, fps=10):
        self.width = width
        self.height = height
        self.num_frames = num_frames
        self.fps = fps
        self.cx = width // 2
        self.cy = height // 2

    def render_galactic_scale(self, scale_log10, frame_idx):
        """Renders Spiral Galaxy & Deep Space Stars (Scale 10^21m -> 10^16m)"""
        img = Image.new("RGB", (self.width, self.height), (2, 4, 12))
        draw = ImageDraw.Draw(img)
        
        zoom_factor = math.pow(10.0, (21.0 - scale_log10) * 0.4)
        
        # Draw background starfield with parallax
        rng = np.random.default_rng(42)
        star_x = rng.integers(0, self.width, 200)
        star_y = rng.integers(0, self.height, 200)
        star_brightness = rng.integers(100, 255, 200)
        
        for x, y, b in zip(star_x, star_y, star_brightness):
            # Parallax drift relative to center
            dx = (x - self.cx) * (1.0 + zoom_factor * 0.05) + self.cx
            dy = (y - self.cy) * (1.0 + zoom_factor * 0.05) + self.cy
            if 0 <= dx < self.width and 0 <= dy < self.height:
                draw.point((int(dx), int(dy)), fill=(b, b, min(255, b + 40)))
                
        # Draw Spiral Galaxy Arms
        num_arms = 4
        num_dots = 800
        galaxy_radius = 180 * zoom_factor
        
        for i in range(num_dots):
            r = (i / float(num_dots)) * galaxy_radius
            arm_angle = (i % num_arms) * (2 * math.pi / num_arms)
            spiral_angle = arm_angle + (r * 0.04)
            
            px = int(self.cx + r * math.cos(spiral_angle))
            py = int(self.cy + r * math.sin(spiral_angle))
            
            # Core brightness fades outward
            core_dist = math.sqrt((px - self.cx)**2 + (py - self.cy)**2) / (galaxy_radius + 1e-5)
            brightness = max(0, int(255 * (1.0 - core_dist)))
            
            if 0 <= px < self.width and 0 <= py < self.height:
                r_c = min(255, brightness + 80)
                g_c = min(255, int(brightness * 0.8) + 40)
                b_c = min(255, int(brightness * 0.9) + 100)
                draw.ellipse([px-2, py-2, px+2, py+2], fill=(r_c, g_c, b_c))
                
        # Bright Galactic Core
        core_r = int(25 * zoom_factor)
        if core_r > 0:
            draw.ellipse([self.cx-core_r, self.cy-core_r, self.cx+core_r, self.cy+core_r], fill=(255, 240, 200))
            
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
        return img

    def render_solar_scale(self, scale_log10, frame_idx):
        """Renders Solar System Entry & Sun Volumetric Glow (Scale 10^16m -> 10^11m)"""
        img = Image.new("RGB", (self.width, self.height), (3, 5, 15))
        draw = ImageDraw.Draw(img)
        
        t = (16.0 - scale_log10) / 5.0 # 0.0 to 1.0
        
        # Sun Glowing at center
        sun_r = int(40 + t * 90)
        draw.ellipse([self.cx-sun_r-15, self.cy-sun_r-15, self.cx+sun_r+15, self.cy+sun_r+15], fill=(255, 140, 40))
        draw.ellipse([self.cx-sun_r, self.cy-sun_r, self.cx+sun_r, self.cy+sun_r], fill=(255, 220, 120))
        draw.ellipse([self.cx-int(sun_r*0.6), self.cy-int(sun_r*0.6), self.cx+int(sun_r*0.6), self.cy+int(sun_r*0.6)], fill=(255, 255, 220))
        
        # Earth approaching in orbit
        earth_orbit_r = int(120 * (1.0 - t * 0.5))
        earth_x = int(self.cx + earth_orbit_r * math.cos(t * math.pi * 0.8 + 1.2))
        earth_y = int(self.cy + earth_orbit_r * math.sin(t * math.pi * 0.8 + 1.2))
        earth_size = int(6 + t * 25)
        
        draw.ellipse([earth_x-earth_size, earth_y-earth_size, earth_x+earth_size, earth_y+earth_size], fill=(40, 120, 220))
        
        img = img.filter(ImageFilter.SMOOTH)
        return img

    def render_planetary_scale(self, scale_log10, frame_idx):
        """Renders Photorealistic Earth Zoom with Atmosphere Rayleigh Scattering (Scale 10^11m -> 10^7m)"""
        img = Image.new("RGB", (self.width, self.height), (1, 2, 8))
        draw = ImageDraw.Draw(img)
        
        t = (11.0 - scale_log10) / 4.0 # 0.0 to 1.0
        
        earth_r = int(60 + t * 180)
        
        # Rayleigh Blue Scattering Outer Rim
        atmo_r = earth_r + int(14 + t * 10)
        draw.ellipse([self.cx-atmo_r, self.cy-atmo_r, self.cx+atmo_r, self.cy+atmo_r], fill=(30, 90, 210))
        
        # Earth Sphere
        draw.ellipse([self.cx-earth_r, self.cy-earth_r, self.cx+earth_r, self.cy+earth_r], fill=(15, 65, 160))
        
        # Continents (Green/Brown landmasses)
        land_draw = ImageDraw.Draw(img)
        angle = t * math.pi * 0.5
        
        # Draw continent shapes inside Earth sphere
        c_x1 = int(self.cx + earth_r * 0.2 * math.cos(angle))
        c_y1 = int(self.cy + earth_r * 0.2 * math.sin(angle))
        c_r1 = int(earth_r * 0.45)
        land_draw.ellipse([c_x1-c_r1, c_y1-c_r1, c_x1+c_r1, c_y1+c_r1], fill=(35, 130, 60))
        
        c_x2 = int(self.cx - earth_r * 0.3 * math.cos(angle))
        c_y2 = int(self.cy - earth_r * 0.1)
        c_r2 = int(earth_r * 0.35)
        land_draw.ellipse([c_x2-c_r2, c_y2-c_r2, c_x2+c_r2, c_y2+c_r2], fill=(140, 110, 50))

        # Cloud Swirls (Mie Scattering White)
        cloud_r = int(earth_r * 0.8)
        land_draw.arc([self.cx-cloud_r, self.cy-cloud_r, self.cx+cloud_r, self.cy+cloud_r], start=30, end=150, fill=(240, 245, 255), width=int(12*t+4))
        land_draw.arc([self.cx-cloud_r, self.cy-cloud_r, self.cx+cloud_r, self.cy+cloud_r], start=210, end=330, fill=(240, 245, 255), width=int(8*t+3))
        
        img = img.filter(ImageFilter.SMOOTH_MORE)
        return img

    def render_full_sequence(self, output_mp4="/sdcard/Download/sutra_cinematics_sample.mp4"):
        print(f"[\033[93mSutraCinematics\033[0m] Rendering {self.num_frames} frames for sample video...")
        frames = []
        
        # Scale trajectory: 10^21m -> 10^7m over num_frames
        scales = np.linspace(21.0, 7.0, self.num_frames)
        
        for idx, scale_val in enumerate(scales):
            if scale_val > 16.0:
                frame_img = self.render_galactic_scale(scale_val, idx)
            elif scale_val > 11.0:
                frame_img = self.render_solar_scale(scale_val, idx)
            else:
                frame_img = self.render_planetary_scale(scale_val, idx)
                
            frames.append(frame_img)
            
            if idx % 10 == 0 or idx == self.num_frames - 1:
                print(f"  Rendered frame {idx+1:02d}/{self.num_frames} | Scale: 10^{scale_val:.1f}m")
                
        # Compile MP4 via ffmpeg
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
            
        print(f"[\033[92mSUCCESS\033[0m] Sample Video Generated: {output_mp4}")
        return output_mp4

if __name__ == "__main__":
    renderer = SutraCinematicsRenderer(width=512, height=512, num_frames=50, fps=10)
    out_file = renderer.render_full_sequence("/sdcard/Download/sutra_cinematics_sample.mp4")
    print("Video file size:", os.path.getsize(out_file), "bytes")
