import textwrap
import os
from PIL import Image, ImageDraw, ImageFont

def create_quote_image(quote_text, author, category, output_path="quote_image.jpg"):
    """
    Creates an image with the quote text.
    """
    # Image settings
    width = 1080
    height = 1080  # Square for Instagram
    bg_color = (0, 0, 0)  # Black
    text_color = (255, 255, 255)  # White
    
    # Create image
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Fonts
    # Try to load a nice font, otherwise default
    try:
        # Windows path for Arial
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        if not os.path.exists(font_path):
             # Linux/Docker fallback (often DejaVuSans)
             font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        
        if not os.path.exists(font_path):
            font_path = None # Use default

        if font_path:
            quote_font = ImageFont.truetype(font_path, 60)
            author_font = ImageFont.truetype(font_path, 40)
            category_font = ImageFont.truetype(font_path, 30)
        else:
            quote_font = ImageFont.load_default()
            author_font = ImageFont.load_default()
            category_font = ImageFont.load_default()
            
    except Exception as e:
        print(f"Error loading font: {e}")
        quote_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        category_font = ImageFont.load_default()

    # Wrap text
    # Estimate chars per line based on width (approximate)
    # 1080px / 30px per char (approx for size 60) ~= 36 chars
    wrapper = textwrap.TextWrapper(width=30) 
    word_list = wrapper.wrap(text=quote_text)
    caption_new = '\n'.join(word_list)

    # Calculate text size and position to center it
    # getbbox returns (left, top, right, bottom)
    bbox = draw.multiline_textbbox((0, 0), caption_new, font=quote_font, align='center')
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x_text = (width - text_width) / 2
    y_text = (height - text_height) / 2 - 50 # Move up a bit to leave room for author
    
    # Draw Quote
    draw.multiline_text((x_text, y_text), caption_new, font=quote_font, fill=text_color, align='center')
    
    # Draw Author
    if author:
        author_text = f"— {author}"
        bbox_author = draw.textbbox((0, 0), author_text, font=author_font)
        author_width = bbox_author[2] - bbox_author[0]
        
        x_author = (width - author_width) / 2
        y_author = y_text + text_height + 40
        
        draw.text((x_author, y_author), author_text, font=author_font, fill=text_color)

    # Draw Category/Footer
    footer_text = f"#{category} #WisdomDaily"
    bbox_footer = draw.textbbox((0, 0), footer_text, font=category_font)
    footer_width = bbox_footer[2] - bbox_footer[0]
    
    x_footer = (width - footer_width) / 2
    y_footer = height - 100
    
    draw.text((x_footer, y_footer), footer_text, font=category_font, fill=(150, 150, 150)) # Grey

    # Save
    img.save(output_path)
    return output_path

if __name__ == "__main__":
    # Test
    create_quote_image(
        "The only way to do great work is to love what you do.",
        "Steve Jobs",
        "motivation"
    )
    print("Test image created: quote_image.jpg")
