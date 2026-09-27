# SutraVak Autonomous Video Producer Engine for SutraOS
import os
import sys
import math
import subprocess
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import gtts

class SutraVakProducer:
    """
    SutraVak Autonomous Video Producer:
    Complete end-to-end AI Video Creation Engine for SutraOS.
    Takes topic -> Plans scenes -> Fetches/Generates visual assets ->
    Synthesizes voiceover -> Generates kinetic motion & synced captions ->
    Renders final broadcast-quality MP4 video reel.
    """
    def __init__(self, width=1080, height=1920, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.scratch_dir = "/data/data/com.termux/files/home/.gemini/antigravity-cli/brain/7705a0d4-ce76-4025-beed-6751c192fb11/scratch"
        os.makedirs(self.scratch_dir, exist_ok=True)

    def log(self, msg):
        print(f"[\033[93mSutraVakEngine\033[0m] {msg}")

    def fetch_visual_asset(self, scene_idx, visual_prompt):
        """Fetches/generates scene visual asset"""
        img_path = os.path.join(self.scratch_dir, f"scene_{scene_idx}.jpg")
        encoded = urllib.parse.quote(f"cinematic {visual_prompt} dramatic golden lighting 8k hyperrealistic vertical reel")
        url = f"https://image.pollinations.ai/prompt/{encoded}"
        
        self.log(f"Scene {scene_idx}: Fetching visual asset for '{visual_prompt}'...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                with open(img_path, 'wb') as f:
                    f.write(data)
            img = Image.open(img_path).convert('RGB')
        except Exception as e:
            self.log(f"Asset fetch fallback ({e}), creating procedural visual background...")
            img = Image.new('RGB', (self.width, self.height), color=(10, 25, 47))
            
        return img.resize((self.width, self.height), Image.Resampling.LANCZOS)

    def generate_voiceover(self, scene_idx, text_narration):
        """Generates natural voiceover audio for scene"""
        audio_path = os.path.join(self.scratch_dir, f"audio_{scene_idx}.mp3")
        self.log(f"Scene {scene_idx}: Generating voiceover narration...")
        tts = gtts.gTTS(text=text_narration, lang='hi')
        tts.save(audio_path)
        
        # Get audio duration via FFprobe
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        duration = float(res.stdout.strip() or 3.0)
        return audio_path, duration

    def produce_video(self, story_scenes, output_path="/sdcard/Download/sutravak_produced_reel.mp4"):
        self.log(f"Starting SutraVak Autonomous Production for {len(story_scenes)} scenes...")
        
        scene_videos = []
        for idx, scene in enumerate(story_scenes, 1):
            visual_prompt = scene['visual']
            narration_text = scene['narration']
            subtitle_text = scene['subtitle']
            
            # Step 1: Visual & Voiceover Generation
            base_img = self.fetch_visual_asset(idx, visual_prompt)
            audio_path, duration_sec = self.generate_voiceover(idx, narration_text)
            
            # Add padding to duration for smooth transition
            scene_duration = duration_sec + 0.5
            total_frames = int(scene_duration * self.fps)
            
            scene_raw_path = os.path.join(self.scratch_dir, f"scene_raw_{idx}.mp4")
            scene_video_path = os.path.join(self.scratch_dir, f"scene_final_{idx}.mp4")
            
            # Setup FFmpeg raw video pipe
            cmd_video = [
                'ffmpeg', '-y',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-s', f'{self.width}x{self.height}',
                '-pix_fmt', 'rgb24',
                '-r', str(self.fps),
                '-i', '-',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'fast',
                scene_raw_path
            ]
            
            pipe = subprocess.Popen(cmd_video, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            for f_idx in range(total_frames):
                progress = f_idx / float(total_frames)
                
                # Apply 3D Camera Pan/Zoom motion
                zoom = 1.0 + 0.12 * math.sin(progress * math.pi)
                crop_w = int(self.width / zoom)
                crop_h = int(self.height / zoom)
                left = (self.width - crop_w) // 2
                top = (self.height - crop_h) // 2
                
                cropped = base_img.crop((left, top, left + crop_w, top + crop_h))
                frame_img = cropped.resize((self.width, self.height), Image.Resampling.LANCZOS)
                
                draw = ImageDraw.Draw(frame_img)
                
                # Draw Kinetic Subtitle Card Overlay
                try:
                    font_path = "/data/data/com.termux/files/usr/share/fonts/TTF/NotoSerifDevanagari-Bold.ttf"
                    if os.path.exists(font_path):
                        font_sub = ImageFont.truetype(font_path, 44)
                    else:
                        font_sub = ImageFont.load_default()
                        
                    banner_y = self.height - 260
                    draw.rectangle([60, banner_y, self.width - 60, banner_y + 130], fill=(10, 25, 47))
                    
                    bbox_s = font_sub.getbbox(subtitle_text)
                    tw_s = bbox_s[2] - bbox_s[0]
                    draw.text((self.width // 2 - tw_s // 2, banner_y + 35), subtitle_text, fill=(245, 240, 220), font=font_sub)
                except Exception:
                    pass
                    
                pipe.stdin.write(frame_img.tobytes())
                
            pipe.stdin.close()
            pipe.wait()

            # Mux narration audio with video stream
            cmd_mux = [
                'ffmpeg', '-y',
                '-i', scene_raw_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                scene_video_path
            ]
            subprocess.run(cmd_mux, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            scene_videos.append(scene_video_path)
            self.log(f"Scene {idx} rendered & audio synced -> {scene_video_path}")

        # Step 4: Concatenate Scene Videos into Final Reel
        self.log("Concatenating scenes into final video reel...")
        concat_list_path = os.path.join(self.scratch_dir, "concat_list.txt")
        with open(concat_list_path, 'w') as f:
            for sv in scene_videos:
                f.write(f"file '{sv}'\n")
                
        subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_list_path, '-c', 'copy', output_path], check=True)
        self.log(f"\033[92m[SUCCESS] SutraVak Production Complete: {output_path}\033[0m")
        return output_path

if __name__ == "__main__":
    producer = SutraVakProducer(width=1080, height=1920, fps=30)
    
    # Story script for SutraVak
    story = [
        {
            "visual": "ancient sanskrit sage looking at glowing universe galaxy cosmic energy",
            "narration": "प्राचीन भारतीय विज्ञान में ब्रह्मांड की उत्पत्ति का गहरा रहस्य छिपा हुआ है।",
            "subtitle": "सृष्टि का अनंत रहस्य"
        },
        {
            "visual": "futuristic glowing mandala cybernetic quantum code matrix",
            "narration": "चेतना और ऊर्जा के संतुलन से ही इस जगत का निर्माण होता है।",
            "subtitle": "चेतना और ऊर्जा का संतुलन"
        },
        {
            "visual": "golden sanskrit text burning aura in dark void",
            "narration": "सूत्रावाक - ज्ञान और तकनीक का अनूठा संगम।",
            "subtitle": "सूत्रावाक • SUTRA OS"
        }
    ]
    
    out = producer.produce_video(story, output_path="/sdcard/Download/sutravak_produced_reel.mp4")
    print("Final Video Size:", os.path.getsize(out), "bytes")
