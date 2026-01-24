import os
import logging
from instagrapi import Client
from dotenv import load_dotenv
from database import QuoteDatabase
from deepseek_generator import deepseek_gen

# Setup logging
logger = logging.getLogger(__name__)

class InstagramUploader:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.cl = Client()
        self.session_file = "instagram_session.json"
        self.db = QuoteDatabase()

    def login(self):
        """Logs in to Instagram, using session if available."""
        if not self.username or not self.password:
            logger.warning("Instagram credentials not found in .env")
            return False

        try:
            if os.path.exists(self.session_file):
                logger.info("Loading Instagram session...")
                self.cl.load_settings(self.session_file)
            
            # Check if session is valid
            # self.cl.get_timeline_feed() # This check is risky, might trigger challenge
            
            # Login if needed (usually instagrapi handles session reuse if settings loaded)
            # If not logged in, perform login
            # Note: instagrapi session management is complex.
            # Simplified approach:
            
            self.cl.login(self.username, self.password)
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

    def process_interactions(self):
        """Checks for new comments and DMs, replies and follows."""
        if not self.login():
            return
            
        logger.info("Processing Instagram interactions...")
        
        try:
            self._process_comments()
            # self._process_dms() # DM processing can be risky for new accounts, uncomment if needed
        except Exception as e:
            logger.error(f"Error processing interactions: {e}")

    def _process_comments(self):
        """Process recent comments on my posts"""
        try:
            my_pk = self.cl.user_id
            medias = self.cl.user_medias(my_pk, amount=5) # Check last 5 posts
            
            for media in medias:
                comments = self.cl.media_comments(media.pk, amount=10)
                
                for comment in comments:
                    # Skip my own comments
                    if str(comment.user.pk) == str(my_pk):
                        continue
                        
                    # Check if already processed
                    if self.db.is_interaction_processed('instagram', 'comment_reply', comment.pk):
                        continue
                    
                    # Generate reply
                    reply_text = deepseek_gen.generate_interaction_reply(comment.text, "comment")
                    
                    # Reply to comment
                    try:
                        self.cl.media_comment(media.pk, reply_text, replied_to_comment_id=comment.pk)
                        logger.info(f"Replied to comment {comment.pk}: {reply_text}")
                        self.db.log_interaction('instagram', 'comment_reply', comment.pk)
                        
                        # Auto-follow user
                        self._auto_follow(comment.user.pk)
                        
                    except Exception as e:
                        logger.error(f"Failed to reply to comment {comment.pk}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in _process_comments: {e}")

    def _auto_follow(self, user_pk):
        """Follows a user if not already followed (and logged)"""
        if self.db.is_interaction_processed('instagram', 'follow', user_pk):
            return
            
        try:
            self.cl.user_follow(user_pk)
            logger.info(f"Auto-followed user {user_pk}")
            self.db.log_interaction('instagram', 'follow', user_pk)
        except Exception as e:
            logger.error(f"Failed to follow user {user_pk}: {e}")

if __name__ == "__main__":
    # Test
    uploader = InstagramUploader()
    # uploader.process_interactions()
