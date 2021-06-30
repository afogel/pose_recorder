from views.camera_view import CameraView
from models.video_capture import VideoCapture
import tkinter.filedialog

from models.csv_writer import CSVWriter


class CameraController():
  def __init__(self, root):
    self.root = root
    self.running = False
    self.writer = None
    self.recording = False

  def render(self):
    # instantiate view
    self.view = CameraView(self.root)
    self.view.pack(expand=True, fill='both')
    self.view.update()
    # instantiate models
    self.camera = VideoCapture(height=self.view.canvas_area.winfo_height(), width=self.view.canvas_area.winfo_width())
    self.delay = int(1000/self.camera.fps)
    self._attach_bindings()

  def update_frame(self):
    # Get a frame from the video source
    ret, frame = self.camera.get_frame()
    if ret:
      self.view.update_canvas(frame)
      self.view.status_fps.configure(text=f'FPS: {self.camera.fps}')
      if self.writer and self.recording:
        self.writer.add(self.camera.results)
    if self.running:
      self.root.after(self.delay, self.update_frame)

  def _attach_bindings(self):
    def start_camera():
      self.running = True
      self.update_frame()
      self.view.status_fps.configure(text=f'FPS: {self.camera.fps}')
      self.view.status.configure(text=f'Last action: Started Camera')
      self.view.start_record_btn.enable()
      self.view.stop_record_btn.enable()
      self.view.stop_btn.enable()
      self.view.start_btn.disable()

    def stop_camera():
      self.running = False
      self.update_frame()
      self.view.status_fps.configure(text=f'FPS: {self.camera.fps}')
      self.view.status.configure(text=f'Last action: Stopped Camera')
      self.view.start_record_btn.disable()
      self.view.stop_record_btn.disable()
      self.view.stop_btn.disable()
      self.view.start_btn.enable()
      if self.recording:
        stop_recording()

    def start_recording():
      self.recording = True
      self.view.recording_indicator.toggle()
      self.view.status.configure(text=f'Last action: Started Recording to CSV')

    def stop_recording():
      self.recording = False
      self.view.recording_indicator.toggle()
      self.view.status.configure(text=f'Last action: Stopped Recording to CSV')

    def select_source():
      self.filename = tkinter.filedialog.asksaveasfilename(
        initialdir=".",
        title="Select a file to write the csv",
        filetypes=[("csv files", ".csv")],
        defaultextension='.csv'
      )
      self.view.filename = self.filename
      self.view.update_directory()
      self.writer = CSVWriter(
          filename=self.view.filename,
          image_height=self.view.canvas_area.winfo_height(),
          image_width=self.view.canvas_area.winfo_width(),
          fps=self.view.fps
      )
      self.view.status.configure(text=f'Last action: Selected Directory')
      if self.filename:
        self.view.start_btn.enable()

    self.view.select_dir_btn.command = select_source
    self.view.start_btn.command = start_camera
    self.view.stop_btn.command = stop_camera
    self.view.start_record_btn.command = start_recording
    self.view.stop_record_btn.command = stop_recording



  def __del__(self):
    """TODO: add docstring"""
    # stop thread
    if self.camera.running:

      self.camera.running = False
      if self.camera.thread.is_alive():
        self.camera.thread.join()

    # release stream
    if self.camera.vid.isOpened():
      self.camera.vid.release()
