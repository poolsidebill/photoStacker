# photoStacker
This program uses the **align_image_stack** and **enfuse** utilities from the [Hugin project](https://hugin.sourceforge.io/) to create a single image from multiple images that were taken with different focus points. Images tested: JPG, TIF, and CR3 (Canon RAW)

 Macro photograpy projects can take hundreds of images, this program will process them in chunks of 10 images at a time to keep memory usage reasonable. Original images are not modified and final image has an unique name.

 Developed and tested with:
 | Name|Version|
 |----|--------|
| Python   | 3.8.10|
|opencv-python   | 4.7.0.72  |
|LibRaw   |0.19.5   |
|rawpy   |  0.18.0 |
| Hugin   | Hugin-2022.0.0 |
|ExifTool   | 11.88  |
|Pillow   |7.0.0   |
| Linux Mint | 20.3  |

While Hugin is cross-platform toolchain, my repository is based on the Linux version and underlining Linux file operations. Libraw, rawpy, and Pillow are used to convert RAW files into JPG or TIFF format. ExifTool is used to copy EXIF camera/image information from first original image to the final stacked image. OpenCV is used to display a 25% scaled version of the final stacked image for a quick image review.
 **Note:** Unable to use Pillow to display image because it does not support 16bit color TIFF files at this time.

## Operation
**photoStacker.py** performs the following actions:
- Examines file types in current directory and prompts user to select the type to process.
- Prompts for subject name. Used to create a unique output file name
-- file name = subjectName+"Stacked"+numImagesProcessed_YYYYMMDD_HHMMSS.tif
- Reads all image filenames from current directory, sorts them in assending order, and adds them to a dictionary to process. Currently, default is for 10 files to be processed at a time
- RAW to JPG image conversion performed if needed. Converted images are deleted after use. No orginal images are modified or deleted
- EXIF details from first image copied into final stacked image
- Final image preview (scaled to 25%) is displayed. Hit enter to dismiss. **Note:** Image preview can display artifacts that are not in final image because it is scaled to fit on display screen
