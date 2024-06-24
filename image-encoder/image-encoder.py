import sys
import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = str(pow(2,40))
import json
import numpy as np
from numba import jit, uint8
import cv2
import math
from PIL import ImageFont,Image, ImageDraw, ImageFilter

# ---------------------------------
# get script argument - 1: jsonfile_name
json_filename = sys.argv[1]

import time

# time.sleep(5)

print("OS----",os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"])


# ---------------------------------
# load josn file
# with open(f'/home/ubuntu/ysm_project/encoder_v2/json/{json_filename}', 'r') as file:
#     loaded_data = json.load(file)
    
    
with open(f'./json/{json_filename}', 'r') as file:
    loaded_data = json.load(file)
    
    

# ---------------------------------
# config encoder
TEMPLATE_CONFIG_KEY = "config"
config = loaded_data["config"]
USER_UID = config["user_uid"]
RECORD_ID = config["record_id"]
TEMPLATE_UID = config["template_uid"]
VIDEO_WIDTH = config["width"]
VIDEO_HEIGHT = config["height"]
VIDEO_DURATION = config["duration"]
VIDEO_FRAMERATE = config["frame_rate"]

current_directory = os.getcwd()
output_directory = f'{current_directory}/result'
user_res_dircetory = f'{current_directory}/assets/users/{USER_UID}/{RECORD_ID}'
admin_res_directory = f'{current_directory}/assets/admin/{TEMPLATE_UID}'
font_directory = f'{current_directory}/fonts'  


# current_directory = os.getcwd()
# output_directory = f'{current_directory}/encoder_v2/result'
# user_res_dircetory = f'{current_directory}/encoder_v2/assets/users/{USER_UID}/{RECORD_ID}'
# admin_res_directory = f'{current_directory}/encoder_v2/assets/admin/{TEMPLATE_UID}'
# font_directory = f'{current_directory}/encoder_v2/fonts'  
# for dir in [current_directory, output_directory,user_res_dircetory,admin_res_directory,font_directory]:
#     print(dir) 
#     mode = os.stat(dir).st_mode
#     print("Readable:", bool(mode & os.R_OK))
#     print("Writable:", bool(mode & os.W_OK))
#     print("Executable:", bool(mode & os.X_OK))
#     os.chmod(dir, 0o777) 


fourcc = cv2.VideoWriter_fourcc(*'avc1')
video_writer = cv2.VideoWriter(f"{output_directory}/output{RECORD_ID}.mp4", fourcc, VIDEO_FRAMERATE, (VIDEO_WIDTH, VIDEO_HEIGHT), True)

instance_container = { }

# ---------------------------------
# helper
@jit(nopython=True,cache= True)
def to_framenumber(time):
    return round(time * VIDEO_FRAMERATE )
    
    # return math.floor(time * VIDEO_FRAMERATE)

# ---------------------------------
# generate encoding data form
TEMPLATE_COMPOSITOINS_KEY = "template_compositions"
TEMPLATE_OBJECTS_KEY = "template_objects"
TEMPLATE_ANIMATIONS_KEY = "template_animations"

template_compositions = loaded_data[TEMPLATE_COMPOSITOINS_KEY]
template_objects = loaded_data[TEMPLATE_OBJECTS_KEY]
template_animations = loaded_data[TEMPLATE_ANIMATIONS_KEY]



time_conversion_value = 1.0
bgm_file_path = f"{admin_res_directory}/bgm.mp3"
# bgm_file_path = f"{output_directory}/72a6a5b0-c0c2-46d8-a385-9d2064449e4e.mp3"
# config["audio_file_duration"] = 205.897143
# time_conversion_value = config["audio_file_duration"] / VIDEO_DURATION

if "audio_file_path" in config and config["audio_file_path"] is not None:
    time_conversion_value = config["audio_file_duration"] / VIDEO_DURATION
    bgm_file_path = config["audio_file_path"]
    
    


# ---------------------------------
# Calibrate Data
VIDEO_DURATION *= time_conversion_value

for template_composition in template_compositions:
    template_composition["init_time"] *= time_conversion_value
    template_composition["deinit_time"] *= time_conversion_value
    if "transition_duration" in template_composition and template_composition["transition_duration"] is not None:
        template_composition["transition_duration"] *= time_conversion_value
    

for template_object in template_objects:
    template_object["init_time"] *= time_conversion_value
    template_object["deinit_time"] *= time_conversion_value
    
    

for template_animation in template_animations:
    template_animation["start_time"] *= time_conversion_value
    template_animation["duration"] *= time_conversion_value
    
    


for template_composition in template_compositions:
    template_composition["init_frame_number"] = to_framenumber(template_composition["init_time"])
    template_composition["deinit_frame_number"] = to_framenumber(template_composition["deinit_time"])
    if "transition_duration" in template_composition and template_composition["transition_duration"] is not None:
        template_composition["transition_duration_frame_count"] = to_framenumber(template_composition["transition_duration"])
    matching_objects = [template_object for template_object in template_objects if template_object["composition_uid"] == template_composition["template_composition_uid"]]
    matching_objects.sort(key=lambda x: x['z_index'], reverse=False)
    
    for matching_object in matching_objects:
        matching_animations = [template_animation for template_animation in template_animations if template_animation["template_object_uid"] == matching_object["template_object_uid"]]
        matching_object["animations"] = matching_animations
        for matching_animation in matching_object["animations"]:
            matching_animation["start_frame_number"] = to_framenumber(matching_animation["start_time"])
            matching_animation["duration_frame_count"] = to_framenumber(matching_animation["duration"])
        matching_object["translation_x_animations"] = [matching_animation for matching_animation in matching_animations if matching_animation["type"] == "translation_x"]
        matching_object["translation_y_animations"] = [matching_animation for matching_animation in matching_animations if matching_animation["type"] == "translation_y"]
        matching_object["opacity_animations"] = [matching_animation for matching_animation in matching_animations if matching_animation["type"] == "opacity"]
        matching_object["scale_animations"] = [matching_animation for matching_animation in matching_animations if matching_animation["type"] == "scale"]
        matching_object["rotation_animations"] = [matching_animation for matching_animation in matching_animations if matching_animation["type"] == "rotation"]
        matching_object["effects"] = [matching_animation for matching_animation in matching_animations if matching_animation["type"] == "effect"]
        matching_object["init_frame_number"] = to_framenumber(matching_object["init_time"])
        matching_object["deinit_frame_number"] = to_framenumber(matching_object["deinit_time"])
        if matching_object["type"] == "video":
            if "video_start_time" in matching_object and matching_object["video_start_time"] is not None:
                matching_object["video_start_frame_number"] = to_framenumber(matching_object["video_start_time"])
            else:
                matching_object["video_start_time"] = 0
                matching_object["video_start_frame_number"] = 0
        
        
    template_composition["objects"] = matching_objects
    
template_compositions.sort(key=lambda x:x['z_index'],reverse=False)


# ---------------------------------
# 
@jit(nopython=True,cache= True)
def generate_composition_frame(r: uint8, g: uint8, b:uint8): # type: ignore
    frame = np.empty((VIDEO_HEIGHT, VIDEO_WIDTH, 3), dtype=np.uint8)
    for y in range(VIDEO_HEIGHT):
        for x in range(VIDEO_WIDTH):
            frame[y, x, :] = (b, g, r)
            
    return frame
#
# ---------------------------------

def resize_image_with_pil(image, new_size):
    """
    OpenCV 이미지를 PIL을 사용하여 리사이즈한 후 다시 OpenCV 이미지로 변환
    
    Args:
    - image: OpenCV 이미지 (numpy 배열)
    - new_size: 리사이즈할 새로운 크기 (width, height)
    
    Returns:
    - resized_image: 리사이즈된 OpenCV 이미지
    """
    # OpenCV 이미지를 PIL 이미지로 변환
    if image.shape[2] == 3:
        input_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        input_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
    pil_image = Image.fromarray(input_image)
    
    # 현재 크기
    original_size = pil_image.size
    
    # 리사이즈할 새로운 크기가 본래 크기보다 크면 확대, 작으면 축소
    if new_size[0] > original_size[0] or new_size[1] > original_size[1]:
        resample_filter = Image.BICUBIC
    else:
        resample_filter = Image.LANCZOS
    
    # PIL을 사용하여 이미지 리사이즈
    resized_pil_image = pil_image.resize(new_size, resample=resample_filter)
    
    # PIL 이미지를 다시 OpenCV 이미지로 변환
    resized_image_rgba = np.array(resized_pil_image)
    if image.shape[2] == 3:
        resized_image = cv2.cvtColor(resized_image_rgba, cv2.COLOR_RGBA2BGR)
    else:
        resized_image = cv2.cvtColor(resized_image_rgba, cv2.COLOR_RGBA2BGRA)
    
    return resized_image


@jit(nopython=True,cache=True)
def curve_value(t, startValue, endValue, duration, effect,multiplier=1.0,curve="ease_in_out"):
    progress = t / duration  # Normalize the progress to a value between 0 and 1
    
    pivot_value = 0.3
    
    if curve == "linear":
        return startValue + (endValue - startValue) * progress
    elif curve == "ease_in":
        easeInValue = np.power(progress, 1 + multiplier)
        return startValue + (endValue - startValue) * easeInValue
    elif curve == "ease_out":
        easeOutValue = - np.power(1-progress, 1 + multiplier) + 1
        return startValue + (endValue - startValue) * easeOutValue
    elif curve == "ease_in_out":
        if progress < pivot_value:
            easeInOutValue = np.power(pivot_value, -multiplier) * np.power(progress, 1 + multiplier)
            return startValue + (endValue - startValue) * easeInOutValue
        else:
            easeInOutValue = - np.power(1-pivot_value, -multiplier) * np.power(1-progress, 1 + multiplier) + 1
            return startValue + (endValue - startValue) * easeInOutValue
    elif curve == "ease_out_in":
        if progress < pivot_value:
            easeOutInValue = - np.power(pivot_value, -multiplier) * np.power(pivot_value-progress, 1 + multiplier) + pivot_value
            return startValue + (endValue - startValue) * easeOutInValue
        else:
            easeOutInValue = np.power(1-pivot_value, -multiplier) * np.power(progress - pivot_value, 1 + multiplier) + pivot_value
            return startValue + (endValue - startValue) * easeOutInValue
    else:
        if progress < pivot_value:
            easeInOutValue = np.power(pivot_value, -multiplier) * np.power(progress, 1 + multiplier)
            return startValue + (endValue - startValue) * easeInOutValue
        else:
            easeInOutValue = - np.power(1-pivot_value, -multiplier) * np.power(1-progress, 1 + multiplier) + 1
            return startValue + (endValue - startValue) * easeInOutValue


@jit(nopython=True,cache=True)
def animation_value(calibrated_number,d_value,start_number,duration_count,multiplier,curve):
    if start_number <= calibrated_number and start_number + duration_count >= calibrated_number:
        return curve_value(calibrated_number-start_number,0,d_value,duration_count,"",multiplier,curve)
    elif start_number + duration_count < calibrated_number:
        return d_value
    else:
        return 0

def toStyle(frame_number,object):
    calibrated_frame_number = frame_number - object["init_frame_number"]
    
    opacity = object["opacity"]
    for animation in object["opacity_animations"]:
        opacity += animation_value(calibrated_frame_number,animation["d_value"],animation["start_frame_number"],animation["duration_frame_count"],animation["multiplier"],animation["curve"])
            
    rect = [object["x"], object["y"], object["width"], object["height"]]
    rect[0] -= object["width"] * object["anchor_x"]
    rect[1] -= object["height"] * object["anchor_y"]
    for animation in object["translation_x_animations"]:
        rect[0] += animation_value(calibrated_frame_number,animation["d_value"],animation["start_frame_number"],animation["duration_frame_count"],animation["multiplier"],animation["curve"])
    
    for animation in object["translation_y_animations"]:
        rect[1] += animation_value(calibrated_frame_number,animation["d_value"],animation["start_frame_number"],animation["duration_frame_count"],animation["multiplier"],animation["curve"])
            
    rotation = object["rotation"]
    for animation in object["rotation_animations"]:
        rotation += animation_value(calibrated_frame_number,animation["d_value"],animation["start_frame_number"],animation["duration_frame_count"],animation["multiplier"],animation["curve"])
    
    
    
    
    scale = object["scale"] - 1
    rect[0] -= (scale)*rect[2] / 2
    rect[1] -= (scale)*rect[3] / 2
    for animation in object["scale_animations"]:
        if (animation["start_frame_number"] <= calibrated_frame_number and animation["start_frame_number"] + animation["duration_frame_count"] >= calibrated_frame_number):
            increment = curve_value(calibrated_frame_number-animation["start_frame_number"],0,animation["d_value"],animation["duration_frame_count"],animation["curve"],animation["multiplier"],animation["curve"])
            rect[0] -= (increment)*rect[2] / 2
            rect[1] -= (increment)*rect[3] / 2
            scale += increment
            
        elif animation["start_frame_number"] + animation["duration_frame_count"] < calibrated_frame_number:
            increment = animation["d_value"]
            rect[0] -= (increment)*rect[2] / 2
            rect[1] -= (increment)*rect[3] / 2
            scale += increment
            
    scale+=1
    
    rect[2] = scale * rect[2]
    rect[3] = scale * rect[3]
    
    effects = []
    for animation in object["effects"]:
        effects.append(animation)
    
    return {
        "top": rect[1],
        "left": rect[0],
        "width": rect[2],
        "height": rect[3],
        "opacity": opacity,
        "scale": scale,
        "rotation": rotation,
        "effects": effects
    }
    

def add_border_radius(image, radius):
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA))
    mask = Image.new('L', image_pil.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + image_pil.size, radius=radius, fill=255)
    result = Image.new('RGBA', image_pil.size)
    result.paste(image_pil, (0, 0), mask)
    return cv2.cvtColor(np.array(result), cv2.COLOR_RGB2BGRA)


