import os
import logging
from instagrapi import Client
from dotenv import load_dotenv

# Setup logging
logger = logging.getLogger(__name__)

class InstagramUploader:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.cl = Client()
        self.session_file = "instagram_session.json"

    def login(self):
        """Logs in to Instagram, using session if available."""
        if not self.username or not self.password:
            logger.warning("Instagram credentials not found in .env")
            return False

        try:
            if os.path.exists(self.session_file):
                logger.info("Loading Instagram session...")
                self.cl.load_settings(self.session_file)
            
            # Check if session is valid (this is a simplified check)
            # Login if needed
            self.cl.login(self.username, self.password)
            
            # Save session
            self.cl.dump_settings(self.session_file)
            logger.info("Instagram login successful")
            return True
        except Exception as e:
            logger.error(f"Instagram login failed: {e}")
            return False

    def upload_photo(self, image_path, caption):
        """Uploads a photo to Instagram."""
        if not self.login():
            return False
            
        try:
            logger.info(f"Uploading to Instagram: {image_path}")
            media = self.cl.photo_upload(
                image_path, 
                caption=caption
            )
            logger.info(f"Uploaded to Instagram successfully. Media PK: {media.pk}")
            return True
        except Exception as e:
            logger.error(f"Instagram upload failed: {e}")
            return False

if __name__ == "__main__":
    # Test
    uploader = InstagramUploader()
    # uploader.upload_photo("quote_image.jpg", "Test caption #test")
