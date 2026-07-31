#type:ignore
import anvil
import os
import datetime
import multiprocessing
import argparse
import threading
import time
import datetime
import sys

worker_terminated = 0
worker_done = 0
worker_spacesaved = 0
COMPLETED = False
TOTAL_TO_COMPLETE = 0
load_directory = ""

def init_worker(t,d,s,l):
    global worker_terminated
    global worker_done
    global worker_spacesaved
    global load_directory
    worker_terminated = t
    worker_done = d
    worker_spacesaved = s
    load_directory = l

def parse_size(data: int) -> str:
    result:str = ""
    if data < 0:
        neg = True
        data = -data
    else:
        neg = False
    if data < 2000:
        result = f"{data} bytes"
    elif data > 2000000000:
        result = f"{round(data/1000000000,2)} GB"
    elif data > 2000000:
        result = f"{round(data/1000000,2)} MB"
    elif data > 2000:
        result = f"{round(data/1000,2)} KB"
    if neg:
        result = "-"+result
    return result


def ticks_to_str(t:int) -> str:
    return str(datetime.timedelta(seconds=round(t/20)))

def handle_file(file:str,output_mode:int,threshold:int) -> None:
    global worker_terminated
    global worker_spacesaved
    global worker_done
    max_on_f = 0
    region = anvil.Region.from_file(load_directory + "/region/" + file)

    for i in range(0,32):
        for j in range(0,32):
            try:
                chunk = region.get_chunk(i,j)
                inhabited = chunk.data["InhabitedTime"]
                if output_mode == 3:
                    print(f"{file} {i} {j} -> {inhabited}")
                max_on_f += inhabited.value
                #print(f"{chunk.data["InhabitedTime"]} on {file} {i} {j}")
            except Exception as e:
                #print(e)
                pass
    with worker_done.get_lock():
        worker_done.value += 1
    if output_mode == 3:
        print(f"{file} sum {max_on_f}")
    if max_on_f < threshold:
        local_ss = 0

        local_ss += os.path.getsize(load_directory+"/region/"+file)
        os.remove(load_directory+"/region/"+file)
        try:
            local_ss += os.path.getsize(load_directory+"/entities/"+file)
            os.remove(load_directory+"/entities/"+file)
            local_ss += os.path.getsize(load_directory+"/poi/"+file)
            os.remove(load_directory+"/poi/"+file)
        except:
            pass
        with worker_spacesaved.get_lock():
            worker_spacesaved.value += local_ss
        with worker_terminated.get_lock():
            worker_terminated.value += 1

def run_progress_thread():
    global TERMINATED
    global DONE_SO_FAR
    global SPACE_SAVED
    global UPDATE_SLEEPTIME
    global OUTPUT_MODE
    
    while not COMPLETED:
        if OUTPUT_MODE >= 2 and DONE_SO_FAR.value > 0:
            tseconds = round(time.time() - TIME_STARTED)
            if tseconds > 0:
                processing_rate = DONE_SO_FAR.value / tseconds
                remaining_seconds = round((TOTAL_TO_COMPLETE - DONE_SO_FAR.value) / processing_rate)
            message = f"{datetime.timedelta(seconds=tseconds)} | {DONE_SO_FAR.value}/{TOTAL_TO_COMPLETE} [{round(DONE_SO_FAR.value/TOTAL_TO_COMPLETE*100)}% overall] - {TERMINATED.value} deleted [{round(TERMINATED.value/DONE_SO_FAR.value*100,2)}% disposal rate] - {parse_size(SPACE_SAVED.value)} saved | Time Remaining: {datetime.timedelta(seconds=remaining_seconds)}"
            spaces = os.get_terminal_size()[0] - 1 - len(message)
            if spaces > 0:
                message += " "*spaces
            print(message,end="\r")
        time.sleep(UPDATE_SLEEPTIME)

if __name__ == "__main__":

    parser = argparse.ArgumentParser("minecraft-world-trimmer")
    parser.add_argument("directory",action="store",type=str,help="The directory that contains the \"region\" and the \"entities\" folders")
    parser.add_argument("-t","--threshold",required=False,action="store",type=int,default=600,help="The number of seconds that a region must accumulate to spare it from deletion. Default is 600s or 10m.")
    parser.add_argument("-u","--update",required=False,action="store",type=float,default=1,help="The number of seconds between each update (decimals OK)")
    parser.add_argument("-c","--cores",required=False,action="store",type=int,default=None,help="The number of CPU cores to use for processing. The default is however many cores you have.")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-v","--verbose",required=False,action="store_true",help="Extra information about program operation")
    group.add_argument("-q","--quiet",action="store_true",required=False,help="Surpress non-error output from program")
    result = parser.parse_args(sys.argv[1:])

    #read args

    DIR = result.directory
    THRESHOLD:int = result.threshold * 20#To convert to ticks
    UPDATE_SLEEPTIME:float = result.update

    if not os.path.isdir(DIR):
        raise RuntimeError("Supplied directory must exist.")
    if not os.path.isdir(DIR+"/region"):
        raise RuntimeError("Supplied directory is not a Minecraft world.")
    if THRESHOLD < 0:
        raise RuntimeError("Unacceptable threshold value.")
    if UPDATE_SLEEPTIME <= 0:
        raise RuntimeError("Unacceptable progress update frequency")
    if result.cores is not None and result.cores <= 0:
        raise RuntimeError("Unacceptable core count")


    if result.verbose:
        OUTPUT_MODE = 3
    elif result.quiet:
        OUTPUT_MODE = 1
    else:
        OUTPUT_MODE = 2


    DONE_SO_FAR = multiprocessing.Value("I",0)
    TIME_STARTED = time.time()
    SPACE_SAVED = multiprocessing.Value("Q",0)
    TERMINATED = multiprocessing.Value("I",0)

    if OUTPUT_MODE >= 2:
        print("Scanning...")
    os.chdir(DIR)
    files = os.listdir(DIR+"/region")
    TOTAL_TO_COMPLETE = len(files)
    threading.Thread(target=run_progress_thread).start()
    with multiprocessing.Pool(initializer=init_worker,initargs=(TERMINATED,DONE_SO_FAR,SPACE_SAVED,DIR),processes=result.cores) as pool:  
        pool.starmap(handle_file,[[f,OUTPUT_MODE,THRESHOLD] for f in files])

    COMPLETED = True
    time.sleep(UPDATE_SLEEPTIME)#Wait for progress thread to 100% be finished
    if OUTPUT_MODE >= 2:
        print("\n\n\n")
        print(f"World trimming complete!\nSaved space: {parse_size(SPACE_SAVED.value)}\nDeleted files: {TERMINATED.value}")
    