def apply_masking(image,mask_image):
    alpha_channel = mask_image[:, :, 3]
    combined_alpha = cv2.bitwise_and(image[:, :, 3], alpha_channel)
    result_image = np.dstack((image[:, :, :3], combined_alpha))
    return result_image

def add_border_line(input_image, border_width, border_color):
    height = input_image.shape[0]
    width = input_image.shape[1]
    bordered_image = np.zeros((height, width, 4), dtype=np.uint8)
    r = int(border_color[1:3], 16) 
    g = int(border_color[3:5], 16)  
    b = int(border_color[5:7], 16)
    a = int(border_color[7:9], 16)
    border_color = (b,g,r,a)
    bordered_image[:, :] = border_color
    bordered_image[border_width:height-border_width, border_width:width-border_width] = input_image[border_width:height-border_width, border_width:width-border_width]
    return bordered_image


@jit(nopython=True,cache=True)
def alpha_blending(foreground, background, alpha):
    for c in range(0, 3):
        background[:, :, c] = (alpha) * foreground[:, :, c] + (1 - alpha) * background[:, :, c]
    return background

# @jit(nopython=True,cache=True)
# def overlay(foreground, background, x_start,x_end, y_start,y_end):
#     for x in range(x_start,x_end):
#         for y in range(y_start,y_end):
#             background[x,y] = foreground[x-x_start,y-y_start]
#     return background



    
# frame2 is appearing frame
def wiper_cross(frame1, frame2, frame_number, frame_count, direction="top_left_to_bottom_right",multiplier=1.0,curve="linear"):
    if frame1 is None:
        height, width = frame2.shape[:2]
    else:
        height, width = frame1.shape[:2]
    y_indices, x_indices = np.indices((height, width))
    diagonal_length = width + height
    # diagonal_progress = (frame_number / frame_count) * diagonal_length
    
    
    diagonal_progress = curve_value(frame_number, 0, diagonal_length,frame_count,"",multiplier,curve)
    if frame1 is None:
        frame1 = np.zeros((height, width, 4), dtype=np.uint8)
    if frame2 is None:
        frame2 = np.zeros((height, width, 4), dtype=np.uint8)
        
    # 입력 이미지의 채널 수 확인
    if frame1.shape[2] == 4:  # 알파 채널이 있는 경우
        channel_length = 4
    else:
        channel_length = 3  # 알파 채널이 없는 경우
    if direction == "top_left_to_bottom_right":
        mask = x_indices + y_indices <= diagonal_progress
    elif direction == "top_right_to_bottom_left":
        mask = (width - x_indices) + y_indices <= diagonal_progress
    elif direction == "bottom_left_to_top_right":
        mask = x_indices + (height - y_indices) <= diagonal_progress
    elif direction == "bottom_right_to_top_left":
        mask = (width - x_indices) + (height - y_indices) <= diagonal_progress
    else:
        raise ValueError("Invalid direction")
    
    transition_frame = np.zeros((height, width, channel_length), dtype=np.uint8)
    for c in range(channel_length):
        transition_frame[:, :, c] = np.where(mask, frame2[:,:,c], frame1[:, :, c])
    return transition_frame

def wiper_vertical(frame1, frame2, frame_number, frame_count,direction="bottom_to_top",multiplier=1.0,curve="linear"):
    if frame1 is None:
        height, width = frame2.shape[:2]
    else:
        height, width = frame1.shape[:2]
    y_indices, x_indices = np.indices((height, width))
    diagonal_length = height
    # diagonal_progress = (frame_number / frame_count) * diagonal_length
    
    
    diagonal_progress = curve_value(frame_number, 0, diagonal_length,frame_count,"",multiplier,curve)
    if frame1 is None:
        frame1 = np.zeros((height, width, 4), dtype=np.uint8)
    if frame2 is None:
        frame2 = np.zeros((height, width, 4), dtype=np.uint8)
        
    # 입력 이미지의 채널 수 확인
    if frame1.shape[2] == 4:  # 알파 채널이 있는 경우
        channel_length = 4
    else:
        channel_length = 3  # 알파 채널이 없는 경우
        
        
    if direction == "top_to_bottom":
        mask = y_indices <= diagonal_progress
    elif direction == "bottom_to_top":
        mask = y_indices >= height - diagonal_progress
    else:
        raise ValueError("Invalid direction")
    transition_frame = np.zeros((height, width, channel_length), dtype=np.uint8)
    for c in range(channel_length):
        # transition_frame[:, :, c] = np.where(y_indices <= diagonal_progress, frame2[:, :, c], frame1[:, :, c])
        transition_frame[:, :, c] = np.where(mask, frame2[:, :, c], frame1[:, :, c])
    return transition_frame

def wiper_horizontal(frame1, frame2, frame_number, frame_count,direction="left_to_right",multiplier=1.0,curve="linear"):
    if frame1 is None:
        height, width = frame2.shape[:2]
    else:
        height, width = frame1.shape[:2]
    y_indices, x_indices = np.indices((height, width))
    diagonal_length = width
    diagonal_progress = curve_value(frame_number, 0, diagonal_length,frame_count,"",multiplier,curve)
    if frame1 is None:
        frame1 = np.zeros((height, width, 4), dtype=np.uint8)
    if frame2 is None:
        frame2 = np.zeros((height, width, 4), dtype=np.uint8)
        
    # 입력 이미지의 채널 수 확인
    if frame1.shape[2] == 4:  # 알파 채널이 있는 경우
        channel_length = 4
    else:
        channel_length = 3  # 알파 채널이 없는 경우
    transition_frame = np.zeros((height,width,channel_length),dtype=np.uint8)
    
    
    if direction == "left_to_right":
        mask = x_indices <= diagonal_progress
    elif direction == "right_to_left":
        mask = x_indices >= width - diagonal_progress
    else:
        raise ValueError("Invalid direction")
    for c in range(channel_length):
        transition_frame[:, :, c] = np.where(mask, frame2[:,:,c], frame1[:, :, c])
    return transition_frame

