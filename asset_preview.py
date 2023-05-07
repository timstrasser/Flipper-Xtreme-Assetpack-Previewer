import tkinter as tk
import os
from PIL import ImageTk
from image_processing import (
    load_image,
    resize_image,
    apply_dithering,
    extract_dimensions_from_filename,
)
from file_utils import (
    load_image_files,
    get_folder_list,
    get_icon_structure,
    natural_sort_key
)

anims_path = "./Anims"

class AssetPreview:
    def __init__(self, root):
        self.root = root
        self.root.title("Asset Pack Preview")

        self.offset_x = 126.7
        self.offset_y = 21.5
        self.new_width = 180.7
        self.new_height = 100.5
        self.margin = 5
        self.new_width_with_margin = self.new_width - 2 * self.margin
        self.new_height_with_margin = self.new_height - 2 * self.margin
        self.offset_x_with_margin = self.offset_x + self.margin
        self.offset_y_with_margin = self.offset_y + self.margin
        self.orange = (255, 130, 0)
        self.black = (0, 0, 0)
        self.animation_running = False

        image1 = load_image("image1.png")
        self.image1_photo = ImageTk.PhotoImage(image1)
        self.image2_photo = None  # This will be updated later with the selected image.

        self.dropdown_frame = tk.Frame(self.root)
        self.dropdown_var2 = tk.StringVar(self.root)
        self.dropdown_menu2 = tk.OptionMenu(self.dropdown_frame, self.dropdown_var2, "")

        self._create_widgets()

    def update_animation(self):

        if not self.animation_running:
            return

        new_image_path = os.path.join(self.selected_folder_path, f"frame_{self.current_frame}.png")
        if os.path.isfile(new_image_path):
            image2 = load_image(new_image_path)
            image2_resized = resize_image(image2, self.new_width_with_margin, self.new_height_with_margin)
            image2_dithered = apply_dithering(image2_resized, fg_color=self.orange, bg_color=self.black)

            self.image2_photo = ImageTk.PhotoImage(image2_dithered)
            self.canvas.itemconfig(self.image2_id, image=self.image2_photo)

            self.current_frame = (self.current_frame + 1) % len(self.image_files)

        if self.frame_rate:
            delay = int(1000 / self.frame_rate)
        else:
            delay = 100  # Fallback to 10 FPS if frame rate is not found in meta.txt

        self.root.after_cancel(self.animation_id)
        self.animation_id = self.root.after(delay, self.update_animation)

    def update_second_dropdown(self, *args):
      selected_option = self.dropdown_var1.get()
      if selected_option == "Animations":
          anims_folders = get_folder_list(anims_path)  # use global variable here
          self.dropdown_var2.set(anims_folders[0])
          self.dropdown_menu2["menu"].delete(0, tk.END)        
          for folder in anims_folders:
              self.dropdown_menu2["menu"].add_command(label=folder, command=lambda folder=folder: [tk._setit(self.dropdown_var2, folder)(), self.set_folder(os.path.join(anims_path, folder))])
      elif selected_option == "Icons":
          if self.animation_running:
              self.animation_running = False
              self.root.after_cancel(self.animation_id)
          
          icons_root_path = "./Icons"
          icons_structure = get_icon_structure(icons_root_path)

          icon_folders = list(icons_structure.keys())
          self.dropdown_var2.set(icon_folders[0])
          self.dropdown_menu2["menu"].delete(0, tk.END)
          for folder in icon_folders:
              self.dropdown_menu2["menu"].add_command(label=folder, command=lambda folder=folder: [tk._setit(self.dropdown_var2, folder)(), self.update_third_dropdown(icons_structure[folder])])
      else:
          self.dropdown_var2.set('')
          self.dropdown_menu2["menu"].delete(0, tk.END)
          self.dropdown_menu3["menu"].delete(0, tk.END)

    def update_third_dropdown(self, files):
      def on_file_selected(file):
          selected_file_path = os.path.join("./Icons", self.dropdown_var2.get(), file)

          # Load the image with the correct file extension
          image_path = selected_file_path
          if os.path.isfile(image_path):
              image2 = load_image(image_path)

              # Extract dimensions from the filename and resize the image accordingly
              width, height = extract_dimensions_from_filename(file)
              if width and height:
                  # Calculate scaling factors based on new_width and new_height
                  width_scale_factor = self.new_width_with_margin / 128
                  height_scale_factor = self.new_height_with_margin / 64

                  # Apply the scaling factors to the extracted dimensions
                  scaled_width = int(width * width_scale_factor)
                  scaled_height = int(height * height_scale_factor)

                  image2_resized = resize_image(image2, scaled_width, scaled_height)
                  image2_dithered = apply_dithering(image2_resized, fg_color=self.orange, bg_color=self.black)
              else:
                  image2_dithered = apply_dithering(image2, fg_color=self.orange, bg_color=self.black)

              image2_photo = ImageTk.PhotoImage(image2_dithered)
              self.canvas.itemconfig(self.image2_id, image=image2_photo)
              self.set_folder(os.path.dirname(image_path)) # set the selected folder

      if files:
          self.dropdown_var3.set(files[0])
          on_file_selected(files[0])
      else:
          self.dropdown_var3.set('')
      self.dropdown_menu3["menu"].delete(0, tk.END)
      for file in files:
          self.dropdown_menu3["menu"].add_command(label=file, command=lambda file=file: [tk._setit(self.dropdown_var3, file)(), on_file_selected(file)])

    def get_frame_rate_from_meta(self, folder_path):
        meta_file_path = os.path.join(folder_path, "meta.txt")
        frame_rate = None
        try:
            with open(meta_file_path, "r") as meta_file:
                for line in meta_file:
                    if "Frame rate:" in line:
                        frame_rate = int(line.split(" ")[-1].strip())
                        break
        except FileNotFoundError:
            print(f"meta.txt not found in {folder_path}")
        return frame_rate

    def set_folder(self, folder_path):
        self.selected_folder_path = folder_path

        # If the selected folder is an animation, get the image files and the frame rate
        if self.dropdown_var1.get() == "Animations":
            self.image_files = sorted([f for f in os.listdir(self.selected_folder_path) if f.startswith("frame_") and f.endswith(".png")], key=natural_sort_key)
            self.current_frame = 0
            self.frame_rate = self.get_frame_rate_from_meta(self.selected_folder_path)

            if self.animation_running:
                self.root.after_cancel(self.animation_id)

            self.animation_running = True
            self.animation_id = self.root.after(0, self.update_animation)

        # If the selected folder is an icon, load and display the icon
        elif self.dropdown_var1.get() == "Icons":
            # Clear the image files and the frame rate
            self.image_files = []
            self.current_frame = 0
            self.frame_rate = None

            # Load the selected icon and resize it
            icon_path = os.path.join(self.selected_folder_path, self.dropdown_var3.get())
            icon_image = load_image(icon_path)
            width, height = icon_image.size
            if width and height:
                # Calculate scaling factors based on new_width and new_height
                width_scale_factor = self.new_width_with_margin / 128
                height_scale_factor = self.new_height_with_margin / 64

                # Apply the scaling factors to the extracted dimensions
                scaled_width = int(width * width_scale_factor)
                scaled_height = int(height * height_scale_factor)

                icon_image_resized = resize_image(icon_image, scaled_width, scaled_height)
            else:
                icon_image_resized = resize_image(icon_image, self.new_width_with_margin, self.new_height_with_margin)

            # Apply dithering and update the canvas
            icon_image_dithered = apply_dithering(icon_image_resized, fg_color=self.orange, bg_color=self.black)
            self.image2_photo = ImageTk.PhotoImage(icon_image_dithered)
            self.canvas.itemconfig(self.image2_id, image=self.image2_photo)



    def _create_widgets(self):
        # Create a canvas widget to display the images
        self.canvas = tk.Canvas(self.root, width=max(self.image1_photo.width(), int(self.offset_x + self.new_width)), height=max(self.image1_photo.height(), int(self.offset_y + self.new_height)))
        self.canvas.pack()

        # Create a frame to hold the dropdown menus
        self.dropdown_frame = tk.Frame(self.root)
        self.dropdown_frame.pack(pady=10)

        # Create the first dropdown menu with the "Icons" and "Animations" options
        self.dropdown_var1 = tk.StringVar(self.dropdown_frame)
        self.dropdown_var1.set("Animations")
        self.dropdown_var1.trace("w", self.update_second_dropdown)
        self.dropdown_menu1 = tk.OptionMenu(self.dropdown_frame, self.dropdown_var1, "Icons", "Animations")
        self.dropdown_menu1.pack(side=tk.LEFT, padx=10)

        # Create the second dropdown menu, initially empty
        self.dropdown_var2 = tk.StringVar(self.root)
        self.dropdown_menu2 = tk.OptionMenu(self.dropdown_frame, self.dropdown_var2, "")
        self.dropdown_menu2.pack(side=tk.LEFT)

        # Create the third dropdown menu, initially empty
        self.dropdown_var3 = tk.StringVar(self.dropdown_frame)
        self.dropdown_menu3 = tk.OptionMenu(self.dropdown_frame, self.dropdown_var3, "")
        self.dropdown_menu3.pack(side=tk.LEFT, padx=10)

        # Display the first image
        self.canvas.create_image(0, 0, image=self.image1_photo, anchor=tk.NW)

        # Display the second image on top of the first image with the specified offset, margin, and dithering
        self.image2_id = self.canvas.create_image(self.offset_x_with_margin, self.offset_y_with_margin, image=self.image2_photo, anchor=tk.NW)
        self.update_second_dropdown()