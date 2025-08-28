import os
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
from PIL import Image, ImageTk
import threading
import queue
import pygame
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn, TaskProgressColumn

# Initialize rich console for logging
console = Console(record=True)
log_queue = queue.Queue()

# Initialize pygame mixer for sound effects
pygame.mixer.init()

# HandBrake CLI executable path
HANDBRAKE_CLI = r"C:\Program Files\HandBrake\HandBrakeCLI.exe"

# Video extensions to process
VIDEO_EXTENSIONS = [".mkv", ".avi", ".mov", ".m4v", ".wmv"]

# Sound effect paths (relative to script directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
START_SOUND = os.path.join(SCRIPT_DIR, "sounds", "luigi-here-we-go.mp3")
FINISH_SOUND = os.path.join(SCRIPT_DIR, "sounds", "jobs_done.mp3")
ERROR_SOUND = os.path.join(SCRIPT_DIR, "sounds", "bmw-bong.mp3")

# Version number
VERSION = "v0.5"

# Global flags and subprocess list
stop_transcoding = False
is_animating = False
subprocesses = []

def process_video(filepath: Path, progress, task_id, app):
    """Run HandBrakeCLI on a single video file and replace it with the processed version."""
    global stop_transcoding, is_animating, subprocesses
    if stop_transcoding:
        log_queue.put("⛔ Transcoding stopped by user")
        return False
    
    # Verify HandBrakeCLI exists
    if not os.path.exists(HANDBRAKE_CLI):
        log_queue.put(f"❌ HandBrakeCLI.exe not found at {HANDBRAKE_CLI}")
        try:
            pygame.mixer.Sound(ERROR_SOUND).play()
        except Exception as e:
            log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
        progress.update(task_id, advance=1)
        return True
    
    # Verify file exists and is accessible
    if not filepath.exists() or not filepath.is_file():
        log_queue.put(f"❌ File does not exist or is not accessible: {filepath}")
        try:
            pygame.mixer.Sound(ERROR_SOUND).play()
        except Exception as e:
            log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
        progress.update(task_id, advance=1)
        return True
    
    # Validate input file with HandBrakeCLI scan
    try:
        scan_proc = subprocess.Popen([
            HANDBRAKE_CLI,
            "-i", str(filepath),
            "--scan"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocesses.append(scan_proc)
        stdout, stderr = scan_proc.communicate(timeout=300)
        if scan_proc.returncode != 0:
            log_queue.put(f"❌ Invalid video file {filepath}: HandBrake scan failed")
            log_queue.put(f"STDERR: {stderr}")
            try:
                pygame.mixer.Sound(ERROR_SOUND).play()
            except Exception as e:
                log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
            subprocesses.remove(scan_proc)
            progress.update(task_id, advance=1)
            return True
        subprocesses.remove(scan_proc)
    except Exception as e:
        log_queue.put(f"❌ Error scanning {filepath}: {str(e)}")
        try:
            pygame.mixer.Sound(ERROR_SOUND).play()
        except Exception as e:
            log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
        if scan_proc in subprocesses:
            subprocesses.remove(scan_proc)
        progress.update(task_id, advance=1)
        return True
    
    temp_output = filepath.with_suffix(".mp4")
    log_queue.put(f"▶ Processing: {filepath}")
    
    # Start progress bar animation for this file
    is_animating = True
    app.progress_bar['value'] = 0
    def update_progress():
        if is_animating:
            app.progress_bar['value'] = (app.progress_bar['value'] + 5) % 100
            app.root.after(100, update_progress)
    
    app.root.after(100, update_progress)
    
    try:
        encode_proc = subprocess.Popen([
            HANDBRAKE_CLI,
            "-i", str(filepath),
            "-o", str(temp_output),
            "--format", "av_mp4",
            "--encoder", "x265_10bit",
            "--encoder-profile", "main10",
            "--encoder-level", "5.1",
            "--quality", "24",
            "--cfr",
            "--keep-display-aspect",
            "--crop", "0:0:0:0",
            "--decomb",
            "--aencoder", "eac3",
            "--ab", "448",
            "--mixdown", "stereo",
            "--arate", "48",
            "--audio-lang-list", "eng",
            "--subtitle-burned",
            "--no-markers"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocesses.append(encode_proc)
        stdout, stderr = encode_proc.communicate(timeout=3600)
        if encode_proc.returncode != 0 or not temp_output.exists() or temp_output.stat().st_size == 0:
            log_queue.put(f"❌ Error processing {filepath}: HandBrake failed or output invalid")
            log_queue.put(f"STDERR: {stderr}")
            log_queue.put(f"STDOUT: {stdout}")
            if temp_output.exists():
                temp_output.unlink()
            try:
                pygame.mixer.Sound(ERROR_SOUND).play()
            except Exception as e:
                log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
            is_animating = False
            app.progress_bar['value'] = 0
            subprocesses.remove(encode_proc)
            progress.update(task_id, advance=1)
            return True
        subprocesses.remove(encode_proc)
    except subprocess.TimeoutExpired:
        log_queue.put(f"❌ Timeout processing {filepath}: HandBrake took too long")
        if temp_output.exists():
            temp_output.unlink()
        try:
            pygame.mixer.Sound(ERROR_SOUND).play()
        except Exception as e:
            log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
        if encode_proc in subprocesses:
            subprocesses.remove(encode_proc)
        is_animating = False
        app.progress_bar['value'] = 0
        progress.update(task_id, advance=1)
        return True
    except Exception as e:
        log_queue.put(f"❌ Unexpected error processing {filepath}: {str(e)}")
        if temp_output.exists():
            temp_output.unlink()
        try:
            pygame.mixer.Sound(ERROR_SOUND).play()
        except Exception as e:
            log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
        if encode_proc in subprocesses:
            subprocesses.remove(encode_proc)
        is_animating = False
        app.progress_bar['value'] = 0
        progress.update(task_id, advance=1)
        return True
    
    if stop_transcoding:
        log_queue.put("⛔ Transcoding stopped by user")
        if temp_output.exists():
            temp_output.unlink()
        is_animating = False
        app.progress_bar['value'] = 0
        if encode_proc in subprocesses:
            subprocesses.remove(encode_proc)
        return False
    
    log_queue.put(f"✅ Finished: {temp_output}")
    if temp_output.exists() and temp_output.stat().st_size > 0:
        try:
            filepath.unlink()
        except Exception as e:
            log_queue.put(f"❌ Failed to delete original file {filepath}: {str(e)}")
            try:
                pygame.mixer.Sound(ERROR_SOUND).play()
            except Exception as e:
                log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
    else:
        log_queue.put(f"❌ Output file missing or empty: {temp_output}")
        try:
            pygame.mixer.Sound(ERROR_SOUND).play()
        except Exception as e:
            log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
    
    # Stop animation for this file
    is_animating = False
    app.progress_bar['value'] = 0
    progress.update(task_id, advance=1)
    return True

def collect_files(root_dir: Path):
    """Collect all video files recursively."""
    files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if file_path.suffix.lower() in VIDEO_EXTENSIONS:
                files.append(file_path)
    return files

def run_transcode(directory, log_text, app):
    """Run the transcoding process for the given directory."""
    global stop_transcoding, is_animating, subprocesses
    # Check if HandBrakeCLI exists before starting
    if not os.path.exists(HANDBRAKE_CLI):
        log_queue.put(f"❌ HandBrakeCLI.exe not found at {HANDBRAKE_CLI}. Please ensure it is installed.")
        try:
            pygame.mixer.Sound(ERROR_SOUND).play()
        except Exception as e:
            log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
        return
    
    log_queue.put(f"Starting transcoding for directory: {directory}")
    files = collect_files(Path(directory))
    total_files = len(files)
    if total_files == 0:
        log_queue.put(f"No video files found in {directory}")
        try:
            pygame.mixer.Sound(ERROR_SOUND).play()
        except Exception as e:
            log_queue.put(f"❌ Error playing sound {ERROR_SOUND}: {str(e)}")
        return
    log_queue.put(f"Found {total_files} video files to process.")
    
    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task_id = progress.add_task("Encoding videos...", total=total_files)
        for file in files:
            if stop_transcoding:
                log_queue.put("⛔ Transcoding stopped by user")
                break
            if not process_video(file, progress, task_id, app):
                break
    
    if not stop_transcoding:
        log_queue.put("🎉 All files processed!")
        try:
            pygame.mixer.Sound(FINISH_SOUND).play()
        except Exception as e:
            log_queue.put(f"❌ Error playing sound {FINISH_SOUND}: {str(e)}")
    # Ensure progress bar is stopped
    is_animating = False
    app.progress_bar['value'] = 0
    # Terminate any remaining subprocesses
    for proc in subprocesses:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            pass
    subprocesses.clear()

class TranscodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("S.M.A.C - Super Mega Auto Converter")
        self.root.configure(bg="#f0f0f0")  # Light grey background
        self.root.resizable(True, True)  # Make window resizable
        self.root.geometry("600x650")  # Set window size to 600px wide, 650px tall
        
        # Apply macOS-like style
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), background="#f0f0f0", foreground="black")
        style.configure("TEntry", font=("Helvetica", 10), fieldbackground="black", foreground="grey")
        style.configure("TButton", font=("Helvetica", 10), background="#f0f0f0", foreground="black")
        style.configure("Stop.TButton", font=("Helvetica", 10), background="#f0f0f0", foreground="red")
        style.configure("TProgressbar", thickness=10)
        
        # Title frame with image
        title_frame = tk.Frame(root, bg="#f0f0f0")
        title_frame.pack(pady=20)
        title_label = ttk.Label(title_frame, text="S.M.A.C - Super Mega Auto Converter", font=("Helvetica", 18, "bold"), foreground="black")
        title_label.pack(side=tk.LEFT)
        
        # Load and display mario.png from images directory
        try:
            mario_img = Image.open(os.path.join(SCRIPT_DIR, "images", "mario.png"))
            mario_img = mario_img.resize((50, 50), Image.LANCZOS)
            self.mario_photo = ImageTk.PhotoImage(mario_img)
            mario_label = ttk.Label(title_frame, image=self.mario_photo, background="#f0f0f0")
            mario_label.pack(side=tk.RIGHT, padx=10)
        except Exception as e:
            log_queue.put(f"❌ Error loading images/mario.png: {e}")
        
        # Directory selection
        dir_frame = tk.Frame(root, bg="#f0f0f0")
        dir_frame.pack(pady=5)
        self.dir_label = ttk.Label(dir_frame, text="Select Folder:", foreground="black")
        self.dir_label.pack(side=tk.LEFT, padx=5)
        self.dir_entry = ttk.Entry(dir_frame, width=50)
        self.dir_entry.pack(side=tk.LEFT, padx=5)
        self.dir_entry.insert(0, r"\\192.168.1.4\Plex Server\MEDIA")
        self.browse_button = ttk.Button(root, text="Browse", command=self.browse_folder)
        self.browse_button.pack(pady=5)
        
        # Button frame for Start and Stop
        button_frame = tk.Frame(root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        self.start_button = ttk.Button(button_frame, text="Start Transcoding", command=self.start_transcode)
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.stop_button = ttk.Button(button_frame, text="Stop Transcoding", command=self.stop_transcode, style="Stop.TButton", state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # Animation frame for progress bar
        animation_frame = tk.Frame(root, bg="#f0f0f0")
        animation_frame.pack(pady=5)
        self.progress_bar = ttk.Progressbar(animation_frame, mode='determinate', maximum=100, length=200)
        self.progress_bar.pack(anchor='center')
        
        # Log area
        self.log_text = scrolledtext.ScrolledText(root, height=20, width=80, state='normal', font=("Helvetica", 10), fg="green", bg="black")
        self.log_text.pack(pady=20)
        self.log_text.insert(tk.END, "Mama Mia! Let's convert some media files!\n")
        
        # Footer with version
        footer_frame = tk.Frame(root, bg="#f0f0f0")
        footer_frame.pack(pady=5)
        version_label = ttk.Label(footer_frame, text=VERSION, font=("Helvetica", 8), foreground="black", background="#f0f0f0")
        version_label.pack()
        footer_label = ttk.Label(footer_frame, text="Designed by GooseWurkz", font=("Helvetica", 8), foreground="black", background="#f0f0f0")
        footer_label.pack()
        
        # Log update thread
        self.running = True
        self.log_thread = threading.Thread(target=self.update_logs)
        self.log_thread.daemon = True
        self.log_thread.start()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def browse_folder(self):
        """Open a native Windows folder picker dialog."""
        folder = filedialog.askdirectory(initialdir=r"\\192.168.1.4\Plex Server\MEDIA")
        if folder:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder)

    def start_transcode(self):
        """Start the transcoding process in a separate thread."""
        global stop_transcoding, is_animating, subprocesses
        stop_transcoding = False
        directory = self.dir_entry.get().strip()
        if not directory or not os.path.exists(directory):
            self.log_text.insert(tk.END, "Error: Invalid or inaccessible directory\n")
            self.log_text.see(tk.END)
            self.progress_bar['value'] = 0
            try:
                pygame.mixer.Sound(ERROR_SOUND).play()
            except Exception as e:
                self.log_text.insert(tk.END, f"❌ Error playing sound {ERROR_SOUND}: {str(e)}\n")
            return
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        while not log_queue.empty():
            log_queue.get()
        try:
            pygame.mixer.Sound(START_SOUND).play()
        except Exception as e:
            self.log_text.insert(tk.END, f"❌ Error playing sound {START_SOUND}: {str(e)}\n")
        # Start transcoding thread
        thread = threading.Thread(target=run_transcode, args=(directory, self.log_text, self))
        thread.start()
        def check_thread():
            if thread.is_alive():
                self.root.after(1000, check_thread)
            else:
                self.start_button.config(state='normal')
                self.stop_button.config(state='disabled')
                is_animating = False
                self.progress_bar['value'] = 0
                for proc in subprocesses:
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                    except:
                        pass
                subprocesses.clear()
        self.root.after(1000, check_thread)

    def stop_transcode(self):
        """Stop the transcoding process and animation."""
        global stop_transcoding, is_animating, subprocesses
        stop_transcoding = True
        is_animating = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar['value'] = 0
        for proc in subprocesses:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                pass
        subprocesses.clear()

    def update_logs(self):
        """Update the log area with messages from the queue."""
        while self.running:
            try:
                log = log_queue.get(timeout=1)
                self.log_text.insert(tk.END, f"{log}\n")
                self.log_text.see(tk.END)
            except queue.Empty:
                continue

    def on_closing(self):
        """Handle window close event."""
        global stop_transcoding, is_animating, subprocesses, self.running
        stop_transcoding = True
        is_animating = False
        self.running = False
        self.progress_bar['value'] = 0
        for proc in subprocesses:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                pass
        subprocesses.clear()
        pygame.mixer.quit()
        self.root.destroy()

    def __del__(self):
        self.running = False
        pygame.mixer.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscodeApp(root)
    root.mainloop()