def clip_scale(image, frame_number, frame_count,multiplier=1.0,curve="linear"):
    scale = curve_value(frame_number, 0, 0.05,frame_count,"",multiplier,curve)
    original_width = image.shape[1]
    original_height = image.shape[0]
    
    increasment_horizontal = math.ceil(original_width * scale)
    increasment_vertical = math.ceil(original_height * scale)
    
    
    if increasment_horizontal == 0 and increasment_vertical == 0:
        return image
     
    image_width = image.shape[1]
    image_height = image.shape[0]
     
    input_frame = image
    
    
    vertex_left = - original_width * scale 
    vertex_right = original_width * scale + original_width
    vertex_top = - original_height * scale
    vertex_bottom = original_height * scale + original_height
    
    larger_left = math.floor(vertex_left)
    larger_right = math.ceil(vertex_right)
    larger_top = math.floor(vertex_top)
    larger_bottom = math.ceil(vertex_bottom)
    
    larger_width = larger_right - larger_left
    larger_height = larger_bottom - larger_top
    
    smaller_left = math.ceil(vertex_left)
    smaller_right = math.floor(vertex_right)
    smaller_top = math.ceil(vertex_top)
    smaller_bottom = math.floor(vertex_bottom) 
    
    smaller_width = smaller_right - smaller_left
    smaller_height = smaller_bottom - smaller_top
    
    
    if image_width != larger_width or image_height != larger_height:
        # larger_frame = cv2.resize(np.copy(input_frame),(larger_width,larger_height),interpolation=cv2.INTER_CUBIC)
        larger_frame = resize_image_with_pil(np.copy(input_frame),(larger_width,larger_height))
    else:
        larger_frame = np.copy(input_frame)
       
       
    
    if image_width != smaller_width or image_height != smaller_height:
        # smaller_frame = cv2.resize(np.copy(input_frame),(smaller_width,smaller_height),interpolation=cv2.INTER_CUBIC)
        smaller_frame = resize_image_with_pil(np.copy(input_frame),(smaller_width,smaller_height))
    else:
        smaller_frame = np.copy(input_frame)
        
        
        
        
    # if larger_frame.shape == smaller_frame.shape:
    #     return larger_frame
        
        
        
    
    
    if vertex_left == math.floor(vertex_left):
        opacity_left = 0
    else:
        opacity_left = math.ceil(vertex_left) - vertex_left
        
    if vertex_right == math.ceil(vertex_right):
        opacity_right = 0
    else:
        opacity_right = vertex_right - math.floor(vertex_right)
        
    
    if vertex_top == math.floor(vertex_top):
        opacity_top = 0
    else:
        opacity_top = math.ceil(vertex_top) - vertex_top
    
    if vertex_bottom == math.ceil(vertex_bottom):
        opacity_bottom = 0
    else:
        opacity_bottom = vertex_bottom - math.floor(vertex_bottom)
        
        
    opacity_count = 0
    if vertex_left == math.floor(vertex_left):
        opacity_left = 0
    else:
        opacity_left = math.ceil(vertex_left) - vertex_left
        larger_frame[:,0,3] = larger_frame[:,0,3] * opacity_left
        opacity_count += 1
        
    if vertex_right == math.ceil(vertex_right):
        opacity_right = 0
    else:
        opacity_right = vertex_right - math.floor(vertex_right)
        larger_frame[:,larger_width-1,3] = larger_frame[:,larger_width-1,3] * opacity_right
        opacity_count += 1
        
    
    if vertex_top == math.floor(vertex_top):
        opacity_top = 0
    else:
        opacity_top = math.ceil(vertex_top) - vertex_top
        larger_frame[0,:,3] = larger_frame[0,:,3] * opacity_top
        opacity_count += 1
    
    if vertex_bottom == math.ceil(vertex_bottom):
        opacity_bottom = 0
    else:
        opacity_bottom = vertex_bottom - math.floor(vertex_bottom)
        larger_frame[larger_height-1,:,3] = larger_frame[larger_height-1,:,3] * opacity_bottom
        opacity_count += 1
    
    
    if opacity_count != 0:
        larger_opacity = (opacity_top + opacity_left + opacity_right + opacity_bottom) / opacity_count
    else:
        larger_opacity = 0
    smaller_opacity = 1 - larger_opacity
    
    # larger_frame[:,:,3] = round(larger_opacity * 255)
    
    larger_frame[smaller_top-larger_top:smaller_height+smaller_top-larger_top,smaller_left-larger_left:smaller_width+smaller_left-larger_left,:] = larger_frame[smaller_top-larger_top:smaller_height+smaller_top-larger_top,smaller_left-larger_left:smaller_width+smaller_left-larger_left,:] * larger_opacity + smaller_frame[:,:,:] * smaller_opacity
    # larger_frame[smaller_top-larger_top:smaller_height+smaller_top-larger_top,smaller_left-larger_left:smaller_width+smaller_left-larger_left,:] = smaller_frame[:,:,:] * 0.5
    
    
    
    return larger_frame[increasment_vertical:increasment_vertical+image_height,increasment_horizontal:increasment_horizontal+image_width]
     
     
    scale_image = cv2.resize(image,(original_width + increasment_horizontal*2,original_height + increasment_vertical*2),interpolation=cv2.INTER_LINEAR)
    return scale_image[increasment_vertical:original_height+increasment_vertical,increasment_horizontal:original_width+increasment_horizontal]

     
     

def clip_translation_horizontal(frame1, frame2, frame_number, frame_count,direction="left_to_right",multiplier=1.0,curve="linear"):
    if frame1 is None:
        height, width = frame2.shape[:2]
    else:
        height, width = frame1.shape[:2]
        
    y_indices, x_indices = np.indices((height, width))
    diagonal_length = width
    diagonal_progress = curve_value(frame_number, 0, diagonal_length,frame_count,"",multiplier,curve)
    
    print("         FRAME NUMBER - ",frame_number)
    print("         DIAGONAL - ",diagonal_progress)
    
    # offset = round(diagonal_progress)
    offset = math.ceil(diagonal_progress)
    
    print("         OFFSET - ",offset)
    if frame1 is None:
        frame1 = np.zeros((height, width, 4), dtype=np.uint8)
    if frame2 is None:
        frame2 = np.zeros((height, width, 4), dtype=np.uint8)
        
    # 입력 이미지의 채널 수 확인
    if frame1.shape[2] == 4:  # 알파 채널이 있는 경우
        channel_length = 4
    else:
        channel_length = 3  # 알파 채널이 없는 경우
    transition_frame = np.zeros((height,width,channel_length),dtype=np.uint8)
    
    # 방향에 따라 프레임 처리 로직을 다르게 적용합니다.
    if direction == "right_to_left":
        # frame1 처리 (왼쪽으로 밀림)
        if offset <= width:
            transition_frame[:, :width-offset, :3] = frame1[:, offset:, :3]
            if channel_length == 4:  # 알파 채널 존재 확인
                transition_frame[:, :width-offset, 3] = frame1[:, offset:, 3]
        # frame2 처리 (왼쪽에서 나타남)
        if offset >= 0:
            transition_frame[:, width-offset:, :3] = frame2[:, :offset, :3]
            if channel_length == 4:  # 알파 채널 존재 확인
                transition_frame[:, width-offset:, 3] = frame2[:, :offset, 3]
    elif direction == "left_to_right":
        # frame1 처리 (오른쪽으로 밀림)
        if offset <= width:
            transition_frame[:, offset:, :3] = frame1[:, :width-offset, :3]
            if channel_length == 4:  # 알파 채널 존재 확인
                transition_frame[:, offset:, 3] = frame1[:, :width-offset, 3]
        # frame2 처리 (오른쪽에서 나타남)
        if offset >= 0:
            transition_frame[:, :offset, :3] = frame2[:, width-offset:, :3]
            if channel_length == 4:  # 알파 채널 존재 확인
                transition_frame[:, :offset, 3] = frame2[:, width-offset:, 3]
    return transition_frame
    
def clip_translation_vertical(frame1, frame2, frame_number, frame_count,direction="top_to_bottom",multiplier=1.0,curve="linear"):
    if frame1 is None and frame2 is not None:
        height, width = frame2.shape[:2]
    elif frame2 is None and frame1 is not None:
        height, width = frame1.shape[:2]
    else:
        # 두 프레임 중 하나는 None이 아니어야 합니다.
        raise ValueError("At least one frame must be provided")
    diagonal_progress = curve_value(frame_number, 0, height,frame_count,"",multiplier,curve)
    offset = round(diagonal_progress)
    if frame1 is None:
        frame1 = np.zeros((height, width, 4), dtype=np.uint8)
    if frame2 is None:
        frame2 = np.zeros((height, width, 4), dtype=np.uint8)
    # 입력 이미지의 채널 수 확인
    channel_length = frame1.shape[2] if frame1 is not None else frame2.shape[2]
    transition_frame = np.zeros((height, width, channel_length), dtype=np.uint8)
    if direction == "top_to_bottom":
        # frame1 처리 (아래로 미는 효과)
        if offset <= height:
            transition_frame[offset:, :, :3] = frame1[:height-offset, :, :3]
            if channel_length == 4:
                transition_frame[offset:, :, 3] = frame1[:height-offset, :, 3]
        # frame2 처리 (위에서 나타남)
        if offset <= height:
            transition_frame[:offset, :, :3] = frame2[height-offset:, :, :3]
            if channel_length == 4:
                transition_frame[:offset, :, 3] = frame2[height-offset:, :, 3]
    elif direction == "bottom_to_top":
        # frame1 처리 (위로 미는 효과)
        if offset <= height:
            transition_frame[:height-offset, :, :3] = frame1[offset:, :, :3]
            if channel_length == 4:
                transition_frame[:height-offset, :, 3] = frame1[offset:, :, 3]
        # frame2 처리 (아래에서 나타남)
        if offset <= height:
            transition_frame[height-offset:, :, :3] = frame2[:offset, :, :3]
            if channel_length == 4:
                transition_frame[height-offset:, :, 3] = frame2[:offset, :, 3]
    return transition_frame

