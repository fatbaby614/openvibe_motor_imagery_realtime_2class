from pylsl import StreamInlet, resolve_stream
 
# 解析可用的EEG流
print("Looking for an EEG stream...")
streams = resolve_stream('type', 'EEG')
 
inlet = StreamInlet(streams[0])
 
while True:
    sample, timestamp = inlet.pull_sample()
    if sample:
        print(f"Received data: {sample} at time {timestamp}")