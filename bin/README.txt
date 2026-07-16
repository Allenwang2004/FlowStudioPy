<Mode 0> TADS will automatically play wav files to processing input then output audio to output device
------------------------------------------------------------------------------------------------------
FlowEngine.exe 0 <wav file path> <config file path> <input Device Index> <output Device Index> <sample rate> <frame size>

------------------------------------------------------------------------------------------------------
<Mode 1> TADS will process from input device then output audio to output device
------------------------------------------------------------------------------------------------------
FlowEngine.exe 1 <config file path> <input Device Index> <output Device Index> <sample rate> <frame size>

Note: if you don't know the index of input/output device, specify -1 to use default device from system

Here's the example to import default_config.flw to the FlowEngine.exe inside bin/ folder

FlowEngine.exe 1 default_config.flw -1 -1 44100 32 2 2


