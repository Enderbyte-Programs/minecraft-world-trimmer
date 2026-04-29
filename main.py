import anvil
import anvil.errors
import os
import datetime
import multiprocessing

DIR = "survival_nether/DIM-1/region"

def ticks_to_str(t:int) -> str:
    return str(datetime.timedelta(seconds=round(t/20)))

def handle_file(file:str) -> None:
    max_on_f = 0
    region = anvil.Region.from_file(DIR + "/" + file)

    for i in range(0,32):
        for j in range(0,32):
            try:
                chunk = region.get_chunk(i,j)
                inhabited = chunk.data["InhabitedTime"]
                max_on_f += inhabited.value
                #print(f"{chunk.data["InhabitedTime"]} on {file} {i} {j}")
            except Exception as e:
                #print(e)
                pass

    if max_on_f < 12000:
        print(f"Terminating {file} {ticks_to_str(max_on_f)}")
        os.remove(DIR+"/"+file)
        try:
            os.remove(DIR.replace("region","entities")+"/"+file)
            os.remove(DIR.replace("region","poi")+"/"+file)
        except:
            pass
    else:
        print(f"Keeping {file} {ticks_to_str(max_on_f)}")


with multiprocessing.Pool() as pool:
    files = os.listdir(DIR)
    pool.map(handle_file,files)

