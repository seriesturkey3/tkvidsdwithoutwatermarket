import streamlit as st
import yt_dlp
import os
from datetime import datetime
import time
import re
from urllib.parse import urlparse
import concurrent.futures
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="TikTok Video Downloader",
    page_icon="🎵",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #071c1a;
    }
    .main {
        padding: 2rem;
    }
    .stButton>button {
        background-color: #fe2c55;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #e6254d;
    }
    .download-status {
        padding: 1rem;
        border-radius: 10px;
        background-color: #071c1a;
        margin: 1rem 0;
        border: 1px solid #071c1a;
    }
    .video-preview {
        border-radius: 10px;
        overflow: hidden;
        margin: 1rem 0;
    }
    .history-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
    }
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .error-text {
        color: #dc3545;
        font-weight: bold;
    }
    .info-card {
        background-color: #071c1a;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

class TikTokDownloader:
    def __init__(self):
        self.download_history = []
        self.ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

    def validate_url(self, url):
        """Validate TikTok URL format"""
        try:
            parsed = urlparse(url)
            return bool(
                parsed.netloc in ['www.tiktok.com', 'tiktok.com', 'vm.tiktok.com'] and
                ('/video/' in parsed.path or '@' in parsed.path)
            )
        except:
            return False

    def get_video_info(self, url):
        """Get video information using yt-dlp"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return True, info
        except Exception as e:
            return False, str(e)

    def download_video(self, url, output_path):
        """Download TikTok video"""
        try:
            # Configure yt-dlp options for downloading
            ydl_opts = {
                'format': 'best',
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
            }

            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Add to download history
            self.download_history.append({
                'url': url,
                'path': output_path,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'Success'
            })
            
            return True, "Download completed successfully"

        except Exception as e:
            error_message = str(e)
            self.download_history.append({
                'url': url,
                'path': output_path,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'Failed',
                'error': error_message
            })
            return False, f"Download error: {error_message}"

def create_download_directory():
    """Create downloads directory if it doesn't exist"""
    download_dir = "tiktok_downloads"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    return download_dir

def main():
    st.title("🎵 TikTok Video Downloader")
    st.markdown("### Download TikTok Videos Without Watermark 🚀")

    # Initialize downloader
    if 'downloader' not in st.session_state:
        st.session_state.downloader = TikTokDownloader()

    # Create tabs for single and bulk download
    tab1, tab2, tab3 = st.tabs(["Single Download", "Bulk Download", "Download History"])

    # Single Download Tab
    with tab1:
        st.markdown("""
        <div class="info-card">
            <h4>📝 Instructions:</h4>
            <ol>
                <li>Copy the TikTok video URL from the app or website</li>
                <li>Paste the URL in the input field below</li>
                <li>Click "Download Video" and wait for the process to complete</li>
                <li>Your video will be saved automatically</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        video_url = st.text_input(
            "Enter TikTok Video URL",
            placeholder="https://www.tiktok.com/@user/video/1234567890"
        )

        if st.button("Download Video", key="single_download"):
            if not video_url:
                st.error("Please enter a TikTok video URL!")
            elif not st.session_state.downloader.validate_url(video_url):
                st.error("Invalid TikTok URL! Please enter a valid video URL.")
            else:
                with st.spinner("Downloading video..."):
                    # Create download directory
                    download_dir = create_download_directory()
                    output_path = os.path.join(download_dir, f"tiktok_video_{int(time.time())}.mp4")
                    
                    # Get video info first
                    success, info = st.session_state.downloader.get_video_info(video_url)
                    
                    if success:
                        # Download video
                        success, message = st.session_state.downloader.download_video(video_url, output_path)
                        
                        if success:
                            st.success("✅ " + message)
                            if os.path.exists(output_path):
                                st.video(output_path)
                                st.markdown(f"""
                                <div class="info-card">
                                    <p><strong>Download Details:</strong></p>
                                    <p>📁 Saved to: {output_path}</p>
                                    <p>⏱️ Duration: {info.get('duration', 'Unknown')} seconds</p>
                                    <p>👤 Author: {info.get('uploader', 'Unknown')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.error("❌ " + message)
                    else:
                        st.error(f"❌ Error getting video info: {info}")

    # Bulk Download Tab
    with tab2:
        st.markdown("""
        <div class="info-card">
            <h4>📝 Bulk Download Instructions:</h4>
            <ol>
                <li>Enter one TikTok video URL per line</li>
                <li>All videos will be downloaded simultaneously</li>
                <li>Progress will be shown for each download</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        urls = st.text_area(
            "Enter TikTok Video URLs (one per line)",
            placeholder="https://www.tiktok.com/@user/video/1234567890\nhttps://www.tiktok.com/@user/video/0987654321"
        )

        if st.button("Download All Videos", key="bulk_download"):
            if not urls:
                st.error("Please enter TikTok video URLs!")
            else:
                url_list = [url.strip() for url in urls.split('\n') if url.strip()]
                valid_urls = [url for url in url_list if st.session_state.downloader.validate_url(url)]
                
                if not valid_urls:
                    st.error("No valid TikTok URLs found!")
                    return

                download_dir = create_download_directory()
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    futures = []
                    for i, url in enumerate(valid_urls):
                        output_path = os.path.join(download_dir, f"tiktok_video_{int(time.time())}_{i}.mp4")
                        futures.append(executor.submit(
                            st.session_state.downloader.download_video,
                            url,
                            output_path
                        ))

                    for i, future in enumerate(concurrent.futures.as_completed(futures)):
                        success, message = future.result()
                        progress = (i + 1) / len(futures)
                        progress_bar.progress(progress)
                        status_text.text(f"Downloaded {i + 1} of {len(futures)} videos")
                        
                        if not success:
                            st.warning(f"Failed to download video: {message}")

                st.success("✅ Bulk download completed!")

    # Download History Tab
    with tab3:
        if st.session_state.downloader.download_history:
            for item in reversed(st.session_state.downloader.download_history):
                status_color = "success-text" if item['status'] == 'Success' else "error-text"
                st.markdown(f"""
                <div class="download-status">
                    <p><strong>URL:</strong> {item['url']}</p>
                    <p><strong>Time:</strong> {item['timestamp']}</p>
                    <p><strong>Status:</strong> <span class="{status_color}">{item['status']}</span></p>
                    {f'<p><strong>Error:</strong> {item.get("error")}</p>' if item.get('error') else ''}
                    {f'<p><strong>File:</strong> {item["path"]}</p>' if item['status'] == 'Success' else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No download history available yet.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Made with ❤️ by Your Name</p>
            <p style='font-size: 0.8em'>⚠️ Use responsibly and in accordance with TikTok's terms of service.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()