def wiper_circle(frame1, frame2, frame_number, frame_count,multiplier=1.0,curve="linear"):
    height, width = frame1.shape[:2]
    center_x, center_y = width // 2, height // 2
    max_distance = np.sqrt(center_x**2 + center_y**2)
    
        # const pausingTime = 0.4
        # const firstDuration = duration/2
        # const secondDuration = duration - pausingTime - firstDuration
        # if (time < firstDuration){
        #     radius = curveValue(time, curve, 0, 40, firstDuration, 3); 
        # }
        # else if (time >= firstDuration && time < firstDuration + pausingTime){
        #     radius = 40
        # }
        # else{
        #     radius = curveValue(time - firstDuration - pausingTime, curve, 40, 100, secondDuration, 1); 
        # }
    curve = "ease_in_out"
    pausing_time = 0.4 * time_conversion_value
    first_duration = frame_count/2
    second_duration = frame_count - pausing_time - first_duration
    first_dist = round(max_distance/10*4)
    if frame_number < first_duration:
        current_radius = curve_value(frame_number, 0, first_dist,first_duration,"",3,curve)
    elif frame_number >= first_duration and frame_number < first_duration + pausing_time:
        current_radius = first_dist
    else:
        current_radius = curve_value(frame_number-first_duration, first_dist, max_distance,second_duration,"",1,curve)
        
        
        
        
    # X와 Y 좌표의 그리드 생성
    Y, X = np.ogrid[:height, :width]
    # 중심으로부터의 거리 계산
    distances = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
    # 현재 반지름보다 거리가 작거나 같은 위치의 마스크
    mask = distances <= current_radius
    # 조건에 따라 frame2 또는 frame1에서 픽셀 선택
    transition_frame = np.where(mask[:,:,None], frame2, frame1)
    return transition_frame

def wiper_circle02(frame1, frame2, frame_number, frame_count, pause_ratio=0.4, pause_duration=0.3):
    height, width = frame1.shape[:2]
    center_x, center_y = width // 2, height // 2
    max_distance = np.sqrt(center_x**2 + center_y**2)
    # 중간 지점에서의 멈춤을 계산
    pause_point = frame_count * pause_ratio
    pause_end = pause_point + (frame_count * pause_duration)
    if frame_number < pause_point:
        progress_ratio = curve_value(frame_number,0,float(frame_number) / float(frame_count),frame_count,"")
    elif frame_number < pause_end:
        progress_ratio = float(frame_number) / float(frame_count)
    else:
        progress_ratio = curve_value(frame_number,float(frame_number) / float(frame_count),(frame_number - pause_end) / (frame_count - pause_end) * (1 - pause_ratio),frame_count,"")
    current_radius = progress_ratio * max_distance
    Y, X = np.ogrid[:height, :width]
    distances = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
    mask = distances <= current_radius
    transition_frame = np.where(mask[:,:,None], frame2, frame1)
    return transition_frame
# ---------------------------------
# ---------------------------------
# ---------------------------------
# ---------------------------------





