# photoStacker
This program uses the **align_image_stack** and **enfuse** utilities from the [Hugin project](https://hugin.sourceforge.io/) to create a single image from multiple images that were taken with different focus points.

 Macro photograpy projects can take hundreds of images, this program will process them in chunks of 10 images at a time to keep memory usage reasonable. Original images are not modified and final image has an unique name.

 Developed and tested with:
 | Name|Version|
 |----|--------|
| Python   | 3.8.10|
| Hugin   | Hugin-2022.0.0 |
| Linux Mint | 20.3  |

While Hugin is cross-platform toolchain, my repository is based on the Linux version and underlining Linux file operations.
