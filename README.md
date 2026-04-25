# SCAMP-Image-Acquisition

# Introduction
This repository is part of a Final Year EEE Project to add colour acquisition to a monochrome camera known as the [SCAMP Vision Sensor](https://personalpages.manchester.ac.uk/staff/p.dudek/scamp/). This repository contains both the firmware code (scamp5_main.cpp) to be uploaded to the SCAMP and the client-side "host" (scamp_stream.py) to accept serial data from the SCAMP to be compiled into a folder of image to be used in the programs in the [SCAMP Colour Extraction Repository](https://github.com/aleifericsson/SCAMP-Colour-Extraction). Code used for programming and controlling the hardware approaches for SCAMP colourisation does not exist within this repository but rather in the [SCAMP Hardware Programming Repository](https://github.com/aleifericsson/SCAMP-Hardware-Programming)

# Installation
1. Refer to the instructions listed in the [SCAMP Official Website](https://scamp.gitlab.io/scamp5d_doc/_p_a_g_e__s_e_t_u_p.html) after downloading all of the required files from the [download page](https://scamp.gitlab.io/scamp5d_doc/_p_a_g_e__d_o_w_n_l_o_a_d.html).

2. Once MCUxpresso has been set up, copy one of the example projects and replace its scamp5_main.cpp with the scamp5_main.cpp from this repository. The file directory of the SCAMP folder should look like as shown below. Follow the instructions on the official website for uploading the code onto the SCAMP.
<img width="602" height="802" alt="image" src="https://github.com/user-attachments/assets/916c4a35-bb09-48b3-a559-95db3696a3fe" />

3. Place scamp_stream.py in the scamp_python_module folder. Ensure that Python 3.14 is installed and use [pip](https://pypi.org/project/pip/) to install the libraries listed on the top the program. The file directory of the scamp_python_module folder should look like as shown below:
<img width="1466" height="738" alt="image" src="https://github.com/user-attachments/assets/16c8e52a-0ec4-40d4-9298-fa8fba8c406e" />

4. Run scamp_stream.py once everything is set up and the SCAMP is connected and set the is_recording flag to true to start saving the resulting RGB images into the captured_frames folder under the date and time at which recording was started.

# Previews
### scamp_stream.py
<img width="1294" height="738" alt="image" src="https://github.com/user-attachments/assets/e73d6267-147f-4936-8d2f-5614630405f9" />



