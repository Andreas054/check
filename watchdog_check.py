import psutil

def process_status(process_name):
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        #print(process.info['cmdline'])
        if process_name in ' '.join(process.info['cmdline']):
            return True
    return False

process_name = "checkpi"
if process_status(process_name):
    print(f"The process {process_name} is running.")
else:
    print(f"The process {process_name} is not running.")
    import os
    os.system('reboot')
