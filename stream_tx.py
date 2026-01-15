from pylsl import StreamInfo, StreamOutlet
 
# 定义一个EEG数据流
info = StreamInfo(name='BCI_Control_Signal', type='EEG', channel_format='float32', channel_count=8,
                 nominal_srate=0, source_id='id_ov_123')
 
outlet = StreamOutlet(info)
i=0
# 模拟发送数据
# for i in range(100):
while(True):
    i = i+1
    data = [channel_data for channel_data in range(8)]  # 假设每通道的数据
    data[0] = i % 2
    # timestamps = [i / info.sampling_rate]  # 数据的时间戳
    timestamps = [i * 0.1]  # 假设采样率为10Hz
    outlet.push_sample(data, timestamps[0])