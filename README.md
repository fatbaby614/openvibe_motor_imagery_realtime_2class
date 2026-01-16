# 🧠 OpenBCI + OpenViBE + Python: 实时运动想象小球控制系统

本项目实现了一个基于**运动想象 (Motor Imagery, MI)** 的脑机接口闭环系统。通过 OpenBCI 采集脑电信号，利用 OpenViBE 进行实时 CSP+LDA 处理，并通过 LSL 协议将控制信号传输给 Python (PyGame)，实现受试者通过想象左手/右手运动来实时控制屏幕上小球的左右移动。

![System Architecture](https://img.shields.io/badge/Architecture-OpenBCI%20%3E%20OpenViBE%20%3E%20LSL%20%3E%20Python-blue)

## 📋 目录

- [硬件需求](#硬件需求)
- [软件环境](#软件环境)
- [电极布局与连接](#电极布局与连接)
- [快速开始](#快速开始)
- [项目文件说明](#项目文件说明)
- [🛠️ 踩坑指南与常见问题 (FAQ)](#%EF%B8%8F-踩坑指南与常见问题-faq)

![脑控小球左右移动](https://github.com/fatbaby614/openvibe_motor_imagery_realtime_2class/blob/main/%E8%BF%90%E5%8A%A8%E6%83%B3%E8%B1%A1-ov.gif?raw=true)





## 硬件需求

1.  **OpenBCI Cyton Board** (8通道) + USB Dongle  （淘宝DeepBCI + USB Dongle作为平替）
2.  **ultarcortex 电极帽** 
![硬件](https://github.com/fatbaby614/openvibe_motor_imagery_realtime_2class/blob/main/%E8%BF%90%E5%8A%A8%E6%83%B3%E8%B1%A1%E7%A1%AC%E4%BB%B6.png?raw=true)

## 软件环境

本项目涉及两个独立的 Python 环境，请严格区分配置：

### 1. OpenViBE 环境 (后端处理)

*   **OpenViBE**: v3.7.0 (64-bit)
*   **Internal Python**: Python 3.10.x (64-bit)
    *   依赖库: `numpy<2.0` (必须低于2.0), `pylsl`
    *   *注意：必须在 `openvibe.conf` 中正确配置 Python 3.10 的 DLL 路径。*

### 2. Python 游戏环境 (前端显示)

* **External Python**: Python 3.13 (或任意 3.x 版本)

* **依赖库**:

  ```bash
  pip install pygame pylsl numpy
  ```

numpy      1.26.4
pylsl      1.16.2

## 电极布局与连接

为了获得最佳的 CSP 空间滤波效果，建议使用以下 8 通道布局（覆盖感觉运动皮层）：

| OpenBCI 引脚 | 电极位置 | 作用            |
| :----------- | :------- | :-------------- |
| N1P          | **C3**   | 左侧运动区核心  |
| N2P          | **C4**   | 右侧运动区核心  |
| N3P          | **Cz**   | 中线参考        |
| N4P          | **FC1**  | 前邻居 (辅助C3) |
| N5P          | **FC1**  | 前邻居 (辅助C4) |
| N6P          | **CP1**  | 后邻居 (辅助C3) |
| N7P          | **CP2**  | 后邻居 (辅助C4) |
| N8P          | **Pz**   | 顶叶辅助        |

> **⚠️ 关键提示**: 参考电极 (SRB2) 接**左耳垂**，地线 (BIAS) 接**右耳垂**。也可以对调

## 快速开始

### 第一阶段：模型训练 (Calibration)

1.  启动 OpenBCI 采集并连接 OpenViBE Acquisition Server。
2.  运行 **`mi-csp-1-acquisition.xml`**: 跟随屏幕箭头提示（动觉想象），采集约 20-40 组数据。
3.  运行 **`mi-csp-2-train-CSP.xml`**: 生成 `csp-spatial-filter.cfg`。
4.  运行 **`mi-csp-3-classifier-trainer.xml`**: 生成 `classifier.cfg`。**确保准确率 > 60-70%**。

### 第二阶段：在线控制 (Online Free Run)

1. 打开 **`mi-csp-5-freerun-analysis.xml`** (本项目修改版)。

   *   该场景去除了箭头提示。
   *   使用 `Python 3 Scripting` 盒子通过 LSL 发送实时控制信号。

2. 点击 OpenViBE **Play**。

3. 运行 Python 游戏脚本：

   ```bash
   python move_ball.py
   ```

4. 开始想象左右手运动，控制小球移动。

## 项目文件说明

*   `openvibe_scenarios/`: 修改后的 OpenViBE 场景文件(OpenViBE 的示例文件通常安装在 C:\Program Files\OpenViBE\share\openvibe\scenarios\ ，受权限影响要拷贝到其它地方  )。
    *   包含 LSL 输出功能的 Python 脚本代码。
*   `python_game/move_ball.py`: PyGame 前端程序。



## 🛠️ 踩坑指南与常见问题 (FAQ)

在开发过程中遇到的问题及解决方案，供参考：

### Q1: OpenViBE 里找不到 `Python Scripting` 盒子？

* **原因**: OpenViBE 启动时没找到指定版本的 Python DLL。

* **解决**: 

  1. 重新安装 Python 3.10 (64-bit) 并勾选 "Add to PATH"。

  2. 修改 `openvibe.conf` (AppData/Roaming/openvibe/)，添加：

     ```ini
     Global_Python3_Path = "C:\\Path\\To\\Python310\\python310.dll"
     ```

  3. 检查控制台日志是否显示 `Python initialized successfully`。

### Q2: Python 3.13 运行 PyGame 报错 `ImportError: cannot import name 'resolve_stream'`

* **原因**: 新版 `pylsl` 在 Python 3.13 环境下 API 变动。

* **解决**: 使用 `resolve_streams` (复数) 获取列表，然后遍历查找名字。

  ```python
  streams = resolve_streams()
  for s in streams:
      if s.name() == "BCI_Control_Signal": ...
  ```

### Q3:运行出错：

[WARNING] At time 0.000 sec <Box algorithm::(0x00006ea1, 0x00004c67) aka Graz Motor Imagery BCI Stimulator> Lua error: .../motor-imagery-CSP/motor-imagery-bci-graz-stimulator.lua:83: bad argument #1 to 'random' (number has no integer representation)
[  INF  ] At time 0.000 sec <Box algorithm::(0x00006ea1, 0x00004c67) aka Graz Motor Imagery BCI Stimulator> Lua script terminated
[ ERROR ] {Error description} : {Box algorithm <Graz Motor Imagery BCI Stimulator> processInput function failed}, {Error type} : {ErrorType::Internal (code 2)}, {Error location} : {C:\Users\tprampar\workspace\ov-3.6\sdk\kernel\src\kernel\player\ovkCSimulatedBox.cpp::168}
[ ERROR ] {Error description} : {Process failed for box with id (0x00006ea1, 0x00004c67)}, {Error type} : {Kernel::ErrorType::Internal (code 2)}, {Error location} : {C:\Users\tprampar\workspace\ov-3.6\sdk\kernel\src\kernel\player\ovkCScheduler.cpp::562}

*   **原因**: share/openvibe/scenarios/bci-examples/motor-imagery-CSP/motor-imagery-bci-graz-stimulator.lua中math.random函数 只能接受整数

*   **解决**: 给参数加上 math.floor() 强制转为整数。

### Q4: OpenViBE 传给 Python 的数据是 `[val1, val2]` 两个数？

* **原因**: 分类器输出可能是两个类别的得分矩阵。

* **解决**: 在 OpenViBE 的 Python 脚本中计算差值：

  ```python
  # 伪代码
  control_val = chunk[0] - chunk[1] # 左手得分 - 右手得分
  outlet.push_sample([control_val])
  ```

### Q5: openvibe acquistition server选openbci,不勾选Daisy module,应该是8个通道才对，为什么打开change channel names却有11个通道呢？9、10、11通道怎么选呢？

* **原因**: 通道 9、10、11 是 OpenBCI 板载的“三轴加速度计” (Accelerometer X, Y, Z) 数据。对于你的 运动想象 (Motor Imagery) 实验，这三个通道的数据是完全不需要甚至有害的。把这三个通道喂给 CSP (Common Spatial Pattern) 算法，CSP 会试图去拟合这些巨大的方差，导致计算出来的空间滤波器完全跑偏，原本应该提取 C3/C4 特征的滤波器变成了提取“头皮抖动”的滤波器
* **解决**: Acquisition Client 盒子后面紧接着连一个 Channel Selector 盒子，双击 Channel Selector，设置 Select 条件为：
  1:8 (表示只保留前8个)或者直接写名字 C3;C4;Cz;FC3;FC4;CP3;CP4;Pz 



另外在可使用Gemini3作为实验指导，但需小心，Gemini3就让我使用 "Matrix to Signal" 转换，但本人怎么也找不到这个box

---

**Author**: [TanHuang]  
