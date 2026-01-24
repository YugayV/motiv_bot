import os
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip

def create_quote_video(image_path, output_path="quote_video.mp4", duration=5):
    """
    Creates a simple video from an image for TikTok/Reels.
    """
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Create video clip from image
        clip = ImageClip(image_path).set_duration(duration)
        
        # Optional: Add background music if available
        # music_path = "background_music.mp3"
        # if os.path.exists(music_path):
        #     audio = AudioFileClip(music_path).subclip(0, duration)
        #     clip = clip.set_audio(audio)
        
        # Resize for TikTok (1080x1920 is best, but 1080x1080 works)
        # Our image is 1080x1080. Let's keep it square or add padding?
        # TikTok supports square, so we keep it simple.
        
        clip.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        return output_path
    except Exception as e:
        print(f"Error creating video: {e}")
        return None

if __name__ == "__main__":
    # Test
    # create_quote_video("quote_image.jpg")
    pass
