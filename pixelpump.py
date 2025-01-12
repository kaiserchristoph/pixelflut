import sys
from PIL import Image
import multiprocessing
import socket

def read_image(file_path):
    try:
        image = Image.open(file_path).convert('RGBA')
        pixels = image.load()
        width, height = image.size
        pixel_array= []

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                if a == 255:
                    pixel_data = f'PX {x} {y} {r:02x}{g:02x}{b:02x}'
                elif a == 0:
                    continue
                else:
                    pixel_data = f'PX {x} {y} {r:02x}{g:02x}{b:02x}{a:02x}'
                pixel_array.append(pixel_data)


        return pixel_array
    except Exception as e:
        print(f"Error reading image: {e}")
        return []


def split_array(arr, n):
    for i in range(n):
        sub_array = arr[i::n]
        yield sub_array


def compress_array(arr, n):
    compressed_array = []
    for i in range(0, len(arr), n):
        compressed_entry = '\n'.join(arr[i:i + n + 1])
        #TODO: why + 1 needed? otherwise last pixel is missing
        compressed_array.append(compressed_entry)
    return compressed_array


def send_pixels(pixel_array, host='localhost', port=1337):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.connect((host, port))
        while True:
            for pixels in pixel_array:
                sock.sendall(pixels.encode('utf-8'))
    except Exception as e:
        print(f"Error sending pixels: {e}")
        return
    

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python pixelpump.py <path_to_png> <host> <port> <num_processes> <pixels_per_packet>")
        sys.exit(1)

    file_path = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])
    num_processes = int(sys.argv[4])
    packet_size = int(sys.argv[5])


    pixel_data = read_image(file_path)


    sub_arrays = list(split_array(pixel_data, num_processes))
   
    processes = []
    for sub_array in sub_arrays:
        compressed_array = compress_array(sub_array, packet_size)
        process = multiprocessing.Process(target=send_pixels, args=(compressed_array, host, port,))
        processes.append(process)
        process.start()

    for process in processes:      
        process.join()    
