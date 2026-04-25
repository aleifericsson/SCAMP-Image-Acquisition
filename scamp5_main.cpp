#include <scamp5.hpp>
#include <string>

using namespace SCAMP5_PE;
#define MSG_GPIO_CONTROL 200


int main(){
	//GPIO
    vs_gpio_as_output(VS_GPIO_X0);
    vs_gpio_as_output(VS_GPIO_X1);
    vs_gpio_as_output(VS_GPIO_X2);
    vs_gpio_as_output(VS_GPIO_X3);

    // Initialization
    vs_init();
    vs_on_shutdown([&](){
        vs_post_text("M0 shutdown\n");
    });

    // --- GUI Switches for each GPIO ---
    volatile int r_enable = 0; //0
    volatile int g_enable = 0; //1
    volatile int b_enable = 0; //2
    volatile int rgb_fps = 10; //3
    volatile int delay_us = 1000; //4
    volatile int switching = 0; //5
    volatile int frame_gain = 1; //6
    volatile int w_enable = 0; //7
    volatile int w_cycle = 0; //8

    int color = 0; //0 = red, 1 = green, 2 = blue
    std::string color_str = "RED";
    std::array<uint8_t, 4> text_color;


    auto red_switch = vs_gui_add_switch("Red: ", r_enable, &r_enable);
    auto green_switch = vs_gui_add_switch("Green: ", g_enable, &g_enable);
    auto blue_switch = vs_gui_add_switch("Blue: ", b_enable, &b_enable);
    auto rgb_fps_slider = vs_gui_add_slider("RGB FPS: ", 0, 30, rgb_fps, &rgb_fps);
    auto delay_slider = vs_gui_add_slider("Delay (us): ", 0, 10000, delay_us, &delay_us);
    auto switching_switch = vs_gui_add_switch("Start Switching?", switching, &switching);
    auto frame_gain_slider = vs_gui_add_slider("Frame Gain ", 1, 5, frame_gain, &frame_gain);
    auto white_switch = vs_gui_add_switch("White: ", w_enable, &w_enable);
    auto w_cycle_switch = vs_gui_add_switch("White Cycle?: ", w_cycle, &w_cycle);

    vs_gui_set_info(VS_M0_PROJECT_INFO_STRING);

    //auto display_1 = vs_gui_add_display("display_1",0,0);
    auto display_2 = vs_gui_add_display("display_2",0,1,2);

    vs_on_gui_update(rgb_fps_slider,[&](int32_t new_value){
    	vs_gui_move_slider(VS_GUI_FRAME_RATE,rgb_fps*3);
    	//vs_gui_move_slider(VS_GUI_FRAME_GAIN,2);
    });

    vs_on_gui_update(switching_switch,[&](int32_t new_value){
        //
    });

    vs_on_gui_update(frame_gain_slider,[&](int32_t new_value){
        vs_gui_move_slider(VS_GUI_FRAME_GAIN,frame_gain);
        //vs_gui_move_slider(VS_GUI_FRAME_GAIN,2);
    });


    uint32_t frame_counter = 0;


    while(1){
    	vs_frame_loop_control();
    	//Step 0 = determine current color:
    	if (color == 0){
    		color_str = "RED";
    		text_color = {255, 0, 0, 255};
    		if (switching){
    			r_enable = 1;
    			g_enable = 0;
    			b_enable = 0;
				w_enable = 0;
    		}
    	}
    	else if (color == 1){
    		color_str = "GREEN";
    		text_color = {0, 230, 0, 255};
    		if (switching){
				r_enable = 0;
				g_enable = 1;
				b_enable = 0;
				w_enable = 0;
			}
    	}
    	else if (color == 2){
    	    color_str = "BLUE";
    	    text_color = {20, 60, 240, 255};
    	    if (switching){
				r_enable = 0;
				g_enable = 0;
				b_enable = 1;
				w_enable = 0;
			}
    	}
    	else if (color == 3){
			color_str = "WHITE";
			text_color = {158, 158, 142, 255};
			if (switching){
				r_enable = 0;
				g_enable = 0;
				b_enable = 0;
				w_enable = 1;
			}
		}

    	//vs_gui_display_text(display_2, 50, 50, color_str.c_str(), text_color);

    	// Step 1 = trigger gpio pins
    	vs_gpio_output(VS_GPIO_X0, r_enable ? 1 : 0);
    	vs_gpio_output(VS_GPIO_X1, g_enable ? 1 : 0);
    	vs_gpio_output(VS_GPIO_X2, b_enable ? 1 : 0);
    	vs_gpio_output(VS_GPIO_X3, w_enable ? 1 : 0);


    	// Step 2 = get image
        scamp5_get_image(C,A); // capture a full-scale image in C, half-scale in A


        // Step 3 = send image
        if(vs_gui_is_on()){
            //scamp5_output_image(A,display_1);
            scamp5_output_image(C,display_2);
            vs_post_text("(%lu) %s\n", VS_LC, color_str.c_str());
            vs_post_text("(%lu) %s\n",VS_LC,scamp5_verbose_str());
        }

        //Increment frame and color
        frame_counter++;
        color += 1;
        if (w_cycle){
        	if (color >= 4) {
				color = 0;
			}
        }
        else{
            if (color >= 3) {
            	color = 0;
            }
        }
    }

    return 0;
}
