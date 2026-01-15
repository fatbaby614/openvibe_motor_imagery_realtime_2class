import numpy
from pylsl import StreamInfo, StreamOutlet

class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        self.outlet = None
        self.signal_name = "BCI_Control_Signal"
        self.signalHeader = None

    def initialize(self):
        print(f"[DEBUG] 初始化 LSL: {self.signal_name}")
        # 我们只需要发 1 个控制值 (差值)，所以 channel_count = 1
        info = StreamInfo(self.signal_name, 'Control', 1, 0, 'float32', 'id_debug')
        self.outlet = StreamOutlet(info)
        return

    def process(self):
        # 遍历输入端口的所有数据块
        for chunkIdx in range( len(self.input[0]) ):
            
            # 1. 处理头信息 (Header)
            if(type(self.input[0][chunkIdx]) == OVStreamedMatrixHeader):
                self.signalHeader = self.input[0].pop()
                print(f"[DEBUG] Header received. Dims: {self.signalHeader.dimensionSizes}")
            
            # 2. 处理数据体 (Buffer)
            elif(type(self.input[0][chunkIdx]) == OVStreamedMatrixBuffer):
                chunk = self.input[0].pop() # 这是一个列表，例如 [55.2, 55.7]
                
                # 确保我们收到了 2 个数 (防止报错)
                if len(chunk) >= 2:
                    val1 = chunk[0] # 第一个值
                    val2 = chunk[1] # 第二个值
                    
                    # === 核心逻辑：计算差值 ===
                    # 假设 val1 是左手，val2 是右手 (如果方向反了，就改成 val2 - val1)
                    control_signal = val2 - val1
                    
                    # 发送给 LSL (必须是列表形式)
                    self.outlet.push_sample([control_signal])
                    
                    # 打印调试信息 (只打印前几个小数位，看着清爽点)
                    print(f"[DEBUG] 发送: {control_signal:.3f} (源: {val1:.1f}, {val2:.1f})")
                
                elif len(chunk) == 1:
                    # 如果突变成 1 个数了，直接发
                    self.outlet.push_sample([chunk[0]])

            # 3. 处理结束符 (End)
            elif(type(self.input[0][chunkIdx]) == OVStreamedMatrixEnd):
                self.input[0].pop() # 移除即可
                
        return

    def uninitialize(self):
        self.outlet = None
        return

box = MyOVBox()