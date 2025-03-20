# painter_streamlit.py
import os
import shutil
from pathlib import Path
from PIL import Image, ImageEnhance
import streamlit as st
import utils.tag_analysis
import utils.file_analysis
import utils.progress_bar

# Set page config
st.set_page_config(
    page_title="Painter Progress Dashboard",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Reuse thumbnail generation functions from thumbnail_bar.py
def generate_thumbnail(image_path: Path, output_folder_name=Path("thumbnails")):
    def crop_max_square(pil_img):
        def crop_center(pil_img, crop_width, crop_height):
            img_width, img_height = pil_img.size
            return pil_img.crop(((img_width - crop_width) // 2,
                                (img_height - crop_height) // 2,
                                (img_width + crop_width) // 2,
                                (img_height + crop_height) // 2))
        return crop_center(pil_img, min(pil_img.size)//6, min(pil_img.size)//6)
    
    with Image.open(image_path) as im:
        im = crop_max_square(im)
        if not tag_analysis.has_tags(image_path.name, ['colour']):
            im = im.convert("L")
        im = ImageEnhance.Contrast(im).enhance(1.5)
        im.thumbnail((12, 12))
        im.save(output_folder_name/image_path.name)

def copy_folder_as_thumbnails(source_path, thumbnail_folder_path):
    if thumbnail_folder_path.exists():
        shutil.rmtree(thumbnail_folder_path)
    os.makedirs(thumbnail_folder_path)
    for root, dirs, files in os.walk(source_path):
        if ".stfolder/" in dirs:
            dirs.remove(".stfolder/")
        for file in files:
            if file.endswith((".jpg", ".png")):
                generate_thumbnail(Path(root)/file, Path(thumbnail_folder_path))
            elif file.endswith(".filetags"):
                shutil.copy2(Path(root)/file, thumbnail_folder_path)

# Data loading and processing
@st.cache_resource(show_spinner="Loading artist data...")
def load_data():
    home_dir = Path(os.getenv("HOME"))
    
    # Generate thumbnails
    sketch_path = home_dir/"Drawing/Sketch Track"
    digital_path = home_dir/"Drawing/Digital Drawing/PNG"
    thumb_dir = Path("streamlit_thumbnails")
    
    with st.spinner("Generating sketchbook thumbnails..."):
        copy_folder_as_thumbnails(sketch_path, thumb_dir)
    
    with st.spinner("Generating digital art thumbnails..."):
        copy_folder_as_thumbnails(digital_path, thumb_dir/"digital")

    # Process data
    try:
        sketch_data = tag_analysis.get_tag_filename_dict(thumb_dir/".filetags", 
                                                       [thumb_dir], ['#sketchbook'])
        sketch_data['dir_count'] = file_analysis.count_dirs([sketch_path], ["[.stfolder/]"])
        
        digital_data = tag_analysis.get_tag_filename_dict(thumb_dir/"digital/.filetags",
                                                        [thumb_dir/"digital"], ['#digital'])
        digital_data.pop('dir_count', None)

        # Combine images
        for root, _, files in os.walk(thumb_dir/"digital"):
            for file in files:
                if file.endswith((".jpg", ".png")):
                    shutil.copy2(Path(root)/file, thumb_dir)

        if (thumb_dir/"digital").exists():
            shutil.rmtree(thumb_dir/"digital")

        skill_data = tag_analysis.get_tag_filename_dict(thumb_dir/".filetags",
                                                      [thumb_dir], ['#skill'])
        skill_data.pop('dir_count', None)
        skill_data.pop('file_count', None)

        overall_data = {'Total_count': len(list(thumb_dir.glob("*.[jp][pn]g")))}
        
        return {
            "sketchbook": sketch_data,
            "digital": digital_data,
            "skill": skill_data,
            "overall": overall_data,
            "thumbnails": sorted(thumb_dir.glob("*.[jp][pn]g"), key=os.path.getmtime)
        }
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return None

# Visualization components
def render_progress_section(title, data, thumb_dir):
    exp = len(data.get("file_count", []))
    level = progress_bar.experience_to_level(exp)
    level_cap = progress_bar.level_cap(exp)
    level_bottom = progress_bar.level_bottom(exp)
    exp_since = exp - level_bottom
    exp_required = level_cap - level_bottom
    filled = round(exp_since / exp_required * 24) if exp_required else 0
    
    cols = st.columns([1, 4])
    with cols[0]:
        st.subheader(f"{title} Progress")
        st.metric("Current Level", f"LVL {level}")
        st.metric("Experience", f"{exp} XP")
        st.metric("Next Level", f"{level_cap - exp} XP needed")
    
    with cols[1]:
        st.markdown(f"**Progress to next level ({filled}/24)**")
        col_list = st.columns(24)
        thumbnails = data.get("file_count", [])[-filled:] if filled > 0 else []
        
        for idx in range(24):
            with col_list[idx]:
                if idx < len(thumbnails):
                    img = Image.open(thumb_dir/thumbnails[idx])
                    st.image(img, use_container_width=True)
                else:
                    st.empty()

def render_gallery(thumbnails):
    cols = st.columns(8)
    for idx, thumb in enumerate(thumbnails):
        with cols[idx % 8]:
            img = Image.open(thumb)
            st.image(img, caption=thumb.name, use_container_width=True)

# Main app
def main():
    st.title("🎨 Digital Painter Progress Tracker")
    st.markdown("---")
    
    data = load_data()
    if not data:
        st.stop()
    
    # Overview section
    with st.container():
        st.header("📊 Overview Statistics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Artworks", data["overall"]["Total_count"])
        col2.metric("Sketchbook Pages", len(data["sketchbook"].get("file_count", [])))
        col3.metric("Digital Works", len(data["digital"].get("file_count", [])))
    
    # Progress sections
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📓 Sketchbook Progress", "💻 Digital Art Progress", "🌟 Skills"])
    
    with tab1:
        render_progress_section("Sketchbook", data["sketchbook"], Path("streamlit_thumbnails"))
        if "dir_count" in data["sketchbook"]:
            st.markdown(f"**Books Used:** {data['sketchbook']['dir_count']}")
    
    with tab2:
        render_progress_section("Digital Art", data["digital"], Path("streamlit_thumbnails"))
    
    with tab3:
        st.subheader("Skill Progression")
        skill_levels = {
            "Sketching": progress_bar.experience_to_level(len(data["sketchbook"].get("file_count", []))),
            "Digital Art": progress_bar.experience_to_level(len(data["digital"].get("file_count", []))),
            "Overall Skills": progress_bar.experience_to_level(len(data["sketchbook"].get("file_count", [])) + len(data["digital"].get("file_count", []))) }
        st.bar_chart(skill_levels)
    
    # Gallery
    st.markdown("---")
    st.header("🖼️ Recent Artwork")
    render_gallery(data["thumbnails"][-64:])
    
    # Refresh control
    st.sidebar.header("Controls")
    if st.sidebar.button("🔄 Refresh Data"):
        load_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()