from flask import Flask, request, render_template, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/generated'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DEFAULT_FONT_PATH = os.path.join(os.path.dirname(__file__), "font", "impact.ttf")

@app.context_processor
def inject_docker_flag():
    return {
        "docker": os.environ.get("RUNNING_IN_DOCKER") == "1"
    }

def draw_text_on_image(image: Image.Image, top_text: str, bottom_text: str) -> Image.Image:
    image = image.convert("RGB")
    draw = ImageDraw.Draw(image)
    img_width, img_height = image.size

    max_allowed_width = int(img_width * 0.98) 
    max_start_font_size = int(img_height * 0.18) 
    min_font_size = 12
    
    edge_padding = int(img_height * 0.01) 

    def get_fitted_font(text, start_size):
        current_size = start_size
        while current_size > min_font_size:
            try:
                font = ImageFont.truetype(DEFAULT_FONT_PATH, current_size)
            except OSError:
                font = ImageFont.load_default()
                
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= max_allowed_width:
                return font

            current_size -= 2 
            
        return ImageFont.truetype(DEFAULT_FONT_PATH, min_font_size)

    center_x = img_width / 2

    if top_text:
        t_text = top_text.upper()
        t_font = get_fitted_font(t_text, max_start_font_size)
        t_stroke_width = max(2, int(t_font.size / 15))
        
        draw.text(
            (center_x, edge_padding),
            t_text,
            font=t_font,
            fill="white",
            stroke_width=t_stroke_width,
            stroke_fill="black",
            anchor="mt" 
        )

    if bottom_text:
        b_text = bottom_text.upper()
        b_font = get_fitted_font(b_text, max_start_font_size)
        b_stroke_width = max(2, int(b_font.size / 15))

        draw.text(
            (center_x, img_height - edge_padding),
            b_text,
            font=b_font,
            fill="white",
            stroke_width=b_stroke_width,
            stroke_fill="black",
            anchor="mb"
        )

    return image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'image' not in request.files:
        return redirect(url_for('index'))

    file = request.files['image']
    top_text = request.form.get('top_text', '').strip()
    bottom_text = request.form.get('bottom_text', '').strip()

    if file.filename == '':
        return redirect(url_for('index'))

    try:
        img = Image.open(file.stream)
    except Exception as e:
        return f"Neveljavna slika: {e}", 400

    result_img = draw_text_on_image(img, top_text, bottom_text)

    filename = f"meme_{uuid.uuid4().hex}.jpg"
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    result_img.save(path, format='JPEG')

    return render_template('result.html', meme_url=url_for('static', filename=f'generated/{filename}'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