# @jit(nopython=True,cache=True)
def merge(frame, frame_number, merging_frame, x_start,y_start,opacity=0.0,rotation=0.0,effects=[],object={}):
     
     if rotation != 0.0:
         [merging_frame,offset_x, offset_y] = apply_rotation(merging_frame,-rotation)
         x_start -= offset_x
         y_start -= offset_y
        #  x_start += round(offset_x*2)
        #  y_start -= round(offset_y*2)
         
     x_end = x_start + merging_frame.shape[1]
     y_end = y_start + merging_frame.shape[0]
     
     if x_start > VIDEO_WIDTH or y_start > VIDEO_HEIGHT or x_end < 0 or y_end < 0 :
         return frame
     
     background_x_start = x_start if x_start >=0 else 0
     background_x_end = x_end if x_end <= VIDEO_WIDTH else VIDEO_WIDTH
     background_y_start = y_start if y_start >= 0 else 0
     background_y_end = y_end if y_end <= VIDEO_HEIGHT else VIDEO_HEIGHT
     
     input_x_start = -x_start if x_start < 0 else 0
     input_x_end = merging_frame.shape[1] - x_end + VIDEO_WIDTH if x_end > VIDEO_WIDTH else merging_frame.shape[1]
     input_y_start = -y_start if y_start < 0 else 0
     input_y_end = merging_frame.shape[0]-y_end + VIDEO_HEIGHT if y_end > VIDEO_HEIGHT else merging_frame.shape[0]
     
     for effect in effects:
         duration_frame_count = effect["duration_frame_count"]
         calibrated_frame_number = frame_number - round((object["init_time"] + effect["start_time"])*time_conversion_value*VIDEO_FRAMERATE)
         if calibrated_frame_number <= duration_frame_count and calibrated_frame_number >= 0:
             

             if effect["d_value"] == 1: # wiper_vertical_disappear
                 merging_frame = wiper_vertical(merging_frame,None,calibrated_frame_number,duration_frame_count,"top_to_bottom",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 2: # wiper_vertical_appear
                 merging_frame = wiper_vertical(None,merging_frame,calibrated_frame_number,duration_frame_count,"top_to_bottom",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 3: # wiper_vertical_disappear_reverse
                 merging_frame = wiper_vertical(merging_frame,None,calibrated_frame_number,duration_frame_count,"bottom_to_top",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 4: # wiper_vertical_appear_reverse
                 merging_frame = wiper_vertical(None,merging_frame,calibrated_frame_number,duration_frame_count,"bottom_to_top",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 11: # wiper_horizontal_disappear
                 merging_frame = wiper_horizontal(merging_frame,None,calibrated_frame_number,duration_frame_count,"left_to_right",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 12: # wiper_horizontoal_appear
                 merging_frame = wiper_horizontal(None,merging_frame,calibrated_frame_number,duration_frame_count,"left_to_right",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 31: # clip_horizontal_disappear
                 merging_frame = clip_translation_horizontal(merging_frame,None,calibrated_frame_number,duration_frame_count,"left_to_right",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 32: # clip_horizontoal_appear
                 merging_frame = clip_translation_horizontal(None,merging_frame,calibrated_frame_number,duration_frame_count,"left_to_right",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 33: # clip_horizontal_disappear_reverse
                 merging_frame = clip_translation_horizontal(merging_frame,None,calibrated_frame_number,duration_frame_count,"right_to_left",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 34: # clip_horizontoal_appear_reverse
                 merging_frame = clip_translation_horizontal(None,merging_frame,calibrated_frame_number,duration_frame_count,"right_to_left",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 21: # clip_vertical_disappear
                 merging_frame = clip_translation_vertical(merging_frame,None,calibrated_frame_number,duration_frame_count,"top_to_bottom",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 22: # clip_vertical_appear
                 merging_frame = clip_translation_vertical(None,merging_frame,calibrated_frame_number,duration_frame_count,"top_to_bottom",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 24: # clip_vertical_appear
                 merging_frame = clip_translation_vertical(None,merging_frame,calibrated_frame_number,duration_frame_count,"bottom_to_top",effect["multiplier"],effect["curve"])
             elif effect["d_value"] == 505:
                 merging_frame = clip_scale(merging_frame,calibrated_frame_number,duration_frame_count,effect["multiplier"],effect["curve"])

     input = merging_frame[input_y_start:input_y_end,input_x_start:input_x_end]
     input_alpha = input[:, :, 3] / 255.0
     alpha = opacity
     if alpha >= 1:
         alpha = 1
     elif alpha <= 0:
         alpha =0
          
     alpha = input_alpha * alpha
     
    #  print(x_start,x_end,y_start,y_end)
     
     
     background = frame[background_y_start:background_y_end,background_x_start:background_x_end]
     overlay_image = alpha_blending(input[:, :, :3], background, alpha)
     frame[background_y_start:background_y_end,background_x_start:background_x_end] = overlay_image
     
     return frame






    
    
@jit(nopython=True,cache=True)
def crop(image, pixel_width, pixel_height, inner_translation_x, inner_translation_y):
    original_height, original_width = image.shape[:2]
    
    
    
    print("-----INNER------start")
    print(inner_translation_x)
    print(inner_translation_y)
    print("-----INNER------end")
    
    if pixel_width/pixel_height >= original_width/original_height:
        print("HERE - 1")
        new_height = pixel_height * original_width / pixel_width
        if (inner_translation_y != 0.0):
            offset_y = (inner_translation_y * original_height / 100)
        else:
            offset_y = 0
            
        x_start = 0
        y_start = math.floor((original_height/2 - new_height/2) + offset_y)
        x_end = x_start+original_width
        y_end = y_start+math.ceil(new_height)
        
        if y_start < 0:
            y_start = 0
            y_end -= y_start
        if y_end > image.shape[0]:
            y_end = image.shape[0]
            y_start -= (y_end - image.shape[0])
        
        cropped_image = image[y_start:y_end, x_start:x_end]
        
    else:
        print("HERE - 2")
        new_width = pixel_width * original_height / pixel_height
        if (inner_translation_x != 0.0):
            offset_x = (inner_translation_x * original_width / 100)
        else:
            offset_x = 0
            
        x_start = math.floor((original_width/2 - new_width/2) + offset_x)
        y_start = 0
        x_end = x_start+math.ceil(new_width)
        y_end = y_start+original_height
        
        if x_start < 0:
            x_start = 0
            x_end -= x_start
        if x_end > image.shape[1]:
            x_end = image.shape[1]
            x_start -= (x_end - image.shape[1])
        
        cropped_image = image[y_start:y_end,x_start:x_end]
        
    return cropped_image

def apply_rotation(image, rotation):
    height, width = image.shape[:2]

    diagonal = np.sqrt(width ** 2 + height ** 2)
    new_width, new_height = int(diagonal), int(diagonal)

    new_image = np.zeros((new_height, new_width, 4), dtype=np.uint8)

    offsetX = (new_width - width) // 2
    offsetY = (new_height - height) // 2
    new_image[offsetY:offsetY+height, offsetX:offsetX+width] = image

    center = (new_width // 2, new_height // 2)
    M = cv2.getRotationMatrix2D(center, rotation, 1)

    rgb_image = new_image[..., :3]
    alpha_channel = new_image[..., 3]

    rotated_rgb = cv2.warpAffine(rgb_image, M, (new_width, new_height), flags=cv2.INTER_LINEAR)

    rotated_alpha = cv2.warpAffine(alpha_channel, M, (new_width, new_height), flags=cv2.INTER_LINEAR)

    rotated_image = np.zeros((new_height, new_width, 4), dtype=np.uint8)
    rotated_image[..., :3] = rotated_rgb
    rotated_image[..., 3] = rotated_alpha


    return [rotated_image, offsetX, offsetY]




# ---------------------------------
# ---------------------------------
# ---------------------------------
# ---------------------------------
# ---------------------------------

def apply_overlay(foreground, background,alpha):
    for c in range(0, 4):
        foreground[:, :, c] = (alpha) * foreground[:, :, c] + (1 - alpha) * background[:, :, c]
    return foreground

def apply_blur(image, blur_degree=200.0, isSidePadding=True):
    
    original_width = image.shape[1]
    original_height = image.shape[0]
    
    
    increasement_horizontal = 0
    increasement_vertical = 0
    if isSidePadding:
        increasement_horizontal = round(original_width * 0.02)
        increasement_vertical = round(original_height * 0.02)
        # image = cv2.resize(image,(original_width + increasement_horizontal*2,original_height + increasement_vertical*2),interpolation=cv2.INTER_CUBIC)
        image = resize_image_with_pil(image,(original_width + increasement_horizontal*2,original_height + increasement_vertical*2))
        
    
        
    if blur_degree == 0:
        if isSidePadding:
            image = image[increasement_vertical:original_height+increasement_vertical,increasement_horizontal:original_width+increasement_horizontal]
    
        return image
    else:
        max_kernel_size = 31
        kernel_size = int((max_kernel_size - 1) * (blur_degree / 100)) + 1
        kernel_size = kernel_size + 1 if kernel_size % 2 == 0 else kernel_size
        blur_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        
        if isSidePadding: 
            return blur_image[increasement_vertical:original_height+increasement_vertical,increasement_horizontal:original_width+increasement_horizontal]
        else:
            return blur_image
            
def apply_fit(background_image, inner_image, object):
    if "inner_background_color" in object and object["inner_background_color"] == "blur":
        print("Apply Blur")
        background_image = apply_blur(background_image,200,True)
        print("Apply Blur - ",background_image.shape)
    background_height = background_image.shape[0]
    background_width = background_image.shape[1]
    
    inner_height = inner_image.shape[0]
    inner_width = inner_image.shape[1]
    
    if background_height/background_width <= inner_height/inner_width:
        resized_inner_width = round(background_height / inner_height * inner_width)
        
        # resize_image = cv2.resize(inner_image,(resized_inner_width,background_height),interpolation=cv2.INTER_CUBIC)
        resize_image = resize_image_with_pil(inner_image,(resized_inner_width,background_height))
        
        x_start = round((background_width - resized_inner_width)/2)
        y_start = 0
        x_end = x_start + resized_inner_width
        y_end = y_start + background_height
        
    else:
        
        resized_inner_height = round(background_width / inner_width * inner_height)
        # resize_image = cv2.resize(inner_image,(background_width,resized_inner_height),interpolation=cv2.INTER_CUBIC)
        resize_image = resize_image_with_pil(inner_image,(background_width,resized_inner_height))
        
        x_start = 0
        y_start = round((background_height - resized_inner_height)/2)
        x_end = x_start + background_width
        y_end = y_start + resized_inner_height
    background_image[y_start:y_end,x_start:x_end] = resize_image
    
    return background_image   

def inner_mode_image(image,pixel_width, pixel_height,object):
    
    if "inner_translation_x" in object and object["inner_translation_x"] is not None:
        inner_translation_x = object["inner_translation_x"]
    else:
        inner_translation_x = 0
    
    if "inner_translation_y" in object and object["inner_translation_y"] is not None:
        inner_translation_y = object["inner_translation_y"]
    else:
        inner_translation_y = 0
        
    
        
        
    if "inner_mode" not in object:
        return crop(image, pixel_width,pixel_height,inner_translation_x,inner_translation_y)

    if (object["inner_mode"] == "fit"):
        if (object["inner_background_color"] != "blur"):
            r = int(object["inner_background_color"][1:3], 16) 
            g = int(object["inner_background_color"][3:5], 16)  
            b = int(object["inner_background_color"][5:7], 16) 
            a = int(object["inner_background_color"][7:9],16)
            background_image = np.full((pixel_height,pixel_width, 4), (b,g,r,a),dtype=np.uint8)
            return apply_fit(background_image,image, object)
        else:
            background_image = crop(image, pixel_width,pixel_height,inner_translation_x,inner_translation_y)
            print("Background Image - ",background_image.shape)
            return apply_fit(background_image,image, object)
    else:
        return crop(image, pixel_width,pixel_height,inner_translation_x,inner_translation_y)





# ---------------------------------
# 
# @jit(nopython=True,cache=True)
def calibrate_frame(input_frame,percent_x,percent_y,percent_width, percent_height):
    image_width = input_frame.shape[1]
    image_height = input_frame.shape[0]
    
    
    
    vertex_left = percent_x / 100 * VIDEO_WIDTH
    vertex_right = (percent_x + percent_width) / 100 * VIDEO_WIDTH
    vertex_top = percent_y / 100 * VIDEO_HEIGHT
    vertex_bottom = (percent_y + percent_height) / 100 * VIDEO_HEIGHT
    
    larger_left = math.floor(vertex_left)
    larger_right = math.ceil(vertex_right)
    larger_top = math.floor(vertex_top)
    larger_bottom = math.ceil(vertex_bottom)
    
    larger_width = larger_right - larger_left
    larger_height = larger_bottom - larger_top
    
    smaller_left = math.ceil(vertex_left)
    smaller_right = math.floor(vertex_right)
    smaller_top = math.ceil(vertex_top)
    smaller_bottom = math.floor(vertex_bottom) 
    
    smaller_width = smaller_right - smaller_left
    smaller_height = smaller_bottom - smaller_top
    
    
    if image_width != larger_width or image_height != larger_height:
        # larger_frame = cv2.resize(np.copy(input_frame),(larger_width,larger_height),interpolation=cv2.INTER_CUBIC)
        larger_frame = resize_image_with_pil(np.copy(input_frame),(larger_width,larger_height))
    else:
        larger_frame = np.copy(input_frame)
       
       
    
    if image_width != smaller_width or image_height != smaller_height:
        # smaller_frame = cv2.resize(np.copy(input_frame),(smaller_width,smaller_height),interpolation=cv2.INTER_CUBIC)
        smaller_frame = resize_image_with_pil(np.copy(input_frame),(larger_width,larger_height))
    else:
        smaller_frame = np.copy(input_frame)
        
        
        
        
    if larger_frame.shape == smaller_frame.shape:
        return larger_frame
        
        
        
    
    
    if vertex_left == math.floor(vertex_left):
        opacity_left = 0
    else:
        opacity_left = math.ceil(vertex_left) - vertex_left
        
    if vertex_right == math.ceil(vertex_right):
        opacity_right = 0
    else:
        opacity_right = vertex_right - math.floor(vertex_right)
        
    
    if vertex_top == math.floor(vertex_top):
        opacity_top = 0
    else:
        opacity_top = math.ceil(vertex_top) - vertex_top
    
    if vertex_bottom == math.ceil(vertex_bottom):
        opacity_bottom = 0
    else:
        opacity_bottom = vertex_bottom - math.floor(vertex_bottom)
        
        
        
        
        
        
    opacity_count = 0
    if vertex_left == math.floor(vertex_left):
        opacity_left = 0
    else:
        opacity_left = math.ceil(vertex_left) - vertex_left
        # larger_frame[:,0,3] = larger_frame[:,0,3]
        # larger_frame[:,0,0:2] = larger_frame[:,0,0:2] * opacity_left
        opacity_count += 1
        
    if vertex_right == math.ceil(vertex_right):
        opacity_right = 0
    else:
        opacity_right = vertex_right - math.floor(vertex_right)
        # larger_frame[:,larger_width-1,3] = larger_frame[:,larger_width-1,3] * opacity_right
        # larger_frame[:,larger_width-1,0:2] = larger_frame[:,larger_width-1,0:2] * opacity_right
        opacity_count += 1
        
    
    if vertex_top == math.floor(vertex_top):
        opacity_top = 0
    else:
        opacity_top = math.ceil(vertex_top) - vertex_top
        # larger_frame[0,:,3] = larger_frame[0,:,3] * opacity_top
        # larger_frame[0,:,0:2] = larger_frame[0,:,0:2] * opacity_top
        # larger_frame[0,:,0:2] = 255
        opacity_count += 1
    
    if vertex_bottom == math.ceil(vertex_bottom):
        opacity_bottom = 0
    else:
        opacity_bottom = vertex_bottom - math.floor(vertex_bottom)
        # larger_frame[larger_height-1,:,3] = larger_frame[larger_height-1,:,3] * opacity_bottom
        # larger_frame[larger_height-1,:,:2] = larger_frame[larger_height-1,:,0:2] * opacity_bottom
        # larger_frame[larger_height-1,:,:2] = 1
        opacity_count += 1
    
    if opacity_count != 0:
        larger_opacity = (opacity_top + opacity_left + opacity_right + opacity_bottom) / opacity_count
    else:
        larger_opacity = 0
    smaller_opacity = 1 - larger_opacity
    
    # larger_frame[:,:,3] = round(larger_opacity * 255)
    
    larger_frame[smaller_top-larger_top:smaller_height+smaller_top-larger_top,smaller_left-larger_left:smaller_width+smaller_left-larger_left,:] = larger_frame[smaller_top-larger_top:smaller_height+smaller_top-larger_top,smaller_left-larger_left:smaller_width+smaller_left-larger_left,:] * larger_opacity + smaller_frame[:,:,:] * smaller_opacity
    # larger_frame[smaller_top-larger_top:smaller_height+smaller_top-larger_top,smaller_left-larger_left:smaller_width+smaller_left-larger_left,:] = smaller_frame[:,:,:] * 0.5
    
    return larger_frame
    
    
    
    
    
    if percent_x == int(percent_x):
        horizontal_frame = input_frame
    else:
        opacity = 1 - (percent_x - math.floor(percent_x))
        horizontal_frame = np.zeros((image_width + 1,image_height,4),dtype=np.uint8)
        horizontal_frame[:,0,:] = input_frame[:,0,:]
        horizontal_frame[:,0,3] = round(255*opacity)
        horizontal_frame[:,image_width,:] = input_frame[:,image_width - 1,:]
        horizontal_frame[:,image_width,3] = round(255*(1-opacity))
        horizontal_frame[:,1:image_width,:] = input_frame[:,0:image_width-1,:] * opacity + input_frame[:,1:image_width,:] * (1-opacity)
    
    
    if percent_y == int(percent_y):
        vertical_frame = horizontal_frame
    else:
        opacity = 1 - (percent_y - math.floor(percent_y))
        vertical_frame = np.zeros((horizontal_frame.shape[1],image_height+1,4),dtype=np.uint8)
        vertical_frame[0,:,:] = horizontal_frame[0,:,:]
        vertical_frame[0,:,3] = round(255*opacity)
        vertical_frame[image_height,:,:] = horizontal_frame[image_height-1,:,:]
        vertical_frame[image_height,:,3] = round(255*(1-opacity))
        vertical_frame[1:image_height,:,:] = horizontal_frame[0:image_height-1,:,:] * opacity + horizontal_frame[1:image_height,:,:] * (1-opacity)
        
    return vertical_frame
        
        
    
    
        
    
    
    return input_frame
#
# ---------------------------------






def add_image_frame(frame,object,frame_number,is_last_frame):
    if object["init_frame_number"]  >= frame_number:
        instance_container[object["uid"]] = {}
        print("[CASE - 1]", object["uid"])
        if "image_url" not in object:
            print("[CASE - 1.2]")
            return frame
        
        print("[CASE - 1.1]")
        
        img_url = object["image_url"]
        if object["is_user_def"] == True:
            input_image = cv2.imread(f"{user_res_dircetory}/{img_url}",cv2.IMREAD_UNCHANGED)
        else:
            input_image = cv2.imread(f"{admin_res_directory}/{img_url}",cv2.IMREAD_UNCHANGED)
        
        if input_image is None:
            print("NULL - ",object["uid"])
            return frame
        
        # print("1@@",object["image_url"],"----",input_image.shape,"@@")
        
        input_image = cv2.cvtColor(input_image,cv2.COLOR_BGR2BGRA)
        
        # print("2@@",object["image_url"],"----",input_image.shape,"@@")
        
        input_width = math.ceil(object["width"] * VIDEO_WIDTH / 100)
        input_height = math.ceil(object["height"] * VIDEO_HEIGHT / 100)
        
        input_image = inner_mode_image(input_image,input_width,input_height,object)
        # print("3@@",object["image_url"],"----",input_image.shape,"@@")
        # input_image = cv2.resize(input_image,(input_width,input_height),interpolation=cv2.INTER_CUBIC)
        input_image = resize_image_with_pil(input_image,(input_width,input_height))
        
        
        
        if "mask_url" in object and object["mask_url"] is not None:
            mask_image = cv2.imread(f"{admin_res_directory}/"+object["mask_url"],cv2.IMREAD_UNCHANGED)
            if mask_image is not None:
                # mask_image = cv2.resize(mask_image,(input_width,input_height),interpolation=cv2.INTER_CUBIC)
                mask_image = resize_image_with_pil(mask_image,(input_width,input_height))
                input_image = apply_masking(input_image, mask_image)
        
        if "border_width" in object and object["border_width"] is not None and object["border_color"] is not None and "border_color" in object:
            border_width = round(VIDEO_HEIGHT * object["border_width"] / 100.0)
            border_color = object["border_color"]
            input_image = add_border_line(input_image,border_width,border_color)
            
        if "border_radius" in object and object["border_radius"] is not None and object["border_radius"] != 0.0:
            input_image = add_border_radius(input_image,VIDEO_HEIGHT*object["border_radius"]/100)
        
        instance_container[object["uid"]]["frame"] = input_image
        
        
        print("SIZE - ",object["uid"],input_image.shape)
        
        
    elif is_last_frame:
        if object["uid"] in instance_container:
            instance_container[object["uid"]]["frame"] = None
            instance_container[object["uid"]] = None
        return frame
    
    if object["uid"] in instance_container and instance_container[object["uid"]] is not None:
        style = toStyle(frame_number, object)
        
        x_start = math.floor(style["left"]/100 * VIDEO_WIDTH)
        y_start = math.floor(style["top"]/100 * VIDEO_HEIGHT)
        
        if "frame" not in instance_container[object["uid"]]:
            return frame
        input_image = instance_container[object["uid"]]["frame"]
        
        ###### temp code ######
        # width = math.ceil(style["width"] / 100 * VIDEO_WIDTH)
        # height = math.ceil(style["height"] / 100 * VIDEO_HEIGHT)
        # input_image = cv2.resize(input_image,(width, height),interpolation=cv2.INTER_LINEAR)
        ###### temp code ######
        
        if object["is_user_def"]:
            calibrated_frame = calibrate_frame(input_image,style["left"],style["top"],style["width"],style["height"])
            return merge(frame,frame_number,calibrated_frame,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
        
        else:
            width = math.ceil(style["width"] / 100 * VIDEO_WIDTH)
            height = math.ceil(style["height"] / 100 * VIDEO_HEIGHT)
            # input_image = cv2.resize(input_image,(width, height),interpolation=cv2.INTER_AREA)
            input_image = resize_image_with_pil(input_image,(width,height))
            return merge(frame,frame_number,input_image,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
            
        
        width = math.ceil(style["width"] / 100 * VIDEO_WIDTH)
        height = math.ceil(style["height"] / 100 * VIDEO_HEIGHT)
        input_image = cv2.resize(input_image,(width, height),interpolation=cv2.INTER_CUBIC)
        return merge(frame,frame_number,input_image,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
        
        # calibrated_frame = calibrate_frame(input_image,style["left"],style["top"],style["width"],style["height"])
        
        return merge(frame,frame_number,calibrated_frame,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
    return frame



def add_gif_frame(frame,object,frame_number,is_last_frame):
    if object["init_frame_number"]  <= frame_number <= object["deinit_frame_number"]:
        
        curremt_frame_number = frame_number - object["init_frame_number"]
        if "gif_fps" in object and object["gif_fps"] is not None:
            gif_frame_rate = object["gif_fps"]
        else:
            gif_frame_rate = 24
            
        gif_number = int(curremt_frame_number * gif_frame_rate / VIDEO_FRAMERATE / time_conversion_value)
        
        filepath = f"{admin_res_directory}/"+object["gif_url"] + f"/{gif_number}.png"
        input_image = cv2.imread(filepath,cv2.IMREAD_UNCHANGED)
        
        if input_image is not None:
            if (input_image.shape[2] == 3):   
                input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2BGRA)
        
        
        if input_image is None:
            if instance_container[object["uid"]]["frame"] is None:
                return frame
        else:
            input_height = math.ceil(object["height"] / 100 * VIDEO_HEIGHT)
            input_width = math.ceil(object["width"] / 100 * VIDEO_WIDTH)
            # input_image = cv2.resize(input_image,(input_width,input_height),interpolation=cv2.INTER_CUBIC)
            input_image = resize_image_with_pil(input_image,(input_width,input_height))

            instance_container[object["uid"]] = {}
            instance_container[object["uid"]]["frame"] = input_image
        
    elif is_last_frame:
        if object["uid"] in instance_container:
            instance_container[object["uid"]]["frame"] = None
            instance_container[object["uid"]] = None
        return frame
        
    if object["uid"] in instance_container and instance_container[object["uid"]] is not None:
        style = toStyle(frame_number, object)
        
        x_start = math.floor(style["left"]/100 * VIDEO_WIDTH)
        y_start = math.floor(style["top"]/100 * VIDEO_HEIGHT)
        
        if object["uid"] not in instance_container:
            return frame
        
        if "frame" not in instance_container[object["uid"]]:
            return frame
        
        input_image = instance_container[object["uid"]]["frame"]
        
        
        if (input_image is None):
            return frame
        ###### temp code ######
        # width = math.ceil(style["width"] / 100 * VIDEO_WIDTH)
        # height = math.ceil(style["height"] / 100 * VIDEO_HEIGHT)
        # input_image = cv2.resize(input_image,(width, height),interpolation=cv2.INTER_LINEAR)
        
        
        ###### temp code ######
        
        
        
        calibrated_frame = calibrate_frame(input_image,style["left"],style["top"],style["width"],style["height"])
        
        return merge(frame,frame_number,calibrated_frame,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
        
        return merge(frame,frame_number,input_image,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
    return frame

# load & generate & remove text frame
def add_text_frame(frame,object,frame_number,is_last_frame):
    if object["init_frame_number"]  >= frame_number:
        antialiasing_value = 2
        instance_container[object["uid"]] = {}
        
        if "text" not in object:
            return frame
        
        if object["text"] is None or object["text"] == "":
            return frame
        
        if object["text"].strip() == "":
            return frame
        
        
        if "text_letter_spacing" in object:
            letter_spacing = object["text_letter_spacing"] * object["text_size"] * VIDEO_HEIGHT / 10000 * antialiasing_value
        else:
            letter_spacing = 10 * antialiasing_value
            
        
            
        
        
        input_height = math.ceil(object["height"] / 100 * VIDEO_HEIGHT) * antialiasing_value
        input_width = math.ceil(object["width"] / 100 * VIDEO_WIDTH) * antialiasing_value
        
        # x_start = math.floor(style["left"]/100 * VIDEO_WIDTH)
        # y_start = math.floor(style["top"]/100 * VIDEO_HEIGHT)
        
        r = int(object["background_color"][1:3], 16) 
        g = int(object["background_color"][3:5], 16)  
        b = int(object["background_color"][5:7], 16)  
        a = int(object["background_color"][7:9], 16) 
        
        image = Image.new('RGBA', (input_width,input_height), (r,g,b,a))
        
        print("*%*%*",input_width, input_height)
        
        font_path = f"{font_directory}/"+object["font_url"] 
        font = ImageFont.truetype(font_path, object["text_size"] * VIDEO_HEIGHT/100 * antialiasing_value)
        
        text_r = int(object["text_color"][1:3],16)
        text_g = int(object["text_color"][3:5],16)
        text_b = int(object["text_color"][5:7],16)
        text_a = int(object["text_color"][7:9],16)
        d = ImageDraw.Draw(image)
        
        
        
        ascent, descent = font.getmetrics()
        
        original_text = object["text"]
        space_count = original_text.count(' ')
        text_none_space = original_text.replace(' ','')
        text_width = font.getmask(text_none_space).getbbox()[2] + (len(list(original_text)) - 1) * letter_spacing + space_count * object["text_size"] * VIDEO_HEIGHT / 200 * antialiasing_value
                
        # text_height = font.getmask(object["text"]).getbbox()[3]
        
        
        text_height = ascent + abs(descent)
        
        if object["text_align_x"] == 0:
            text_left_position = 0
        elif object["text_align_x"] == 1:
            text_left_position = round(input_width - text_width)
        else:
            text_left_position = round(input_width/2 - text_width/2)
            
        if object["text_align_y"] == 0:
            text_top_position = 0 
        elif object["text_align_y"] == 1:
            text_top_position = round(input_height - text_height) 
        else:
            text_top_position = round(input_height/2 - text_height/2) 
            print("")
            # text_top_position = 0
            
            
        
            
        # if "text_border_width" in object and object["text_border_width"] is not None and "text_border_color" in object and object["text_border_color"] is not None and object["text_border_width"] != 0.0:
        #     text_border_pixel_with = round(VIDEO_HEIGHT * object["text_border_width"]/100.0)
        #     text_border_color = object["text_border_color"]
            
            
            
            
        # object["text_shadow_enable"] = False
                    
            
        if "text_shadow_enable" in object and object["text_shadow_enable"] is True:
            object["text_shadow_radius"] = 1
            object["text_shadow_blur"] = 4
            object["text_shadow_opacity"] = 0.5
            object["text_shadow_color"] = "#000000ff"
            object["text_shadow_offset_x"] = 0.4
            object["text_shadow_offset_y"] = 0.4
                    
                    
        
        if "text_shadow_color" in object and object["text_shadow_color"] is not None:
            shadow_image = Image.new('RGBA', [image.size[0], image.size[1]], (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_image)  
            shadow_r = int(object["text_shadow_color"][1:3],16)
            shadow_g = int(object["text_shadow_color"][3:5],16)
            shadow_b = int(object["text_shadow_color"][5:7],16)
            shadow_a = int(object["text_shadow_color"][7:9],16)
            shadow_color_rgba = (shadow_r, shadow_g, shadow_b, shadow_a)
                 
            text_shadow_offset_x = round(VIDEO_HEIGHT * object["text_shadow_offset_x"] / 100)
            text_shadow_offset_y = round(VIDEO_HEIGHT * object["text_shadow_offset_y"] / 100)
            
            
            
            left_position = text_left_position
            for char in list(object["text"]):
                ascent, descent = font.getmetrics()
                if char == " ":
                    if letter_spacing == 0:
                        left_position += object["text_size"] * VIDEO_HEIGHT / 200* antialiasing_value
                    else:
                        left_position += letter_spacing/2 + letter_spacing*2
                        
                        
                else:
                    char_width = font.getlength(char)
                        
                    shadow_draw.text((left_position+text_shadow_offset_x,text_top_position+text_shadow_offset_y), char, font=font, fill=shadow_color_rgba)
                    # shadow_draw.text((left_position+text_shadow_offset_x,text_top_position+text_shadow_offset_y), char, font=font, fill=shadow_color_rgba)

                    left_position += char_width + letter_spacing
            
            
            
            if "text_shadow_radius" in object and object["text_shadow_radius"] is not None:
                text_shadow_radius = object["text_shadow_blur"]
                shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(text_shadow_radius))
        
            # shadow_image = shadow_image.resize((round(input_width/4),round(input_height/4)),Image.Resampling.LANCZOS)
            shadow_image = np.array(shadow_image)
            shadow_image = cv2.cvtColor(shadow_image, cv2.COLOR_RGBA2BGRA)
        
            if "text_shadow_blur" in object and object["text_shadow_blur"] is not None:
                text_shadow_blur = object["text_shadow_blur"]
                shadow_image = apply_blur(shadow_image,text_shadow_blur,False)
        
            if "text_shadow_opacity" in object and object["text_shadow_opacity"] is not None:
                text_shadow_opacity = object["text_shadow_opacity"]
                shadow_image[:,:,3] = shadow_image[:,:,3] * text_shadow_opacity
                
                
        
        
        left_position = text_left_position
        for char in list(object["text"]):
            ascent, descent = font.getmetrics()
            if char == " ":
                if letter_spacing == 0:
                    left_position += object["text_size"] * VIDEO_HEIGHT / 200* antialiasing_value
                else:
                    left_position += letter_spacing/2 + letter_spacing*2
            else:
                char_width = font.getlength(char)



                d.text((left_position,text_top_position), char, font=font, fill=(text_r,text_g,text_b,text_a))
                # d.text((left_position,text_top_position), char, font=font, fill=(text_r,text_g,text_b,text_a))
                left_position += char_width + letter_spacing
                
        
        
        # image = image.resize((round(input_width/4),round(input_height/4)),Image.Resampling.LANCZOS)
        text_image = np.array(image)
        text_image = cv2.cvtColor(text_image, cv2.COLOR_RGBA2BGRA)
        
        
        
        if "text_shadow_enable" in object and object["text_shadow_enable"] is True:
            alpha = text_image[:, :, 3] / 255.0
            result = apply_overlay(text_image,shadow_image,alpha)
        else:
            result = text_image
            
        # alpha = text_image[:, :, 3] / 255.0
        # result = apply_overlay(text_image,shadow_image,alpha)
        
        # print("SHADOW----",shadow_image.shape)
        # if "text_shadow_color" in object and object["text_shadow_color"] is not None:
        #     alpha = text_image[:, :, 3] / 255.0
        #     result = apply_overlay(text_image,shadow_image,alpha)
        # else:
        #     result = text_image
        # print("!!! - ",result.shape[1])
        # print( "$$$- ",result.shape[0])
        # result = cv2.resize(result,(result.shape[1]/antialiasing_value,result.shape[0]/antialiasing_value),interpolation=cv2.INTER_LINEAR)
        result = resize_image_with_pil(result,(round(input_width/antialiasing_value),round(input_height/antialiasing_value)))
        instance_container[object["uid"]]["frame"] = result
        
    elif is_last_frame:
        if object["uid"] in instance_container:
            instance_container[object["uid"]]["frame"] = None
            instance_container[object["uid"]] = None
        return frame
        
    if object["uid"] in instance_container and instance_container[object["uid"]] is not None:
        style = toStyle(frame_number, object)
        
        x_start = math.floor(style["left"]/100 * VIDEO_WIDTH)
        y_start = math.floor(style["top"]/100 * VIDEO_HEIGHT)
        
        if object["uid"] not in instance_container:
            return frame
        
        if "frame" not in instance_container[object["uid"]]:
            return frame
        
        input_image = instance_container[object["uid"]]["frame"]
        
        
        if (input_image is None):
            return frame
        
        ###### temp code ######
        # width = math.ceil(style["width"] / 100 * VIDEO_WIDTH)
        # height = math.ceil(style["height"] / 100 * VIDEO_HEIGHT)
        # input_image = cv2.resize(input_image,(width, height),interpolation=cv2.INTER_LINEAR)
        ###### temp code ######
        
        
        
        
        calibrated_frame = calibrate_frame(input_image,style["left"],style["top"],style["width"],style["height"])
        
        return merge(frame,frame_number,calibrated_frame,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
        
        
        return merge(frame,frame_number,input_image,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
    return frame

# load & generate & remove empty frame
def add_empty_frame(frame,object,frame_number,is_last_frame):
    if object["init_frame_number"]  >= frame_number:
        instance_container[object["uid"]] = {}
        r = int(object["background_color"][1:3], 16) 
        g = int(object["background_color"][3:5], 16)  
        b = int(object["background_color"][5:7], 16)  
        a = int(object["background_color"][7:9], 16)
         
        
        style = toStyle(frame_number, object)
        
        input_height = math.ceil(object["height"] / 100 * VIDEO_HEIGHT)
        input_width = math.ceil(object["width"] / 100 * VIDEO_WIDTH)
        
        input_image = np.full((input_height,input_width,4), (b,g,r,a), dtype=np.uint8)
        
        x_start = math.floor(style["left"]/100 * VIDEO_WIDTH)
        y_start = math.floor(style["top"]/100 * VIDEO_HEIGHT)
        
        instance_container[object["uid"]]["frame"] = input_image
        
        
    elif is_last_frame:
        if object["uid"] in instance_container:
            instance_container[object["uid"]]["frame"] = None
            instance_container[object["uid"]] = None
        
        
    if object["uid"] in instance_container and instance_container[object["uid"]] is not None:
        style = toStyle(frame_number, object)
        
        x_start = math.floor(style["left"]/100 * VIDEO_WIDTH)
        y_start = math.floor(style["top"]/100 * VIDEO_HEIGHT)
        
        
        if object["uid"] not in instance_container:
            return frame
        
        if "frame" not in instance_container[object["uid"]]:
            return frame
        
        input_image = instance_container[object["uid"]]["frame"]
        
        
        
        ###### temp code ######
        # width = math.ceil(style["width"] / 100 * VIDEO_WIDTH)
        # height = math.ceil(style["height"] / 100 * VIDEO_HEIGHT)
        # input_image = cv2.resize(input_image,(width, height),interpolation=cv2.INTER_LINEAR)
        ###### temp code ######
        
        
        
        
        calibrated_frame = calibrate_frame(input_image,style["left"],style["top"],style["width"],style["height"])
        
        return merge(frame,frame_number,calibrated_frame,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
        
        
        
        
        return merge(frame,frame_number,input_image,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
    return frame


# load & generate & remove video frame   
def add_video_frame(frame,object,frame_number,is_last_frame):
    if object["init_frame_number"] >= frame_number:
        instance_container[object["uid"]] = {}
        # img_url = object["image_url"]
        # input_image = cv2.imread(f"{input_dircetory}/{img_url}",cv2.IMREAD_UNCHANGED)
        input_video = cv2.VideoCapture(f"{user_res_dircetory}/"+object["video_url"])
            
        instance_container[object["uid"]]["frame"] = input_video
        
        
        
    elif is_last_frame:
        if object["uid"] in instance_container:
            instance_container[object["uid"]]["frame"] = None
            instance_container[object["uid"]] = None
            # return frame
        
    if object["uid"] in instance_container and instance_container[object["uid"]] is not None:
        style = toStyle(frame_number, object)
        
        x_start = math.floor(style["left"]/100 * VIDEO_WIDTH)
        y_start = math.floor(style["top"]/100 * VIDEO_HEIGHT)
        
        input_width = math.ceil(object["width"] * VIDEO_WIDTH / 100)
        input_height = math.ceil(object["height"] * VIDEO_HEIGHT / 100)
        
        
        if object["uid"] not in instance_container:
            return frame
        
        if "frame" not in instance_container[object["uid"]]:
            return frame
        
        
        fps = instance_container[object["uid"]]["frame"].get(cv2.CAP_PROP_FPS)
        
        video_start_frame_number = frame_number + object["video_start_frame_number"] * time_conversion_value
        
        calibrated_frame_number = int((video_start_frame_number - object["init_frame_number"]) * fps / VIDEO_FRAMERATE / time_conversion_value)
        
        instance_container[object["uid"]]["frame"].set(cv2.CAP_PROP_POS_FRAMES, calibrated_frame_number)
        success, video_frame = instance_container[object["uid"]]["frame"].read()
        
        
        if (video_frame is None):
            return frame
        
        if success:
            style = toStyle(frame_number, object)
            
            if (video_frame.shape[2] == 3):   
                video_frame = cv2.cvtColor(video_frame, cv2.COLOR_BGR2BGRA)
            
            input_image = inner_mode_image(video_frame,input_width,input_height-1,object)
            
            
            # print("CALIBRATED TIME ",calibrated_frame_number," frame_size ",input_image.shape)
            
            if (input_image is None):
                return frame

            if (input_image.shape[2] == 3):   
                input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2BGRA)
                
            # input_image = cv2.resize(input_image,(input_width,input_height),interpolation=cv2.INTER_LINEAR)
            
            
            
            calibrated_frame = calibrate_frame(input_image,style["left"],style["top"],style["width"],style["height"])

            return merge(frame,frame_number,calibrated_frame,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
            
            
            
            return merge(frame,frame_number,input_image,x_start,y_start,style["opacity"],style["rotation"],style["effects"],object)
        else:
            return frame
        
    return frame
        
# ---------------------------------
# ---------------------------------
# ---------------------------------
# ---------------------------------
# --------------------------------- 
# ---------------------------------
# start loop for generate frame buffer
# for frame_number in range( int(VIDEO_DURATION * VIDEO_FRAMERATE)+1):
for frame_number in range( VIDEO_FRAMERATE*55, VIDEO_FRAMERATE*62):
    current_compositions = [comp for comp in template_compositions if comp["init_frame_number"] <= frame_number <= comp["deinit_frame_number"]]
    # print("sec - ",frame_number /VIDEO_FRAMERATE)
    former_transition_frame = None
    after_transition_frame = None
    composition_frame = None
    
    
    if frame_number / VIDEO_FRAMERATE == int(frame_number / VIDEO_FRAMERATE):
        print("SEC - ",int(frame_number / VIDEO_FRAMERATE))
    
    
    for index,current_composition in enumerate(current_compositions):
        composition_frame = None
        composition_r = int(current_composition["background_color"][1:3], 16) 
        composition_g = int(current_composition["background_color"][3:5], 16) 
        composition_b = int(current_composition["background_color"][5:7], 16) 
        composition_frame = generate_composition_frame(composition_r, composition_g, composition_b)
        for object in current_composition["objects"]:
            if object["enable"] is True and object["visible"] is True:
                if object["init_frame_number"] <= frame_number <= object["deinit_frame_number"]:
                    if object["type"] == "image":
                        composition_frame = add_image_frame(composition_frame,object,frame_number,frame_number == object["deinit_frame_number"])
                    elif object["type"] == "video":
                        composition_frame = add_video_frame(composition_frame, object,frame_number,frame_number == object["deinit_frame_number"])
                    elif object["type"] == "text":
                        composition_frame = add_text_frame(composition_frame,object,frame_number,frame_number == object["deinit_frame_number"])
                    elif object["type"] == "gif":
                        composition_frame = add_gif_frame(composition_frame,object,frame_number,frame_number == object["deinit_frame_number"])
                    elif object["type"] == "empty":
                        composition_frame = add_empty_frame(composition_frame,object,frame_number,frame_number == object["deinit_frame_number"])
                        
          
        if index == 0 and len(current_compositions) == 2:
            former_transition_frame = np.copy(composition_frame)
        elif index == 1 and len(current_compositions) == 2:
            after_transition_frame = np.copy(composition_frame)
        
    
    current_compositions.sort(key=lambda x:x['init_time'],reverse=False)
    
    if len(current_compositions) == 2 and "transition_duration_frame_count" in current_compositions[0] and current_compositions[0]["transition_duration_frame_count"] != None:
    
        if current_compositions[0]["deinit_frame_number"] > frame_number >= current_compositions[0]["deinit_frame_number"] - current_compositions[0]["transition_duration_frame_count"]:
            
            transition_frame_count = current_compositions[0]["transition_duration_frame_count"]
            calibrated_frame_number = frame_number + current_compositions[0]["transition_duration_frame_count"] - current_compositions[0]["deinit_frame_number"]
           
            if current_compositions[0]["type"] == 1:
              composition_frame = wiper_vertical(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count),"top_to_bottom")

            elif current_compositions[0]["type"] == 3:
                composition_frame = wiper_vertical(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count),"bottom_to_top")

            elif current_compositions[0]["type"] == 11:
                composition_frame = wiper_horizontal(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count),"left_to_right")

            elif current_compositions[0]["type"] == 13:
                composition_frame = wiper_horizontal(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count),"right_to_left")

            elif current_compositions[0]["type"] == 21:
                composition_frame = clip_translation_vertical(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count),"top_to_bottom")

            elif current_compositions[0]["type"] == 23:
                composition_frame = clip_translation_vertical(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count),"bottom_to_top")

            elif current_compositions[0]["type"] == 31:
                composition_frame = clip_translation_horizontal(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count),"left_to_right")

            elif current_compositions[0]["type"] == 33:
                composition_frame = clip_translation_horizontal(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count),"right_to_left")

            elif current_compositions[0]["type"] == 42:
                composition_frame = wiper_cross(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count))

            elif current_compositions[0]["type"] == 44:
                composition_frame = wiper_cross(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count),"top_right_to_bottom_left")

            elif current_compositions[0]["type"] == 104:
                composition_frame = wiper_circle(former_transition_frame,after_transition_frame,calibrated_frame_number ,round(transition_frame_count),3)
            
    # composition_frame = resize_image_with_pil(composition_frame,(VIDEO_WIDTH//2,VIDEO_HEIGHT//2))
    video_writer.write(composition_frame)
    composition_frame = None
    
video_writer.release()




command = f"""
ffmpeg -y -i {output_directory}/output{RECORD_ID}.mp4 -i {bgm_file_path} -t {VIDEO_DURATION} -c:v copy -c:a aac -strict experimental {output_directory}/result{RECORD_ID}.mp4
"""
import os

print("OSPATH - ",os.path.curdir)

os.system(command)