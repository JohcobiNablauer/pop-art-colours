import streamlit as st
from PIL import Image
import numpy as np

class PopArtApp:
    def __init__(self):
        self.original = self.alpha = self.greyscaled = self.recoloured = None
        self.colour_map = {}

    def run(self):
        st.set_page_config(page_title='Pop Art Colours', page_icon='🎨')
        
        st.title('Pop Art Colours')
        self.load_section()
        
        if self.original is not None:
            self.edit_section()
            self.preview_section()


    def load_section(self):
        st.subheader('Load')

        if (upload := st.file_uploader('Insert image:', ['jpeg', 'jpg', 'png'])):
            img =  np.array(Image.open(upload).convert('RGBA'))
            self.original, self.alpha = img[:, :, :3], img[:, :, 3]

    def edit_section(self):
        st.markdown('---')
        st.subheader('Edit')

        self.greyscale()
        self.hex_input()
        self.recolour()
    
    def preview_section(self):
        st.markdown('---')
        st.subheader('Preview')

        imgs = [self.original, self.greyscaled, self.recoloured]
        suffixes = ['original', 'greyscaled', 'recoloured']
        cols = st.columns([1, 1, 1])

        for i, (col, suffix, rgb) in enumerate(zip(cols, suffixes, imgs)):
            rgb = np.stack([rgb] * 3, axis=-1) if i == 1 else rgb
            rgba = np.dstack((rgb, self.alpha))

            img = Image.fromarray(rgba, mode='RGBA')
            col.image(img, caption=f'{suffix.capitalize()} image')

    def greyscale(self):
        array = np.array(Image.fromarray(self.original).convert('L'))

        greys = np.linspace(0, 255, st.slider('Number of grayscales:', 2, 20, 5), dtype=np.uint8)
        indices = np.argmin(np.abs(array[:, :, None] - greys), axis=2)

        self.greyscaled = greys[indices].astype(np.uint8)
        self.colour_map = {int(g): (g, g, g) for g in greys}

    def hex_input(self):
        def get_square(colour):
            return Image.new('RGB', (40, 40), colour)

        def is_hex(val):
            try:
                return len(val) == 7 and int(val.lstrip('#'), 16)
            except ValueError:
                return False
         
        for grey, (r, g, b) in self.colour_map.items():
            col1, col2, col3 = st.columns([1, 1, 4])
            col1.image(get_square((grey, grey, grey)), use_container_width=False)

            hex_value = f'#{r:02x}{g:02x}{b:02x}'
            hex_input = col3.text_input('HEX: ', hex_value, 7, label_visibility='collapsed')
            if hex_input != hex_value:
                if is_hex(hex_input):
                    rgb = tuple(np.uint8(int(hex_input.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))
                    self.colour_map[grey] = rgb
                    col2.image(get_square(rgb), use_container_width=False)
                else:
                    col3.error('❌ Invalid input! Value needs to be in HEX form: #abcdef')
                    col3.warning('⚠️ Allowed characters: 0123456789abcdefABCDEF')

    def recolour(self):
        self.recoloured = np.array([self.colour_map[int(g)] for g in self.greyscaled.flatten()]).reshape(self.greyscaled.shape + (3,))
    

if __name__ == '__main__':
    app = PopArtApp()
    app.run()
